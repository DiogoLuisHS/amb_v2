#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
⚡ AMB_V2 - Jules SDK: Criação de Nova Sessão Assíncrona de Codificação (SRP)
Localização: amb_v2/integrations/jules/tools/create_session.py
Responsabilidade Única: Despachar uma tarefa com prompt e branch base para a cloud do Google Jules.
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

from config import Colors, log, log_error, get_repo_name, ApiExecutionError
from jules_client import JulesClient


def resolve_source_name(client: JulesClient, repo_target: str) -> str:
    """Busca o source_name correto na API do Jules que corresponde ao repositório."""
    sources = client.list_sources()
    for s in sources:
        gh = s.get("githubRepo", {})
        full = f"{gh.get('owner')}/{gh.get('repo')}"
        if full.lower() == repo_target.lower():
            return s.get("name")
    
    if sources:
        first = sources[0]
        first_repo = f"{first.get('githubRepo', {}).get('owner')}/{first.get('githubRepo', {}).get('repo')}"
        log("JULES-SESSION", f"Aviso: Repo '{repo_target}' não encontrado exato. Usando fonte conectada: '{first_repo}'", Colors.YELLOW)
        return first.get("name")

    raise ApiExecutionError(
        f"Nenhum repositório conectado encontrado no Jules.",
        hint="Acesse https://jules.google.com e vincule seu repositório GitHub à sua conta."
    )


def create_session(
    prompt: str,
    title: str = None,
    repo_name: str = None,
    base_branch: str = "main"
) -> dict:
    """Cria uma nova sessão no Jules."""
    client = JulesClient()
    target_repo = repo_name or get_repo_name()
    source_name = resolve_source_name(client, target_repo)

    log("JULES-SESSION", f"Despachando tarefa para Jules no repositório {target_repo} (branch: {base_branch})...", Colors.CYAN)
    res = client.create_session(
        prompt=prompt,
        source_name=source_name,
        title=title,
        base_branch=base_branch
    )
    return res


def main():
    parser = argparse.ArgumentParser(description="Cria uma nova sessão de codificação no Google Jules.")
    parser.add_argument("--prompt", "-p", required=True, help="Prompt da tarefa a ser executada pelo agente.")
    parser.add_argument("--title", "-t", help="Título descritivo da sessão.")
    parser.add_argument("--repo", "-r", help="Repositório GitHub (ex: owner/repo).")
    parser.add_argument("--branch", "-b", default="main", help="Branch base para início do trabalho.")
    parser.add_argument("--json", action="store_true", help="Retorna saída JSON puro.")

    args = parser.parse_args()

    try:
        res = create_session(
            prompt=args.prompt,
            title=args.title,
            repo_name=args.repo,
            base_branch=args.branch
        )
        if args.json:
            print(json.dumps(res, indent=2))
        else:
            sid = res.get("name", "").split("/")[-1] or res.get("id")
            log("JULES-SESSION", "✅ Sessão criada com sucesso no Google Jules!", Colors.GREEN)
            print(f"  • Session ID: {Colors.BOLD}{sid}{Colors.RESET}")
            print(f"  • Título:     {res.get('title') or args.title or 'Sem título'}")
            print(f"  • Estado:     {res.get('state', 'QUEUED')}")
            print(f"  • Painel Web: https://jules.google.com/session/{sid}")
    except Exception as e:
        log_error("JULES-SESSION", str(e))
        sys.exit(1)


if __name__ == "__main__":
    main()
