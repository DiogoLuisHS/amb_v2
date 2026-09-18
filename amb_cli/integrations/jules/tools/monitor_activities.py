#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
⚡ Jules Tool: monitor_activities (Facade)
Localização: amb_v2/integrations/jules/tools/monitor_activities.py
Responsabilidade Única: Acompanhar em tempo real (streaming) saídas, comandos bash, planos e diálogos de uma sessão Jules.
"""

import sys
import os
import argparse
from typing import Optional

from core.bootstrap import ensure_amb_env
ensure_amb_env()

from core import Colors, log, log_error
from integrations.jules.jules_client import JulesClient
from integrations.jules.jules_watcher import stream_session_activities


def run_monitor_activities(
    session_id: str,
    poll_interval: int = 4,
    client: Optional[JulesClient] = None
) -> None:
    """Inicia o streaming em tempo real das atividades da sessão no terminal."""
    c = client or JulesClient()
    clean_id = c.normalize_session_id(session_id)
    stream_session_activities(session_id=clean_id, poll_interval=poll_interval, client=c)


# Alias retrocompatível
monitor_session = run_monitor_activities


def main():
    p = argparse.ArgumentParser(description="Acompanha em tempo real as atividades de uma sessão do Google Jules.")
    p.add_argument("session_id", nargs="?", help="ID ou URL da sessão do Jules.")
    p.add_argument("--session-id", "-s", dest="session_id_flag", help="ID ou URL da sessão (flag alternativa).")
    p.add_argument("--interval", "-i", type=int, default=4, help="Intervalo de pooling em segundos (padrão: 4s).")
    args = p.parse_args()

    target_id = args.session_id or args.session_id_flag
    if not target_id:
        log_error("JULES", "ID da sessão é obrigatório.")
        sys.exit(1)

    try:
        run_monitor_activities(session_id=target_id, poll_interval=args.interval)
    except Exception as e:
        log_error("JULES", str(e))
        sys.exit(1)


if __name__ == "__main__":
    main()
