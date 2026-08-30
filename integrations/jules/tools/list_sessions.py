#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
⚡ AMB_V2 - Jules SDK: Listagem de Sessões e Chats (SRP)
Localização: amb_v2/integrations/jules/tools/list_sessions.py
Responsabilidade Única: Consultar a API do Google Jules e listar todas as sessões recentes,
com status, título, data e link do Pull Request.
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

from config import Colors, log, log_error, get_repo_name
from jules_client import JulesClient


def main():
    parser = argparse.ArgumentParser(description="Lista sessões e tarefas recentes no Google Jules.")
    parser.add_argument("--limit", "-n", type=int, default=20, help="Número de sessões a listar (padrão: 20).")
    parser.add_argument("--state", choices=["QUEUED", "PLANNING", "AWAITING_USER_FEEDBACK", "EXECUTING", "COMPLETED", "FAILED"], help="Filtrar por estado.")
    parser.add_argument("--json", action="store_true", help="Retorna em formato JSON puro.")

    args = parser.parse_args()

    try:
        client = JulesClient()
        sessions = client.list_sessions(page_size=args.limit)

        if args.state:
            sessions = [s for s in sessions if s.get("state") == args.state]

        if args.json:
            print(json.dumps(sessions, indent=2))
        else:
            log("JULES-SESSIONS", f"Sessões recentes encontradas ({len(sessions)}):", Colors.CYAN)
            for s in sessions:
                sid = s.get("name", "").split("/")[-1] or s.get("id")
                title = s.get("title") or "Sem título"
                state = s.get("state", "UNKNOWN")
                created = s.get("createTime", "")[:19].replace("T", " ")

                state_color = Colors.GREEN if state in ["COMPLETED", "SUCCEEDED"] else (
                    Colors.YELLOW if state in ["AWAITING_USER_FEEDBACK", "PLANNING", "EXECUTING"] else Colors.RED
                )

                pr_url = None
                outputs = s.get("outputs", {})
                if isinstance(outputs, list):
                    for out in outputs:
                        if isinstance(out, dict) and out.get("pullRequest", {}).get("url"):
                            pr_url = out["pullRequest"]["url"]
                elif isinstance(outputs, dict):
                    pr_url = outputs.get("pullRequest", {}).get("url")

                print(f"\n  • [{Colors.BOLD}{sid}{Colors.RESET}] {title}")
                print(f"    Estado: {state_color}{state}{Colors.RESET} | Criado em: {created}")
                if pr_url:
                    print(f"    PR: {Colors.GREEN}{pr_url}{Colors.RESET}")
                print(f"    Painel: https://jules.google.com/session/{sid}")

    except Exception as e:
        log_error("JULES-SESSIONS", str(e))
        sys.exit(1)


if __name__ == "__main__":
    main()
