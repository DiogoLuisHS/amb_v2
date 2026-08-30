#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""🚀 Render Tool: list_services (Facade)"""
import sys, os
_cur = os.path.dirname(os.path.abspath(__file__))
while _cur and os.path.basename(_cur) != "amb_v2":
    _p = os.path.dirname(_cur)
    if _p == _cur: break
    _cur = _p
for _s in ["config", "integrations/render"]:
    _p = os.path.normpath(os.path.join(_cur, *_s.split("/")))
    if os.path.exists(_p) and _p not in sys.path: sys.path.insert(0, _p)
from render_client import RenderClient, Colors, log, log_error

def main():
    try:
        client = RenderClient()
        services = client.list_services()
        log("RENDER", f"Serviços encontrados na conta ({len(services)}):", Colors.CYAN)
        for item in services:
            srv = item.get("service", item)
            print(f"  • ID: {Colors.BOLD}{srv.get('id')}{Colors.RESET} | {Colors.GREEN}{srv.get('name')}{Colors.RESET} ({srv.get('type')})")
    except Exception as e:
        log_error("RENDER", str(e)); sys.exit(1)

if __name__ == "__main__":
    main()
