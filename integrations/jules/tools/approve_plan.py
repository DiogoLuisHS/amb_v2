#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""⚡ Jules Tool: approve_plan (Facade)"""
import sys, os, argparse
_cur = os.path.dirname(os.path.abspath(__file__))
while _cur and os.path.basename(_cur) != "amb_v2":
    _p = os.path.dirname(_cur)
    if _p == _cur: break
    _cur = _p
for _s in ["config", "integrations/jules"]:
    _p = os.path.normpath(os.path.join(_cur, *_s.split("/")))
    if os.path.exists(_p) and _p not in sys.path: sys.path.insert(0, _p)
from jules_client import JulesClient, Colors, log, log_error

def approve_plan(session_id: str, client: JulesClient = None):
    c = client or JulesClient()
    return c.approve_plan(session_id)

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--session-id", "-s", required=True)
    args = p.parse_args()
    try:
        approve_plan(args.session_id)
        log("JULES", f"✅ Plano da sessão {args.session_id} aprovado com sucesso!", Colors.GREEN)
    except Exception as e:
        log_error("JULES", str(e)); sys.exit(1)

if __name__ == "__main__":
    main()
