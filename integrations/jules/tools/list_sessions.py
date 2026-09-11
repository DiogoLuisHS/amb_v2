#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""⚡ Jules Tool: list_sessions (Facade)"""

import sys, os, argparse

_cur = os.path.dirname(os.path.abspath(__file__))
while _cur and os.path.basename(_cur) != "amb_v2":
    _p = os.path.dirname(_cur)
    if _p == _cur:
        break
    _cur = _p
for _s in ["config", "integrations/jules"]:
    _p = os.path.normpath(os.path.join(_cur, *_s.split("/")))
    if os.path.exists(_p) and _p not in sys.path:
        sys.path.insert(0, _p)
from jules_client import JulesClient, Colors, log, log_error


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--limit", "-n", type=int, default=10)
    args = p.parse_args()
    try:
        c = JulesClient()
        sessions = c.list_sessions(page_size=args.limit)
        log("JULES", f"Sessões recentes ({len(sessions)}):", Colors.CYAN)
        for s in sessions:
            sid = s.get("name", "").split("/")[-1] or s.get("id")
            print(f"  • [{sid}] {s.get('title') or 'Sem título'} ({s.get('state')})")
    except Exception as e:
        log_error("JULES", str(e))
        sys.exit(1)


if __name__ == "__main__":
    main()
