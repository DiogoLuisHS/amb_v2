#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""⚡ Jules Tool: list_sources (Facade)"""
import sys, os
_cur = os.path.dirname(os.path.abspath(__file__))
while _cur and os.path.basename(_cur) != "amb_v2":
    _p = os.path.dirname(_cur)
    if _p == _cur: break
    _cur = _p
for _s in ["config", "integrations/jules"]:
    _p = os.path.normpath(os.path.join(_cur, *_s.split("/")))
    if os.path.exists(_p) and _p not in sys.path: sys.path.insert(0, _p)
from jules_client import JulesClient, Colors, log, log_error

def main():
    try:
        c = JulesClient()
        sources = c.list_sources()
        log("JULES", f"Fontes/Repositórios conectados ({len(sources)}):", Colors.CYAN)
        for s in sources:
            print(f"  • {s.get('name')}")
    except Exception as e:
        log_error("JULES", str(e)); sys.exit(1)

if __name__ == "__main__":
    main()
