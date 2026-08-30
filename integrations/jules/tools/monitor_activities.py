#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
⚡ AMB_V2 - Jules SDK: Monitoramento de Atividades em Tempo Real (SRP)
Localização: amb_v2/integrations/jules/tools/monitor_activities.py
Responsabilidade Única: Fazer polling e imprimir em tempo real os passos, bash outputs e mensagens da sessão.
"""

import os
import sys
import time
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


def monitor_session(session_id: str, poll_interval: int = 5):
    """Loop de streaming das atividades do agente."""
    client = JulesClient()
    seen_ids = set()
    log("JULES-MONITOR", f"Iniciando acompanhamento da sessão {session_id}...", Colors.CYAN)

    while True:
        try:
            session = client.get_session(session_id)
            state = session.get("state", "UNKNOWN")

            act_data = client.list_activities(session_id=session_id, page_size=50)
            activities = act_data.get("activities", [])
            activities.reverse()

            for act in activities:
                aid = act.get("name") or act.get("id") or str(act.get("createTime"))
                if aid not in seen_ids:
                    seen_ids.add(aid)
                    orig = act.get("originator", "SYSTEM")
                    desc = act.get("description") or act.get("title") or ""
                    
                    if "bashCommand" in act:
                        cmd = act.get("bashCommand", {}).get("command", "")
                        print(f"[{Colors.YELLOW}BASH{Colors.RESET}] $ {cmd}")
                    elif "agentMessage" in act or "agentMessaged" in act:
                        txt = (act.get("agentMessaged") or act.get("agentMessage") or {}).get("text") or desc
                        print(f"[{Colors.CYAN}AGENTE{Colors.RESET}] {txt}")
                    elif "userFeedbackRequired" in act:
                        q = act.get("userFeedbackRequired", {}).get("question") or desc
                        print(f"[{Colors.BOLD}{Colors.RED}DÚVIDA DO AGENTE{Colors.RESET}] ❓ {q}")
                    else:
                        print(f"[{Colors.DIM}{orig}{Colors.RESET}] {desc}")

            if state in ["COMPLETED", "SUCCEEDED", "FAILED", "CANCELLED", "CLOSED"]:
                log("JULES-MONITOR", f"Sessão finalizada com estado: {state}", Colors.GREEN if state in ["COMPLETED", "SUCCEEDED"] else Colors.RED)
                break

            time.sleep(poll_interval)
        except KeyboardInterrupt:
            print(f"\n{Colors.YELLOW}Monitoramento interrompido.{Colors.RESET}")
            break
        except Exception as e:
            log_error("JULES-MONITOR", f"Erro no polling: {e}")
            time.sleep(poll_interval)


def main():
    parser = argparse.ArgumentParser(description="Acompanha em tempo real as atividades de uma sessão Jules.")
    parser.add_argument("--session-id", "-s", required=True, help="ID da sessão Jules.")
    parser.add_argument("--interval", "-i", type=int, default=5, help="Intervalo de polling em segundos (padrão: 5s).")

    args = parser.parse_args()
    monitor_session(session_id=args.session_id, poll_interval=args.interval)


if __name__ == "__main__":
    main()
