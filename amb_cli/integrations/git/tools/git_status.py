#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
⚡ Git Tool: git_status (Facade)
Localização: amb_v2/integrations/git/tools/git_status.py
Responsabilidade Única: Diagnóstico consolidado de branches, upstream, ahead/behind,
status da working tree e autenticação da GitHub CLI.
"""

import sys
import os
import json
import argparse
from typing import Dict, Any, Optional

from config.bootstrap import ensure_amb_env
ensure_amb_env()

from config import Colors, log, log_error
from integrations.git.git_service import GitService


def run_git_status(as_json: bool = False, cwd: Optional[str] = None) -> Dict[str, Any]:
    """Coleta e opcionalmente imprime o status detalhado do Git e GitHub CLI."""
    git = GitService()
    status_info = git.get_detailed_status(cwd=cwd)
    gh_installed = git.is_gh_installed()
    gh_auth = git.check_gh_auth(cwd=cwd, fail_silently=True)

    status_info["github_cli"] = {
        "installed": gh_installed,
        "authenticated": gh_auth,
    }

    if as_json:
        print(json.dumps(status_info, indent=2, ensure_ascii=False))
        return status_info

    print(f"\n{Colors.BOLD}{Colors.CYAN}=== ⚡ STATUS DO REPOSITÓRIO GIT ==={Colors.RESET}\n")
    print(f"  • Branch Ativa: {Colors.BOLD}{status_info['branch']}{Colors.RESET}")
    print(f"  • Upstream: {Colors.DIM}{status_info['upstream'] or 'Nenhum'}{Colors.RESET}")
    print(f"  • Commits: Ahead +{status_info['ahead']} | Behind -{status_info['behind']}")
    clean_color = Colors.GREEN if status_info["is_clean"] else Colors.YELLOW
    print(f"  • Working Tree: {clean_color}{'Limpa' if status_info['is_clean'] else 'Modificada'}{Colors.RESET}")
    print(f"  • Repositório GitHub: {Colors.BOLD}{status_info['github_repo'] or 'Não detectado'}{Colors.RESET}")

    gh_st = f"{Colors.GREEN}Autenticada{Colors.RESET}" if gh_auth else (f"{Colors.YELLOW}Instalada, não autenticada{Colors.RESET}" if gh_installed else f"{Colors.RED}Não instalada{Colors.RESET}")
    print(f"  • GitHub CLI: {gh_st}")

    if status_info["staged"]:
        print(f"\n{Colors.GREEN}Arquivos Prontos para Commit (Staged):{Colors.RESET}")
        for s in status_info["staged"][:15]:
            print(f"    + {s}")
        if len(status_info["staged"]) > 15:
            print(f"    ... [+ {len(status_info['staged']) - 15} arquivos omitidos]")

    if status_info["unstaged"]:
        print(f"\n{Colors.YELLOW}Arquivos Modificados Não Preparados (Unstaged):{Colors.RESET}")
        for u in status_info["unstaged"][:15]:
            print(f"    ~ {u}")
        if len(status_info["unstaged"]) > 15:
            print(f"    ... [+ {len(status_info['unstaged']) - 15} arquivos omitidos]")

    if status_info["untracked"]:
        print(f"\n{Colors.RED}Arquivos Não Rastreados (Untracked):{Colors.RESET}")
        for ut in status_info["untracked"][:15]:
            print(f"    ? {ut}")
        if len(status_info["untracked"]) > 15:
            print(f"    ... [+ {len(status_info['untracked']) - 15} arquivos omitidos]")
    print()

    return status_info


def main():
    p = argparse.ArgumentParser(description="Exibe o status consolidado do Git e GitHub CLI.")
    p.add_argument("--json", action="store_true", help="Exibe a saída em formato JSON puro.")
    args = p.parse_args()

    try:
        run_git_status(as_json=args.json)
    except Exception as e:
        log_error("GIT", str(e))
        sys.exit(1)


if __name__ == "__main__":
    main()
