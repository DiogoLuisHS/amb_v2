#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
⚡ Jules Tool: get_session (Facade)
Localização: amb_v2/integrations/jules/tools/get_session.py
Responsabilidade Única: Exibir metadados detalhados de uma sessão do Google Jules ou iniciar streaming ao vivo.
"""

import sys
import os
import json
import argparse
from typing import Dict, Any, Optional

from core.bootstrap import ensure_amb_env
ensure_amb_env()

from core import Colors, log, log_error
from integrations.jules.jules_client import JulesClient


def run_get_session(
    session_id: str,
    watch: bool = False,
    as_json: bool = False,
    client: Optional[JulesClient] = None
) -> Dict[str, Any]:
    """Obtém detalhes de uma sessão do Jules ou inicia acompanhamento ao vivo."""
    c = client or JulesClient()
    clean_id = c.normalize_session_id(session_id)

    if watch:
        from integrations.jules.jules_watcher import stream_session_activities
        stream_session_activities(clean_id, client=c)
        return c.get_session(clean_id)

    data = c.get_session(clean_id)

    if as_json:
        print(json.dumps(data, indent=2, ensure_ascii=False))
        return data

    sid = data.get("name", "").split("/")[-1] or data.get("id") or clean_id
    state = data.get("state", "UNKNOWN")
    title = data.get("title") or "Sem título"

    if "AWAITING" in state:
        st_color = f"{Colors.YELLOW}{state}{Colors.RESET}"
    elif "COMPLETED" in state or "SUCCEEDED" in state:
        st_color = f"{Colors.GREEN}{state}{Colors.RESET}"
    elif "FAIL" in state or "CANCEL" in state:
        st_color = f"{Colors.RED}{state}{Colors.RESET}"
    else:
        st_color = f"{Colors.CYAN}{state}{Colors.RESET}"

    print(f"\n{Colors.BOLD}{Colors.CYAN}=== 🔍 DETALHES DA SESSÃO JULES ==={Colors.RESET}\n")
    print(f"  • ID:          {Colors.BOLD}{sid}{Colors.RESET}")
    print(f"  • Título:      {title}")
    print(f"  • Estado:      {st_color}")

    pr_info = JulesClient.extract_pull_request(data)
    if pr_info and pr_info.get("url"):
        print(f"  • Pull Request:{Colors.GREEN} {pr_info['url']}{Colors.RESET}")

    src = data.get("sourceContext", {}).get("source", "")
    if src:
        print(f"  • Fonte:       {Colors.DIM}{src}{Colors.RESET}")

    starting_branch = data.get("sourceContext", {}).get("githubRepoContext", {}).get("startingBranch", "")
    if starting_branch:
        print(f"  • Branch Base: {Colors.DIM}{starting_branch}{Colors.RESET}")

    print(f"  • Painel Web:  https://jules.google.com/session/{sid}\n")
    return data


# Alias retrocompatível
get_session_details = run_get_session


def main():
    p = argparse.ArgumentParser(description="Consulta detalhes de uma sessão do Google Jules.")
    p.add_argument("session_id", help="ID da sessão, rota REST ou URL da sessão no navegador.")
    p.add_argument("--watch", "-w", action="store_true", help="Acompanha atividades e saídas em tempo real (streaming).")
    p.add_argument("--json", action="store_true", help="Exibe a saída em formato JSON puro.")
    args = p.parse_args()

    try:
        run_get_session(
            session_id=args.session_id,
            watch=args.watch,
            as_json=args.json
        )
    except Exception as e:
        log_error("JULES", str(e))
        sys.exit(1)


if __name__ == "__main__":
    main()
