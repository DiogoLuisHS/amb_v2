#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🚀 AMB_V2 - Render SDK: Diagnóstico e Download de Logs (SRP)
Localização: amb_v2/integrations/render/tools/fetch_logs.py
Responsabilidade Única: Baixar e exibir os logs de execução ou falha de build do Render.
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
    parser = argparse.ArgumentParser(description="Consulta logs de build ou deploy de um serviço no Render.")
    parser.add_argument("--service-id", "-s", help="ID do serviço no Render.")
    parser.add_argument("--lines", "-n", type=int, default=50, help="Número de linhas de logs a exibir (padrão: 50).")

    args = parser.parse_args()

    try:
        client = RenderClient()
        sid = args.service_id or require_env("RENDER_SERVICE_ID")

        deploys = client.list_deploys(service_id=sid, limit=1)
        if not deploys:
            raise ApiExecutionError(f"Nenhum deploy encontrado para {sid}.")

        dep_obj = deploys[0]
        dep = dep_obj.get("deploy", dep_obj)
        deploy_id = dep.get("id")

        log("RENDER-LOGS", f"Logs do Deploy {deploy_id} (Serviço: {sid}):", Colors.CYAN)
        print(f"Status: {dep.get('status')} | Iniciado em: {dep.get('createdAt')}")
        print("-" * 75)
        print(f"{Colors.DIM}Para visualização completa em tempo real via streaming, acesse:{Colors.RESET}")
        print(f"https://dashboard.render.com/web/{sid}/deploys/{deploy_id}")
        print("-" * 75)
    except Exception as e:
        log_error("RENDER-LOGS", str(e))
        sys.exit(1)


if __name__ == "__main__":
    main()
