#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🚀 AMB_V2 - Render Cloud API v1 Client (SRP)
Localização: amb_v2/integrations/render/client/render_client.py
Responsabilidade Única: Executar chamadas HTTP autenticadas para a API REST da Render Cloud.
"""

import os
import sys
import json
import urllib.request
import urllib.parse
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
    "config",
    "agents",
    "pipeline",
    "dashboard",
    "dashboard/watchers",
    "integrations/jules",
    "integrations/jules/tools",
    "integrations/stitch",
    "integrations/stitch/tools",
    "integrations/antigravity",
    "integrations/antigravity/tools",
    "integrations/render",
    "integrations/render/tools",
]:
    _p = os.path.normpath(os.path.join(_AMB, *_sub.split("/")))
    if os.path.exists(_p) and _p not in sys.path:
        sys.path.insert(0, _p)

from config import Colors, log, log_error, require_env, ApiExecutionError


class RenderClient:
    """Client REST para Render Cloud API v1."""

    BASE_URL = "https://api.render.com/v1"

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or require_env("RENDER_API_KEY")

    def _request(
        self,
        method: str,
        path: str,
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
    ) -> Any:
        """Executa chamada HTTP autenticada via Bearer Token."""
        url = f"{self.BASE_URL}/{path.lstrip('/')}"
        if params:
            query = urllib.parse.urlencode(
                {k: v for k, v in params.items() if v is not None}
            )
            url = f"{url}?{query}"

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Accept": "application/json",
            "Content-Type": "application/json",
            "User-Agent": "AMB-CLI-v2/1.0",
        }

        body_bytes = json.dumps(data).encode("utf-8") if data is not None else None
        req = urllib.request.Request(
            url, data=body_bytes, headers=headers, method=method.upper()
        )

        try:
            with urllib.request.urlopen(req, timeout=45) as resp:
                resp_text = resp.read().decode("utf-8")
                return json.loads(resp_text) if resp_text else {}
        except urllib.error.HTTPError as e:
            error_body = e.read().decode("utf-8")
            msg = f"HTTP {e.code}: {e.reason}"
            try:
                err_json = json.loads(error_body)
                if "message" in err_json:
                    msg = f"{msg} - {err_json['message']}"
            except Exception:
                msg = f"{msg} - {error_body}"

            hint = "Verifique se a RENDER_API_KEY no .env é válida."
            if e.code == 401:
                hint = "Token inválido. Gere uma nova API Key no painel do Render em https://dashboard.render.com/u/settings#api-keys"
            elif e.code == 404:
                hint = "Serviço ou deploy não encontrado no Render. Verifique o ID do serviço."
            raise ApiExecutionError(f"Erro na API Render: {msg}", hint=hint)
        except Exception as e:
            raise ApiExecutionError(f"Falha de conexão com Render API: {e}")

    def list_services(self, limit: int = 50) -> List[Dict[str, Any]]:
        res = self._request("GET", "services", params={"limit": limit})
        if isinstance(res, list):
            return res
        return res.get("services", [])

    def get_service(self, service_id: str) -> Dict[str, Any]:
        return self._request("GET", f"services/{service_id}")

    def list_deploys(self, service_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        res = self._request(
            "GET", f"services/{service_id}/deploys", params={"limit": limit}
        )
        if isinstance(res, list):
            return res
        return res.get("deploys", [])

    def get_deploy(self, service_id: str, deploy_id: str) -> Dict[str, Any]:
        return self._request("GET", f"services/{service_id}/deploys/{deploy_id}")

    def trigger_deploy(
        self, service_id: str, clear_cache: bool = False
    ) -> Dict[str, Any]:
        data = {"clearCache": "clear" if clear_cache else "do_not_clear"}
        return self._request("POST", f"services/{service_id}/deploys", data=data)


if __name__ == "__main__":
    try:
        c = RenderClient()
        services = c.list_services()
        print(
            f"{Colors.GREEN}✅ Conexão Render API bem-sucedida! Serviços encontrados: {len(services)}{Colors.RESET}"
        )
    except Exception as e:
        log_error("RENDER-CLIENT", str(e))
