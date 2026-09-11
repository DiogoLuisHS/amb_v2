#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""⚡ Jules Tool: approve_plan (Facade)"""

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


def approve_plan(session_id: str, client: JulesClient = None):
    c = client or JulesClient()
    return c.approve_plan(session_id)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--session-id", "-s", required=True)
    args = p.parse_args()
    try:
        c = JulesClient()

        # Guardrail: Check if the latest activity contains a planGenerated from the agent
        activities_response = c.list_activities(
            session_id=args.session_id, page_size=10
        )
        activities = (
            activities_response.get("activities", [])
            if isinstance(activities_response, dict)
            else activities_response
        )

        if not isinstance(activities, list):
            activities = []

        if not activities:
            log_error("JULES", "Error: There is no pending plan to approve.")
            sys.exit(1)

        # Sort by createTime descending to get the most recent activity
        activities.sort(
            key=lambda x: x.get("createTime", "") if isinstance(x, dict) else "",
            reverse=True,
        )
        latest_activity = activities[0]

        originator = (
            latest_activity.get("originator", "").lower()
            if isinstance(latest_activity, dict)
            else ""
        )
        has_plan = (
            isinstance(latest_activity, dict) and "planGenerated" in latest_activity
        )

        if originator != "agent" or not has_plan:
            log_error("JULES", "Error: There is no pending plan to approve.")
            sys.exit(1)

        approve_plan(args.session_id, client=c)
        log(
            "JULES",
            f"✅ Plano da sessão {args.session_id} aprovado com sucesso!",
            Colors.GREEN,
        )
    except Exception as e:
        log_error("JULES", str(e))
        sys.exit(1)


if __name__ == "__main__":
    main()
