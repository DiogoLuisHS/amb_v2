#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
⚡ Jules Tool: create_session (Facade)
Localização: amb_v2/integrations/jules/tools/create_session.py
Responsabilidade Única: Criar e despachar novas sessões de desenvolvimento no Google Jules Cloud VM.
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


def run_create_session(
    prompt: str,
    title: Optional[str] = None,
    base_branch: Optional[str] = None,
    source_name: Optional[str] = None,
    as_json: bool = False,
    client: Optional[JulesClient] = None
) -> Dict[str, Any]:
    """Cria uma nova sessão no Google Jules a partir de prompt ou arquivo markdown."""
    c = client or JulesClient()
    res = c.create_session(
        prompt=prompt,
        title=title,
        source_name=source_name,
        base_branch=base_branch
    )

    sid = res.get("name", "").split("/")[-1] or res.get("id")

    if as_json:
        print(json.dumps(res, indent=2, ensure_ascii=False))
        return res

    log("JULES", f"🎉 Sessão do Jules criada com sucesso! ID: {sid}", Colors.GREEN)
    if title:
        print(f"  • Título:     {title}")
    print(f"  • Painel Web: https://jules.google.com/session/{sid}")
    print(f"👉 Para monitorar ao vivo: amb jules get {sid} --watch\n")
    return res


# Alias retrocompatível
create_session = run_create_session


def main():
    p = argparse.ArgumentParser(description="Cria uma nova sessão no Google Jules.")
    p.add_argument("--prompt", "-p", required=True, help="Texto do prompt ou caminho para arquivo com instruções.")
    p.add_argument("--title", "-t", help="Título descritivo da tarefa.")
    p.add_argument("--branch", "-b", help="Branch base de início no repositório (padrão: branch ativa do Git).")
    p.add_argument("--source", "-s", help="Nome da fonte conectada (ex: sources/github/owner/repo).")
    p.add_argument("--json", action="store_true", help="Exibe a resposta em formato JSON puro.")
    args = p.parse_args()

    try:
        run_create_session(
            prompt=args.prompt,
            title=args.title,
            base_branch=args.branch,
            source_name=args.source,
            as_json=args.json
        )
    except Exception as e:
        log_error("JULES", str(e))
        sys.exit(1)


if __name__ == "__main__":
    main()
