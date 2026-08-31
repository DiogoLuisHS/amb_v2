#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""⚡ Jules Tool: send_message (Facade)"""
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

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--session-id", "-s", required=True)
    p.add_argument("--message", "-m", required=True)
    args = p.parse_args()
    try:
        c = JulesClient()

        # Guardrail to avoid double-sending
        activities_response = c.list_activities(session_id=args.session_id, page_size=1)
        activities = activities_response.get("activities", []) if isinstance(activities_response, dict) else activities_response
        if activities and len(activities) > 0:
            last_activity = activities[0]
            originator = last_activity.get("originator", "")
            if originator and originator.lower() == "user":
                log_error("JULES", "Error: Please wait for the agent to reply before sending another message.")
                sys.exit(1)

        c.send_message(session_id=args.session_id, message=args.message)
        log("JULES", f"✅ Mensagem enviada com sucesso para {args.session_id}!", Colors.GREEN)
    except Exception as e:
        log_error("JULES", str(e)); sys.exit(1)

if __name__ == "__main__":
    main()
