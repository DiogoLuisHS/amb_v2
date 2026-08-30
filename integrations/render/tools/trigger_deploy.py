#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🚀 AMB_V2 - Render SDK: Disparo de Novo Deploy Manual (SRP)
Localização: amb_v2/integrations/render/tools/trigger_deploy.py
Responsabilidade Única: Enviar requisição POST para iniciar nova compilação e deploy no Render.
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

from config import Colors, log, log_error, require_env
from render_client import RenderClient


def main():
    parser = argparse.ArgumentParser(description="Dispara um novo deploy manual para um serviço no Render.")
    parser.add_argument("--service-id", "-s", help="ID do serviço no Render.")
    parser.add_argument("--clear-cache", action="store_true", help="Limpa o cache de build antes de compilar.")
    parser.add_argument("--json", action="store_true", help="Retorna saída JSON puro.")

    args = parser.parse_args()

    try:
        client = RenderClient()
        sid = args.service_id or require_env("RENDER_SERVICE_ID")

        log("RENDER-TRIGGER", f"Disparando deploy para o serviço {sid} (Clear Cache: {args.clear_cache})...", Colors.CYAN)
        res = client.trigger_deploy(service_id=sid, clear_cache=args.clear_cache)

        if args.json:
            print(json.dumps(res, indent=2))
        else:
            dep_id = res.get("id") or res.get("deploy", {}).get("id")
            log("RENDER-TRIGGER", "✅ Deploy disparado com sucesso!", Colors.GREEN)
            print(f"  • Deploy ID: {Colors.BOLD}{dep_id}{Colors.RESET}")
            print(f"  • Status:    {res.get('status', 'created')}")
    except Exception as e:
        log_error("RENDER-TRIGGER", str(e))
        sys.exit(1)


if __name__ == "__main__":
    main()
