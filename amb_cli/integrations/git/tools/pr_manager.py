#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
⚡ Git Tool: pr_manager (Facade)
Localização: amb_v2/integrations/git/tools/pr_manager.py
Responsabilidade Única: Prover interface CLI e de serviço para operações do ciclo de vida
de Pull Requests no GitHub (list, get, create, ready, approve, merge, close).
"""

import sys
import os
import json
import argparse
from typing import Dict, Any, Optional, List

from core.bootstrap import ensure_amb_env
ensure_amb_env()

from core import Colors, log, log_error, ApiExecutionError
from integrations.git.git_service import GitService


def run_pr_manager(action: str, **kwargs) -> Any:
    """Despacha a ação de ciclo de vida do Pull Request para o GitService."""
    git = GitService()
    git.check_gh_auth(fail_silently=False)

    repo_name = kwargs.get("repo_name")

    if action == "list":
        include_drafts = kwargs.get("include_drafts", True)
        return git.list_open_prs(repo_name=repo_name, include_drafts=include_drafts)

    elif action == "get":
        pr_number = kwargs.get("pr_number")
        if not pr_number:
            raise ApiExecutionError("Número do PR é obrigatório para consulta.")
        return git.get_pr(pr_number=int(pr_number), repo_name=repo_name)

    elif action == "create":
        title = kwargs.get("title")
        body = kwargs.get("body", "")
        if not title:
            raise ApiExecutionError("Título é obrigatório para criação de PR.")
        return git.create_pr(
            title=title,
            body=body,
            base=kwargs.get("base"),
            head=kwargs.get("head"),
            draft=kwargs.get("draft", False),
            repo_name=repo_name,
        )

    elif action == "ready":
        pr_number = kwargs.get("pr_number")
        if not pr_number:
            raise ApiExecutionError("Número do PR é obrigatório para marcar como pronto.")
        success = git.mark_pr_ready(pr_number=int(pr_number), repo_name=repo_name)
        return {"success": success, "number": pr_number, "action": "ready"}

    elif action == "approve":
        pr_number = kwargs.get("pr_number")
        if not pr_number:
            raise ApiExecutionError("Número do PR é obrigatório para aprovação.")
        body = kwargs.get("body", "✅ Aprovado automaticamente pelo AMB_V2 após validação de integridade.")
        success = git.approve_pr(pr_number=int(pr_number), repo_name=repo_name, body=body)
        return {"success": success, "number": pr_number, "action": "approved"}

    elif action == "merge":
        pr_number = kwargs.get("pr_number")
        if not pr_number:
            raise ApiExecutionError("Número do PR é obrigatório para merge.")
        squash = kwargs.get("squash", True)
        delete_branch = kwargs.get("delete_branch", True)
        admin = kwargs.get("admin", True)
        success = git.merge_pr(
            pr_number=int(pr_number),
            repo_name=repo_name,
            squash=squash,
            delete_branch=delete_branch,
            admin=admin,
        )
        return {"success": success, "number": pr_number, "action": "merged"}

    elif action == "close":
        pr_number = kwargs.get("pr_number")
        if not pr_number:
            raise ApiExecutionError("Número do PR é obrigatório para fechamento.")
        comment = kwargs.get("comment")
        delete_branch = kwargs.get("delete_branch", False)
        success = git.close_pr(
            pr_number=int(pr_number),
            comment=comment,
            delete_branch=delete_branch,
            repo_name=repo_name,
        )
        return {"success": success, "number": pr_number, "action": "closed"}

    else:
        raise ApiExecutionError(f"Ação de PR desconhecida: {action}")


def main():
    p = argparse.ArgumentParser(description="Gerenciador de Pull Requests no GitHub via GitHub CLI.")
    sub = p.add_subparsers(dest="action", required=True)

    # list
    p_list = sub.add_parser("list", help="Lista PRs abertos.")
    p_list.add_argument("--repo", help="Repositório alvo (dono/repo).")
    p_list.add_argument("--no-drafts", action="store_true", help="Oculta PRs em draft.")
    p_list.add_argument("--json", action="store_true", help="Exibe em JSON puro.")

    # get
    p_get = sub.add_parser("get", help="Exibe detalhes de um PR.")
    p_get.add_argument("number", type=int, help="Número do PR.")
    p_get.add_argument("--repo", help="Repositório alvo.")
    p_get.add_argument("--json", action="store_true", help="Exibe em JSON puro.")

    # create
    p_create = sub.add_parser("create", help="Cria um novo PR.")
    p_create.add_argument("--title", "-t", required=True, help="Título do PR.")
    p_create.add_argument("--body", "-b", default="", help="Corpo descritivo do PR.")
    p_create.add_argument("--base", help="Branch base.")
    p_create.add_argument("--head", help="Branch de origem.")
    p_create.add_argument("--draft", action="store_true", help="Criar como rascunho (Draft).")
    p_create.add_argument("--repo", help="Repositório alvo.")
    p_create.add_argument("--json", action="store_true", help="Exibe em JSON puro.")

    # ready
    p_ready = sub.add_parser("ready", help="Remove status de draft do PR.")
    p_ready.add_argument("number", type=int, help="Número do PR.")
    p_ready.add_argument("--repo", help="Repositório alvo.")

    # approve
    p_app = sub.add_parser("approve", help="Aprova o PR.")
    p_app.add_argument("number", type=int, help="Número do PR.")
    p_app.add_argument("--body", default="✅ Aprovado pelo AMB_V2.", help="Comentário de aprovação.")
    p_app.add_argument("--repo", help="Repositório alvo.")

    # merge
    p_merge = sub.add_parser("merge", help="Realiza o merge do PR.")
    p_merge.add_argument("number", type=int, help="Número do PR.")
    p_merge.add_argument("--no-squash", action="store_false", dest="squash", help="Não usar squash merge.")
    p_merge.add_argument("--keep-branch", action="store_false", dest="delete_branch", help="Não deletar a branch após merge.")
    p_merge.add_argument("--repo", help="Repositório alvo.")

    # close
    p_close = sub.add_parser("close", help="Fecha o PR sem merge.")
    p_close.add_argument("number", type=int, help="Número do PR.")
    p_close.add_argument("--comment", help="Comentário opcional ao fechar.")
    p_close.add_argument("--delete-branch", action="store_true", help="Deletar branch associada.")
    p_close.add_argument("--repo", help="Repositório alvo.")

    args = p.parse_args()

    try:
        kwargs = vars(args)
        action = kwargs.pop("action")
        pr_number = kwargs.pop("number", None)
        if pr_number:
            kwargs["pr_number"] = pr_number
        if "no_drafts" in kwargs:
            kwargs["include_drafts"] = not kwargs.pop("no_drafts")
        as_json = kwargs.pop("json", False)

        res = run_pr_manager(action=action, **kwargs)

        if as_json or isinstance(res, (dict, list)):
            print(json.dumps(res, indent=2, ensure_ascii=False))
        else:
            print(res)
    except Exception as e:
        log_error("GIT", str(e))
        sys.exit(1)


if __name__ == "__main__":
    main()
