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

from config.bootstrap import ensure_amb_env
ensure_amb_env()

from config import Colors, log, log_error
from integrations.jules.jules_client import JulesClient


def run_list_sources(
    as_json: bool = False,
    client: Optional[JulesClient] = None
) -> List[Dict[str, Any]]:
    """Consulta fontes e repositórios conectados ao Google Jules."""
    c = client or JulesClient()
    sources = c.list_sources()

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
        repo_str = f"({owner}/{repo})" if owner and repo else ""
        print(f"  {idx}. {Colors.BOLD}{name}{Colors.RESET} {Colors.GREEN}{repo_str}{Colors.RESET}")
    print()
    return sources


def main():
    p = argparse.ArgumentParser(description="Lista fontes/repositórios conectados no Google Jules.")
    p.add_argument("--json", action="store_true", help="Exibe a saída em formato JSON puro.")
    args = p.parse_args()

    try:
        run_list_sources(as_json=args.json)
    except Exception as e:
        log_error("JULES", str(e))
        sys.exit(1)


if __name__ == "__main__":
    main()
