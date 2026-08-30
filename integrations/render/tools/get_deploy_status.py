#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🚀 AMB_V2 - Render SDK: Status do Último Deploy (SRP)
Localização: amb_v2/integrations/render/tools/get_deploy_status.py
Responsabilidade Única: Consultar e detalhar o estado da última compilação/deploy de um serviço no Render.
"""

import os
import sys
import json
import argparse

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
from render_client import RenderClient


def main():
    parser = argparse.ArgumentParser(description="Consulta o status do deploy mais recente de um serviço no Render.")
    parser.add_argument("--service-id", "-s", help="ID do serviço no Render (padrão: RENDER_SERVICE_ID do .env).")
    parser.add_argument("--json", action="store_true", help="Retorna saída JSON puro.")

    args = parser.parse_args()

    try:
        client = RenderClient()
        sid = args.service_id or require_env("RENDER_SERVICE_ID")

        deploys = client.list_deploys(service_id=sid, limit=1)
        if not deploys:
            raise ApiExecutionError(f"Nenhum histórico de deploy encontrado para o serviço {sid}.")

        dep_obj = deploys[0]
        dep = dep_obj.get("deploy", dep_obj)

        if args.json:
            print(json.dumps(dep, indent=2))
        else:
            status = dep.get("status", "UNKNOWN")
            status_color = Colors.GREEN if status == "live" else (Colors.RED if "fail" in status.lower() else Colors.YELLOW)
            
            log("RENDER-DEPLOY", f"Deploy mais recente do serviço {sid}:", Colors.CYAN)
            print(f"  • Deploy ID:   {dep.get('id')}")
            print(f"  • Status:      {status_color}{status}{Colors.RESET}")
            print(f"  • Commit:      {dep.get('commit', {}).get('message', 'N/A')}")
            print(f"  • Criado em:   {dep.get('createdAt')}")
            print(f"  • Finalizado:  {dep.get('finishedAt') or 'Em andamento'}")
    except Exception as e:
        log_error("RENDER-DEPLOY", str(e))
        sys.exit(1)


if __name__ == "__main__":
    main()
