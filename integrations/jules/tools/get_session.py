#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""⚡ Jules Tool: get_session (Facade)"""

import sys, os, argparse, json

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


def get_session_details(
    session_id: str, output_json: bool = False, client: JulesClient = None
):
    c = client or JulesClient()
    data = c.get_session(session_id)
    if output_json:
        print(json.dumps(data, indent=2))
    else:
        sid = data.get("name", "").split("/")[-1] or data.get("id")
        state = data.get("state", "UNKNOWN")
        log("JULES", f"Sessão {sid} ({state})", Colors.CYAN)
        print(f"  • Título: {data.get('title') or 'Sem título'}")
        print(f"  • Web:    https://jules.google.com/session/{sid}")
    return data


def main():
    p = argparse.ArgumentParser()
    p.add_argument("session_id")
    p.add_argument("--json", action="store_true")
    args = p.parse_args()
    try:
        get_session_details(args.session_id, output_json=args.json)
    except Exception as e:
        log_error("JULES", str(e))
        sys.exit(1)


if __name__ == "__main__":
    main()
