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

# Bootstrap dinâmico de caminhos amb_v2
_cur = os.path.dirname(os.path.abspath(__file__))
while _cur and os.path.basename(_cur) != "amb_v2":
    _p = os.path.dirname(_cur)
    if _p == _cur:
        break
    _cur = _p
_AMB = _cur
for _sub in [
    "config", "agents", "pipeline", "dashboard", "dashboard/watchers",
    "integrations/jules", "integrations/jules/tools",
    "integrations/stitch", "integrations/stitch/tools",
    "integrations/antigravity", "integrations/antigravity/tools",
    "integrations/render", "integrations/render/tools",
]:
    _p = os.path.normpath(os.path.join(_AMB, *_sub.split("/")))
    if os.path.exists(_p) and _p not in sys.path:
        sys.path.insert(0, _p)

from config import Colors, log, log_error, require_env, ApiExecutionError


class JulesClient:
    """Client REST para Google Jules API v1alpha."""

    BASE_URL = "https://jules.googleapis.com/v1alpha"

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or require_env("JULES_API_KEY")

    def _request(
        self,
        method: str,
        path: str,
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Executa requisição HTTP autenticada via header X-Goog-Api-Key."""
        url = f"{self.BASE_URL}/{path.lstrip('/')}"
        if params:
            query = urllib.parse.urlencode({k: v for k, v in params.items() if v is not None})
            url = f"{url}?{query}"

        headers = {
            "X-Goog-Api-Key": self.api_key,
            "Content-Type": "application/json",
            "User-Agent": "AMB-CLI-v2/1.0",
        }

        body_bytes = json.dumps(data).encode("utf-8") if data is not None else None
        req = urllib.request.Request(url, data=body_bytes, headers=headers, method=method.upper())

        try:
            with urllib.request.urlopen(req, timeout=45) as resp:
                resp_text = resp.read().decode("utf-8")
                return json.loads(resp_text) if resp_text else {}
        except urllib.error.HTTPError as e:
            error_body = e.read().decode("utf-8")
            msg = f"HTTP {e.code}: {e.reason}"
            try:
                err_json = json.loads(error_body)
                if "error" in err_json:
                    msg = f"{msg} - {err_json['error'].get('message', error_body)}"
            except Exception:
                msg = f"{msg} - {error_body}"

            hint = "Verifique se a JULES_API_KEY é válida e tem permissões na API do Google Jules."
            if e.code == 404:
                hint = "Recurso não encontrado. Verifique o ID da sessão ou se o repositório está conectado no Jules."
            elif e.code == 403:
                hint = "Acesso negado. Confirme se a chave de API está ativada no Google Cloud / Jules."
            raise ApiExecutionError(f"Erro na API Jules: {msg}", hint=hint)
        except Exception as e:
            raise ApiExecutionError(f"Falha de conexão com Jules API: {e}", hint="Verifique sua conexão com a internet.")

    # 1. Sources
    def list_sources(self, page_size: int = 50) -> List[Dict[str, Any]]:
        res = self._request("GET", "sources", params={"pageSize": page_size})
        return res.get("sources", [])

    # 2. Sessions
    def create_session(self, prompt: str, source_name: str, title: Optional[str] = None, base_branch: str = "main") -> Dict[str, Any]:
        payload = {
            "prompt": prompt,
            "sourceContext": {
                "source": source_name,
                "githubRepoContext": {
                    "startingBranch": base_branch
                }
            }
        }
        if title:
            payload["title"] = title
        return self._request("POST", "sessions", data=payload)

    def get_session(self, session_id: str) -> Dict[str, Any]:
        path = session_id if session_id.startswith("sessions/") else f"sessions/{session_id}"
        return self._request("GET", path)

    def list_sessions(self, page_size: int = 50, repo_filter: Optional[str] = None) -> List[Dict[str, Any]]:
        res = self._request("GET", "sessions", params={"pageSize": page_size})
        sessions = res.get("sessions", [])
        if repo_filter:
            target = repo_filter.lower().strip()
            filtered = []
            for s in sessions:
                s_src = s.get("sourceContext", {}).get("source", "").lower()
                if s_src:
                    if target in s_src or s_src.endswith(target):
                        filtered.append(s)
                else:
                    filtered.append(s)
            return filtered
        return sessions

    def send_message(self, session_id: str, message: str) -> Dict[str, Any]:
        clean_id = session_id.split("/")[-1]
        path = f"sessions/{clean_id}:sendMessage"
        return self._request("POST", path, data={"prompt": message})

    def approve_plan(self, session_id: str) -> Dict[str, Any]:
        clean_id = session_id.split("/")[-1]
        path = f"sessions/{clean_id}:approvePlan"
        return self._request("POST", path, data={})

    def delete_session(self, session_id: str) -> Dict[str, Any]:
        clean_id = session_id.split("/")[-1]
        path = f"sessions/{clean_id}"
        return self._request("DELETE", path)

    # 3. Activities
    def list_activities(self, session_id: str, page_size: int = 50) -> Dict[str, Any]:
        clean_id = session_id.split("/")[-1]
        path = f"sessions/{clean_id}/activities"
        return self._request("GET", path, params={"pageSize": page_size})


if __name__ == "__main__":
    try:
        c = JulesClient()
        sources = c.list_sources()
        print(f"{Colors.GREEN}✅ Conexão Jules REST API bem-sucedida! Repositórios encontrados: {len(sources)}{Colors.RESET}")
    except Exception as e:
        log_error("JULES-CLIENT", str(e))
