#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
⚡ AMB_V2 - Jules SDK: Listar Fontes e Repositórios Conectados (SRP)
Localização: amb_v2/integrations/jules/tools/list_sources.py
Responsabilidade Única: Consultar a API do Google Jules e exibir os repositórios vinculados.
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
    parser = argparse.ArgumentParser(description="Lista os repositórios do GitHub conectados à sua conta Jules.")
    parser.add_argument("--json", action="store_true", help="Retorna em formato JSON puro.")

    args = parser.parse_args()

    try:
        client = JulesClient()
        sources = client.list_sources()

        if args.json:
            print(json.dumps(sources, indent=2))
        else:
            log("JULES-SOURCES", f"Repositórios conectados ({len(sources)}):", Colors.CYAN)
            for s in sources:
                name = s.get("name")
                gh = s.get("githubRepo", {})
                owner = gh.get("owner", "")
                repo = gh.get("repo", "")
                full_repo = f"{owner}/{repo}" if owner and repo else "N/A"
                print(f"  • Source ID: {Colors.BOLD}{name}{Colors.RESET} | Repo: {Colors.GREEN}{full_repo}{Colors.RESET}")
    except Exception as e:
        log_error("JULES-SOURCES", str(e))
        sys.exit(1)


if __name__ == "__main__":
    main()
