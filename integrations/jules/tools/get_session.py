#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""⚡ Jules Tool: get_session (Facade)"""
import sys
import os
import argparse
import json

from config.bootstrap import ensure_amb_env
ensure_amb_env()

from config import Colors, log, log_error
from integrations.jules.jules_client import JulesClient

def get_session_details(session_id: str, output_json: bool = False, client: JulesClient = None):
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
        log_error("JULES", str(e)); sys.exit(1)

if __name__ == "__main__":
    main()
