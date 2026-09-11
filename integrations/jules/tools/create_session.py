#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""⚡ Jules Tool: create_session (Facade)"""

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


def create_session(
    prompt: str, title: str = None, source_name: str = None, client: JulesClient = None
):
    c = client or JulesClient()
    return c.create_session(prompt=prompt, title=title, source_name=source_name)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--prompt", "-p", required=True)
    p.add_argument("--title", "-t")
    args = p.parse_args()
    try:
        res = create_session(prompt=args.prompt, title=args.title)
        sid = res.get("name", "").split("/")[-1] or res.get("id")
        log("JULES", f"Sessão criada: {sid}", Colors.GREEN)
    except Exception as e:
        log_error("JULES", str(e))
        sys.exit(1)


if __name__ == "__main__":
    main()
