#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🚀 AMB_V2 - Render SDK: Listagem de Serviços e IDs (SRP)
Localização: amb_v2/integrations/render/tools/list_services.py
Responsabilidade Única: Consultar a Render API e listar todos os serviços da conta com seus IDs.
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

from config import Colors, log, log_error
from render_client import RenderClient


def main():
    parser = argparse.ArgumentParser(description="Lista todos os serviços configurados na sua conta Render.")
    parser.add_argument("--json", action="store_true", help="Retorna saída JSON puro.")

    args = parser.parse_args()

    try:
        client = RenderClient()
        services = client.list_services()

        if args.json:
            print(json.dumps(services, indent=2))
        else:
            log("RENDER-SERVICES", f"Serviços encontrados ({len(services)}):", Colors.CYAN)
            for item in services:
                srv = item.get("service", item)
                sid = srv.get("id")
                name = srv.get("name")
                stype = srv.get("type")
                url = srv.get("serviceDetails", {}).get("url", "")
                print(f"  • ID: {Colors.BOLD}{sid}{Colors.RESET} | Nome: {Colors.GREEN}{name}{Colors.RESET} ({stype})")
                if url:
                    print(f"    URL: {url}")
    except Exception as e:
        log_error("RENDER-SERVICES", str(e))
        sys.exit(1)


if __name__ == "__main__":
    main()
