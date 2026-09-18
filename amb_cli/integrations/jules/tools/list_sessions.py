#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
⚡ Jules Tool: list_sessions (Facade)
Localização: amb_v2/integrations/jules/tools/list_sessions.py
Responsabilidade Única: Listar sessões do Google Jules com suporte a filtros de repositório, estado e saída JSON.
"""

import sys
import os
import json
import argparse
from typing import List, Dict, Any, Optional

from core.bootstrap import ensure_amb_env
ensure_amb_env()

from core import Colors, log, log_error
from workspace import get_repo_name
from integrations.jules.jules_client import JulesClient


def run_list_sessions(
    limit: int = 10,
    repo: Optional[str] = None,
    all_repos: bool = False,
    state: Optional[str] = None,
    as_json: bool = False,
    client: Optional[JulesClient] = None
) -> List[Dict[str, Any]]:
    """Consulta e lista sessões do Jules com suporte a filtros de escopo."""
    c = client or JulesClient()
    target_repo = None if all_repos else (repo or get_repo_name())

    sessions = c.list_sessions(
        page_size=max(limit, 10),
        repo_filter=target_repo,
        state_filter=state
    )
    displayed = sessions[:limit]

    if as_json:
        print(json.dumps(displayed, indent=2, ensure_ascii=False))
        return displayed

    filter_desc = f" (Repositório: {target_repo})" if target_repo else " (Todos os repositórios)"
    state_desc = f" [Estado: {state.upper()}]" if state else ""
    print(f"\n{Colors.BOLD}{Colors.CYAN}=== 📋 SESSÕES GOOGLE JULES{filter_desc}{state_desc} ==={Colors.RESET}\n")

    if not displayed:
        print(f"  {Colors.YELLOW}Nenhuma sessão encontrada para os critérios selecionados.{Colors.RESET}\n")
        return displayed

    for s in displayed:
        sid = s.get("name", "").split("/")[-1] or s.get("id")
        title = s.get("title") or "Sem título"
        st = s.get("state", "UNKNOWN")

        # Colorização por estado
        if "AWAITING" in st:
            st_color = f"{Colors.YELLOW}{st}{Colors.RESET}"
        elif "COMPLETED" in st or "SUCCEEDED" in st:
            st_color = f"{Colors.GREEN}{st}{Colors.RESET}"
        elif "FAIL" in st or "CANCEL" in st:
            st_color = f"{Colors.RED}{st}{Colors.RESET}"
        else:
            st_color = f"{Colors.CYAN}{st}{Colors.RESET}"

        pr_info = JulesClient.extract_pull_request(s)
        pr_str = f" | PR: {Colors.GREEN}{pr_info['url']}{Colors.RESET}" if pr_info and pr_info.get("url") else ""

        print(f"  • [{Colors.BOLD}{sid}{Colors.RESET}] {st_color}: {title}{pr_str}")
        print(f"    {Colors.DIM}https://jules.google.com/session/{sid}{Colors.RESET}")
    print()
    return displayed


def main():
    p = argparse.ArgumentParser(description="Lista sessões recentes do Google Jules.")
    p.add_argument("--limit", "-n", type=int, default=10, help="Limite máximo de sessões exibidas (padrão: 10).")
    p.add_argument("--repo", "-r", help="Filtra por repositório específico (ex: org/repo).")
    p.add_argument("--all", "-a", action="store_true", help="Lista sessões de todos os repositórios conectados.")
    p.add_argument("--state", "-s", help="Filtra por estado (ex: AWAITING_USER_FEEDBACK, IN_PROGRESS, COMPLETED, FAILED).")
    p.add_argument("--json", action="store_true", help="Exibe a saída em formato JSON puro.")
    args = p.parse_args()

    try:
        run_list_sessions(
            limit=args.limit,
            repo=args.repo,
            all_repos=args.all,
            state=args.state,
            as_json=args.json
        )
    except Exception as e:
        log_error("JULES", str(e))
        sys.exit(1)


if __name__ == "__main__":
    main()
