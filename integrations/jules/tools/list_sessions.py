#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""⚡ Jules Tool: list_sessions (Facade)"""
import sys
import os
import argparse

from config.bootstrap import ensure_amb_env
ensure_amb_env()

from config import Colors, log, log_error
from integrations.jules.jules_client import JulesClient

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
        log_error("JULES", str(e)); sys.exit(1)

if __name__ == "__main__":
    main()
