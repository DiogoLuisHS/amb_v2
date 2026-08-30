#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""⚡ Jules Tool: monitor_activities (Facade)"""
import sys, os, argparse, time
_cur = os.path.dirname(os.path.abspath(__file__))
while _cur and os.path.basename(_cur) != "amb_v2":
    _p = os.path.dirname(_cur)
    if _p == _cur: break
    _cur = _p
for _s in ["config", "integrations/jules"]:
    _p = os.path.normpath(os.path.join(_cur, *_s.split("/")))
    if os.path.exists(_p) and _p not in sys.path: sys.path.insert(0, _p)
from jules_client import JulesClient, Colors, log, log_error

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
