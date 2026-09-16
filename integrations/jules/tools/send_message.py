#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""⚡ Jules Tool: send_message (Facade)"""
import sys
import os
import argparse

from config.bootstrap import ensure_amb_env
ensure_amb_env()

from config import Colors, log, log_error
from integrations.jules.jules_client import JulesClient

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
