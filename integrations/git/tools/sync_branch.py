#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
⚡ Git Tool: sync_branch (Facade)
Localização: amb_v2/integrations/git/tools/sync_branch.py
Responsabilidade Única: Prover interface CLI e de serviço para sincronização segura
da branch ativa com o repositório remoto (fetch, pull, auto-stash).
"""

import sys
import os
import argparse
from typing import Optional

from config.bootstrap import ensure_amb_env
ensure_amb_env()

from config import Colors, log, log_error, ApiExecutionError
from integrations.git.git_service import GitService


def run_sync_branch(
    remote: str = "origin",
    branch: Optional[str] = None,
    auto_stash: bool = True,
    cwd: Optional[str] = None
) -> bool:
    """Sincroniza a branch local com o remote realizando fetch e pull com stash preventivo opcional."""
    git = GitService()
    active_branch = branch or git.get_current_branch(cwd=cwd)
    log("GIT", f"Sincronizando branch '{active_branch}' com remote '{remote}'...", Colors.CYAN)

    is_clean = git.is_clean(cwd=cwd)
    stashed = False

    if not is_clean:
        if auto_stash:
            log("GIT", "Alterações locais não commitadas detectadas. Salvando em stash preventivo...", Colors.YELLOW)
            git.stash(action="push", message="AMB_V2 auto-stash before sync", cwd=cwd)
            stashed = True
        else:
            raise ApiExecutionError("Working tree contém alterações não commitadas. Faça commit ou use --auto-stash.")

    try:
        log("GIT", f"Buscando referências remotas (git fetch {remote})...", Colors.CYAN)
        git.fetch(remote=remote, prune=True, cwd=cwd)

        log("GIT", f"Atualizando branch local (git pull {remote} {active_branch})...", Colors.CYAN)
        pulled = git.pull(remote=remote, branch=active_branch, cwd=cwd)
        if not pulled:
            raise ApiExecutionError(f"Falha ao executar git pull {remote} {active_branch}.")

        log("GIT", f"✅ Branch '{active_branch}' sincronizada com sucesso!", Colors.GREEN)
        return True
    finally:
        if stashed:
            log("GIT", "Restaurando alterações locais do stash...", Colors.CYAN)
            git.stash(action="pop", cwd=cwd)


def main():
    p = argparse.ArgumentParser(description="Sincroniza a branch ativa com o repositório remoto.")
    p.add_argument("--remote", "-r", default="origin", help="Nome do remote (padrão: origin).")
    p.add_argument("--branch", "-b", help="Nome da branch (padrão: branch ativa).")
    p.add_argument("--no-stash", action="store_false", dest="auto_stash", help="Não realizar stash automático se houver alterações locais.")
    args = p.parse_args()

    try:
        run_sync_branch(remote=args.remote, branch=args.branch, auto_stash=args.auto_stash)
    except Exception as e:
        log_error("GIT", str(e))
        sys.exit(1)


if __name__ == "__main__":
    main()
