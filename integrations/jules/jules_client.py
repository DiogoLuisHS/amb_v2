#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
⚡ AMB_V2 - Jules REST API v1alpha Client (SRP)
Localização: amb_v2/integrations/jules/jules_client.py
Responsabilidade Única: Executar chamadas HTTP autenticadas para o endpoint oficial do Google Jules.
"""

import os
import sys
import json
import urllib.request
import urllib.error
from typing import Dict, Any, Optional, List

from config.bootstrap import ensure_amb_env
ensure_amb_env()

from config import Colors, log, log_error, require_env, ApiExecutionError
from integrations.common.base_google_client import BaseGoogleClient


class JulesClient(BaseGoogleClient):
    """Client REST para Google Jules API v1alpha com resiliência e retry exponencial."""

    BASE_URL = "https://jules.googleapis.com/v1alpha"

    def __init__(self, api_key: Optional[str] = None):
        resolved_key = api_key or require_env("JULES_API_KEY")
        super().__init__(
            base_url=self.BASE_URL,
            api_key=resolved_key,
            service_name="JULES",
            timeout=45,
            max_retries=3,
        )

    def _request(
        self,
        method: str,
        path: str,
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Executa requisição HTTP autenticada via BaseGoogleClient com retry exponencial e jitter."""
        return self.execute_request(method=method, path_or_url=path, params=params, data=data)

    # 1. Normalização & Helpers
    @staticmethod
    def normalize_session_id(session_id: str) -> str:
        """
        Normaliza strings de ID de sessão, aceitando:
        - ID numérico/alfanumérico puro: '17502412430766789460'
        - Rota REST: 'sessions/17502412430766789460'
        - URL web: 'https://jules.google.com/session/17502412430766789460'
        - URLs com parâmetros de query ou barras no final.
        """
        if not session_id:
            return ""
        raw = str(session_id).strip().rstrip("/")
        if "jules.google.com/session/" in raw:
            raw = raw.split("jules.google.com/session/")[-1].split("/")[0].split("?")[0]
        elif "sessions/" in raw:
            raw = raw.split("sessions/")[-1].split("/")[0].split("?")[0]
        return raw.strip()

    # 2. Sources
    def list_sources(self, page_size: int = 50) -> List[Dict[str, Any]]:
        res = self._request("GET", "sources", params={"pageSize": page_size})
        return res.get("sources", [])

    def get_source(self, source_name: str) -> Dict[str, Any]:
        """Retorna detalhes de uma fonte/repositório conectado no Jules."""
        clean = source_name.strip().lstrip("/")
        path = clean if clean.startswith("sources/") else f"sources/{clean}"
        return self._request("GET", path)

    # 3. Sessions
    def create_session(
        self,
        prompt: str,
        source_name: Optional[str] = None,
        title: Optional[str] = None,
        base_branch: Optional[str] = None
    ) -> Dict[str, Any]:
        if os.path.isfile(prompt):
            try:
                with open(prompt, "r", encoding="utf-8") as f:
                    prompt = f.read()
            except Exception:
                pass
        from config import get_repo_name
        resolved_source = source_name or f"sources/github/{get_repo_name()}"

        # Se base_branch não for especificada, auto-detecta branch ativa do repositório local
        if not base_branch:
            try:
                from integrations.git.git_service import GitService
                base_branch = GitService().get_current_branch()
            except Exception:
                base_branch = None
        base_branch = base_branch or "main"

        payload = {
            "prompt": prompt,
            "sourceContext": {
                "source": resolved_source,
                "githubRepoContext": {
                    "startingBranch": base_branch
                }
            }
        }
        if title:
            payload["title"] = title
        return self._request("POST", "sessions", data=payload)

    def get_session(self, session_id: str) -> Dict[str, Any]:
        clean_id = self.normalize_session_id(session_id)
        return self._request("GET", f"sessions/{clean_id}")

    @staticmethod
    def extract_pull_request(
        session_dict: Dict[str, Any],
        activities: Optional[List[Dict[str, Any]]] = None
    ) -> Optional[Dict[str, Any]]:
        """Extrai metadados do Pull Request (url, number) dos outputs da sessão ou das atividades com fallback via regex."""
        # 1. Inspeciona outputs estruturados da sessão
        outputs = session_dict.get("outputs", [])
        if isinstance(outputs, list):
            for item in outputs:
                if isinstance(item, dict) and "pullRequest" in item:
                    pr_info = item["pullRequest"]
                    if isinstance(pr_info, dict) and pr_info.get("url"):
                        return pr_info
        elif isinstance(outputs, dict) and "pullRequest" in outputs:
            pr_info = outputs["pullRequest"]
            if isinstance(pr_info, dict) and pr_info.get("url"):
                return pr_info

        # 2. Inspeciona activities fornecidas via regex resiliente
        if activities and isinstance(activities, list):
            import re
            for act in activities:
                txt = str(act)
                m = re.search(r"(https://github\.com/[^/]+/[^/]+/pull/(\d+))", txt)
                if m:
                    return {
                        "url": m.group(1),
                        "number": int(m.group(2))
                    }

        return None

    def list_sessions(
        self,
        page_size: int = 50,
        repo_filter: Optional[str] = None,
        state_filter: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        res = self._request("GET", "sessions", params={"pageSize": page_size})
        sessions = res.get("sessions", [])
        filtered = []
        target = repo_filter.lower().strip() if repo_filter else None
        target_state = state_filter.upper().strip() if state_filter else None

        for s in sessions:
            if target:
                s_src = s.get("sourceContext", {}).get("source", "").lower()
                if not s_src or (target not in s_src and not s_src.endswith(target)):
                    continue
            if target_state:
                if (s.get("state") or "").upper() != target_state:
                    continue
            filtered.append(s)

        return filtered

    def send_message(self, session_id: str, message: str) -> Dict[str, Any]:
        if os.path.isfile(message):
            try:
                with open(message, "r", encoding="utf-8") as f:
                    message = f.read()
            except Exception:
                pass
        clean_id = self.normalize_session_id(session_id)
        path = f"sessions/{clean_id}:sendMessage"
        return self._request("POST", path, data={"prompt": message})

    def approve_plan(self, session_id: str) -> Dict[str, Any]:
        clean_id = self.normalize_session_id(session_id)
        path = f"sessions/{clean_id}:approvePlan"
        return self._request("POST", path, data={})

    def delete_session(self, session_id: str) -> Dict[str, Any]:
        clean_id = self.normalize_session_id(session_id)
        path = f"sessions/{clean_id}"
        return self._request("DELETE", path)

    def get_status(self, repo_filter: Optional[str] = None) -> Dict[str, Any]:
        """Retorna diagnóstico completo de conectividade, chave, fontes e sessões ativas."""
        from config import get_repo_name, get_env
        target_repo = repo_filter or get_repo_name()
        key = get_env("JULES_API_KEY")

        status: Dict[str, Any] = {
            "api_key_configured": bool(key),
            "api_reachable": False,
            "sources_count": 0,
            "active_repo": target_repo,
            "repo_connected": False,
            "sessions_total": 0,
            "sessions_awaiting_feedback": 0,
            "sessions_in_progress": 0,
            "sessions_completed": 0,
            "sessions_failed": 0,
            "error": None,
        }

        if not key:
            status["error"] = "JULES_API_KEY não configurada no ambiente."
            return status

        try:
            sources = self.list_sources()
            status["api_reachable"] = True
            status["sources_count"] = len(sources)
            if target_repo:
                target_norm = target_repo.lower().strip()
                status["repo_connected"] = any(
                    target_norm in (s.get("name") or "").lower() for s in sources
                )

            sessions = self.list_sessions(page_size=50, repo_filter=target_repo)
            status["sessions_total"] = len(sessions)
            for s in sessions:
                st = (s.get("state") or "UNKNOWN").upper()
                if "AWAITING" in st:
                    status["sessions_awaiting_feedback"] += 1
                elif "IN_PROGRESS" in st or "RUNNING" in st or "STARTING" in st:
                    status["sessions_in_progress"] += 1
                elif "COMPLETED" in st or "SUCCEEDED" in st:
                    status["sessions_completed"] += 1
                elif "FAIL" in st or "CANCEL" in st:
                    status["sessions_failed"] += 1
        except Exception as e:
            status["error"] = str(e)

        return status

    # 4. Activities
    def list_activities(self, session_id: str, page_size: int = 50, fetch_all: bool = True) -> Dict[str, Any]:
        """Lista atividades da sessão. Se fetch_all=True, percorre todas as páginas para capturar as atividades mais recentes."""
        clean_id = self.normalize_session_id(session_id)
        path = f"sessions/{clean_id}/activities"
        
        if not fetch_all:
            return self._request("GET", path, params={"pageSize": page_size})

        all_acts = []
        page_token = None
        while True:
            params = {"pageSize": 100}
            if page_token:
                params["pageToken"] = page_token
            res = self._request("GET", path, params=params)
            acts = res.get("activities", []) if isinstance(res, dict) else (res if isinstance(res, list) else [])
            all_acts.extend(acts)
            if not isinstance(res, dict) or not res.get("nextPageToken"):
                break
            page_token = res.get("nextPageToken")

        return {"activities": all_acts}


    def list_activities_for_sessions(self, session_ids: List[str], page_size: int = 50, max_workers: int = 10) -> Dict[str, Dict[str, Any]]:
        import concurrent.futures

        results = {}

        def fetch_for_session(sid):
            try:
                act_res = self.list_activities(session_id=sid, page_size=page_size)
                return sid, (act_res if isinstance(act_res, list) else act_res.get("activities", []))
            except Exception as e:
                from config import log_error
                log_error("JULES-CLIENT", f"Falha ao buscar atividades da sessão {sid}: {e}")
                return sid, []

        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_sid = {executor.submit(fetch_for_session, sid): sid for sid in session_ids}
            for future in concurrent.futures.as_completed(future_to_sid):
                sid = future_to_sid[future]
                try:
                    sid, acts = future.result()
                    results[sid] = acts
                except Exception as e:
                    from config import log_error
                    log_error("JULES-CLIENT", f"Erro fatal ao processar atividades da sessão {sid}: {e}")
                    results[sid] = []

        return results


if __name__ == "__main__":
    try:
        c = JulesClient()
        sources = c.list_sources()
        print(f"{Colors.GREEN}✅ Conexão Jules REST API bem-sucedida! Repositórios encontrados: {len(sources)}{Colors.RESET}")
    except Exception as e:
        log_error("JULES-CLIENT", str(e))
