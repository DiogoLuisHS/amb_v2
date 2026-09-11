#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""🚀 Render Tool: get_deploy_status (Facade)"""

import sys, os, argparse

_cur = os.path.dirname(os.path.abspath(__file__))
while _cur and os.path.basename(_cur) != "amb_v2":
    _p = os.path.dirname(_cur)
    if _p == _cur:
        break
    _cur = _p
for _s in ["config", "integrations/render"]:
    _p = os.path.normpath(os.path.join(_cur, *_s.split("/")))
    if os.path.exists(_p) and _p not in sys.path:
        sys.path.insert(0, _p)
from render_client import RenderClient, Colors, log, log_error, require_env


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--service-id", "-s")
    args = p.parse_args()
    try:
        client = RenderClient()
        sid = args.service_id or require_env("RENDER_SERVICE_ID")
        deploys = client.list_deploys(service_id=sid, limit=1)
        if deploys:
            dep = deploys[0].get("deploy", deploys[0])
            status = dep.get("status", "UNKNOWN")
            log("RENDER", f"Status do serviço {sid}: {status}", Colors.CYAN)
            print(f"  • Deploy ID: {dep.get('id')} | Status: {status}")
        else:
            print(f"Nenhum deploy encontrado para {sid}.")
    except Exception as e:
        log_error("RENDER", str(e))
        sys.exit(1)


if __name__ == "__main__":
    main()
