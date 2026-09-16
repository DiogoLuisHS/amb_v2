#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""⚡ Jules Tool: monitor_activities (Facade)"""
import sys
import os
import argparse
import time

from config.bootstrap import ensure_amb_env
ensure_amb_env()

from config import Colors, log, log_error
from integrations.jules.jules_client import JulesClient

def monitor_session(session_id: str, poll_interval: int = 5, client: JulesClient = None):
    c = client or JulesClient()
    seen_ids = set()
    log("JULES-WATCH", f"Acompanhando sessão {session_id}...", Colors.CYAN)
    while True:
        try:
            acts = c.list_activities(session_id=session_id, page_size=15)
            activities = acts if isinstance(acts, list) else acts.get("activities", [])
            for a in reversed(activities):
                aid = a.get("id") or a.get("name")
                if aid and aid not in seen_ids:
                    seen_ids.add(aid)
                    print(f"[{a.get('createTime', '')[:19]}] {a.get('type') or 'Activity'}: {a.get('description', '')}")
            time.sleep(poll_interval)
        except KeyboardInterrupt:
            break
        except Exception as e:
            time.sleep(poll_interval)

def main():
    p = argparse.ArgumentParser()
    p.add_argument("session_id")
    p.add_argument("--interval", "-i", type=int, default=5)
    args = p.parse_args()
    try:
        monitor_session(args.session_id, poll_interval=args.interval)
    except Exception as e:
        log_error("JULES", str(e)); sys.exit(1)

if __name__ == "__main__":
    main()
