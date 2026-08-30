#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
⚡ AMB_V2 - Jules SDK: Consulta de Estado e Saídas de Sessão (SRP)
Localização: amb_v2/integrations/jules/tools/get_session.py
Responsabilidade Única: Obter estado atual, branch criada e Pull Request de uma sessão Jules.
"""

import os
import sys
import json
import argparse

# Bootstrap dinâmico de caminhos amb_v2
_cur = os.path.dirname(os.path.abspath(__file__))
while _cur and os.path.basename(_cur) != "amb_v2":
    _p = os.path.dirname(_cur)
    if _p == _cur:
        break
    _cur = _p
_AMB = _cur
for _sub in [
    "config", "agents", "pipeline", "dashboard", "dashboard/watchers",
    "integrations/jules", "integrations/jules/tools",
    "integrations/stitch", "integrations/stitch/tools",
    "integrations/antigravity", "integrations/antigravity/tools",
    "integrations/render", "integrations/render/tools",
]:
    _p = os.path.normpath(os.path.join(_AMB, *_sub.split("/")))
    if os.path.exists(_p) and _p not in sys.path:
        sys.path.insert(0, _p)

from config import Colors, log, log_error
from jules_client import JulesClient


def main():
    parser = argparse.ArgumentParser(description="Consulta o status e saídas de uma sessão no Jules.")
    parser.add_argument("--session-id", "-s", required=True, help="ID da sessão Jules (ou sessions/<id>).")
    parser.add_argument("--json", action="store_true", help="Retorna saída JSON.")

    args = parser.parse_args()

    try:
        client = JulesClient()
        data = client.get_session(args.session_id)

        if args.json:
            print(json.dumps(data, indent=2))
        else:
            sid = data.get("name", "").split("/")[-1] or data.get("id")
            state = data.get("state", "UNKNOWN")
            log("JULES-STATUS", f"Sessão {sid}:", Colors.CYAN)
            print(f"  • Título:     {data.get('title') or 'Sem título'}")
            print(f"  • Estado:     {Colors.BOLD}{state}{Colors.RESET}")
            
            outputs = data.get("outputs", {})
            pr_url = None
            branch_name = None

            if isinstance(outputs, list):
                for item in outputs:
                    if isinstance(item, dict):
                        if item.get("pullRequest", {}).get("url"):
                            pr_url = item["pullRequest"]["url"]
                        if item.get("branch"):
                            branch_name = item["branch"]
            elif isinstance(outputs, dict):
                pr_url = outputs.get("pullRequest", {}).get("url")
                branch_name = outputs.get("branch")

            if pr_url:
                print(f"  • Pull Request: {Colors.GREEN}{pr_url}{Colors.RESET}")
            if branch_name:
                print(f"  • Branch:       {branch_name}")
            print(f"  • Painel Web:   https://jules.google.com/session/{sid}")
    except Exception as e:
        log_error("JULES-STATUS", str(e))
        sys.exit(1)


if __name__ == "__main__":
    main()
