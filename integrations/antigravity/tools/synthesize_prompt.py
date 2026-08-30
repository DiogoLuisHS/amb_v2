#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""🧠 Antigravity Tool: synthesize_prompt (Facade)"""
import sys, os, argparse
_cur = os.path.dirname(os.path.abspath(__file__))
while _cur and os.path.basename(_cur) != "amb_v2":
    _p = os.path.dirname(_cur)
    if _p == _cur: break
    _cur = _p
for _s in ["config", "integrations/antigravity"]:
    _p = os.path.normpath(os.path.join(_cur, *_s.split("/")))
    if os.path.exists(_p) and _p not in sys.path: sys.path.insert(0, _p)
from antigravity_client import synthesize_prompt, Colors, log, log_error

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--idea", "-i", required=True)
    p.add_argument("--role", "-r", default="general")
    args = p.parse_args()
    try:
        res = synthesize_prompt(raw_idea=args.idea, role=args.role)
        print(res)
    except Exception as e:
        log_error("ANTIGRAVITY", str(e)); sys.exit(1)

if __name__ == "__main__":
    main()
