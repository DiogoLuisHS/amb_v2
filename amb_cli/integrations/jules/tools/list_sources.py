#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
⚡ Jules Tool: list_sources (Facade)
Localização: amb_v2/integrations/jules/tools/list_sources.py
Responsabilidade Única: Listar e inspecionar fontes e repositórios conectados à conta Google Jules.
"""

import sys
import os
import json
import argparse
from typing import List, Dict, Any, Optional

from core.bootstrap import ensure_amb_env
ensure_amb_env()

from core import Colors, log, log_error
from integrations.jules.jules_client import JulesClient


def run_list_sources(
    as_json: bool = False,
    filter_expr: Optional[str] = None,
    client: Optional[JulesClient] = None
) -> List[Dict[str, Any]]:
    """Consulta fontes e repositórios conectados ao Google Jules."""
    c = client or JulesClient()
    sources = c.list_sources(filter_expr=filter_expr)

    if as_json:
        print(json.dumps(sources, indent=2, ensure_ascii=False))
        return sources

    print(f"\n{Colors.BOLD}{Colors.CYAN}=== 🌐 FONTES & REPOSITÓRIOS CONECTADOS (GOOGLE JULES) ==={Colors.RESET}\n")
    if not sources:
        print(f"  {Colors.YELLOW}Nenhum repositório conectado encontrado.{Colors.RESET}")
        print(f"  {Colors.DIM}Conecte um repositório no console do Jules: https://jules.google.com{Colors.RESET}\n")
        return sources

    log("JULES", f"Fontes encontradas ({len(sources)}):", Colors.CYAN)
    for idx, s in enumerate(sources, 1):
        name = s.get("name") or s.get("id") or "Fonte desconhecida"
        github_repo = s.get("githubRepo", {})
        owner = github_repo.get("owner", "")
        repo = github_repo.get("repo", "")
        is_private = github_repo.get("isPrivate")
        default_branch = (github_repo.get("defaultBranch") or {}).get("displayName", "")

        repo_str = f"({owner}/{repo})" if owner and repo else ""

        tags = []
        if is_private is True:
            tags.append(f"{Colors.YELLOW}[🔒 Privado]{Colors.RESET}")
        elif is_private is False:
            tags.append(f"{Colors.BLUE}[🌐 Público]{Colors.RESET}")

        if default_branch:
            tags.append(f"{Colors.DIM}[🌿 Default: {default_branch}]{Colors.RESET}")

        tags_str = " ".join(tags)
        if tags_str:
            print(f"  {idx}. {Colors.BOLD}{name}{Colors.RESET} {Colors.GREEN}{repo_str}{Colors.RESET} {tags_str}")
        else:
            print(f"  {idx}. {Colors.BOLD}{name}{Colors.RESET} {Colors.GREEN}{repo_str}{Colors.RESET}")
    print()
    return sources


def main():
    p = argparse.ArgumentParser(description="Lista fontes/repositórios conectados no Google Jules.")
    p.add_argument("--json", action="store_true", help="Exibe a saída em formato JSON puro.")
    p.add_argument("--filter", "-f", help="Filtro AIP-160 para consultar fontes específicas na API.")
    args = p.parse_args()

    try:
        run_list_sources(as_json=args.json, filter_expr=args.filter)
    except Exception as e:
        log_error("JULES", str(e))
        sys.exit(1)


if __name__ == "__main__":
    main()
