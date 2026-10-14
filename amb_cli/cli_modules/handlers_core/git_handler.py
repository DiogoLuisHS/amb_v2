import json
from typing import Any
from core.bootstrap import ensure_amb_env

ensure_amb_env()

def handle_cmd_git(args: Any) -> None:
    """Gerencia comandos locais do Git e ciclo de vida de Pull Requests."""
    sub = getattr(args, "git_cmd", None)
    from integrations.git.git_service import GitService
    from core import Colors, log

    if sub in ["status", None]:
        from integrations.git.tools.git_status import run_git_status
        run_git_status(as_json=getattr(args, "json", False))

    elif sub == "sync":
        from integrations.git.tools.sync_branch import run_sync_branch
        remote = getattr(args, "remote", "origin")
        branch = getattr(args, "branch", None)
        auto_stash = getattr(args, "auto_stash", True)
        run_sync_branch(remote=remote, branch=branch, auto_stash=auto_stash)

    elif sub == "diff":
        git = GitService()
        file_path = getattr(args, "file", None)
        base_branch = getattr(args, "base", None)
        cached = getattr(args, "cached", False)
        diff_text = git.get_diff(file_path=file_path, base_branch=base_branch, cached=cached)
        if diff_text:
            print(diff_text)
        else:
            log("GIT", "Nenhuma alteração detectada no diff.", Colors.CYAN)

    elif sub == "pr":
        from integrations.git.tools.pr_manager import run_pr_manager
        pr_action = getattr(args, "pr_cmd", None)
        if not pr_action:
            pr_action = "list"
        kwargs = {
            "repo_name": getattr(args, "repo", None),
            "pr_number": getattr(args, "number", None),
            "title": getattr(args, "title", None),
            "body": getattr(args, "body", ""),
            "base": getattr(args, "base", None),
            "head": getattr(args, "head", None),
            "draft": getattr(args, "draft", False),
            "include_drafts": not getattr(args, "no_drafts", False),
            "squash": getattr(args, "squash", True),
            "delete_branch": getattr(args, "delete_branch", True),
            "comment": getattr(args, "comment", None),
        }
        res = run_pr_manager(action=pr_action, **kwargs)
        as_json = getattr(args, "json", False)

        if as_json or isinstance(res, (dict, list)):
            print(json.dumps(res, indent=2, ensure_ascii=False))
        elif res:
            print(res)

    elif sub == "commit":
        message = getattr(args, "message", None)
        no_verify = getattr(args, "no_verify", False)
        git = GitService()

        if not no_verify:
            from workspace import get_rules_manager
            mgr = get_rules_manager()
            staged_files = mgr.get_staged_files()

            if not staged_files:
                log("GIT", "Nenhum arquivo no stage (git add) para auditar e commitar.", Colors.CYAN)
                return

            has_violations = False
            for file_path in staged_files:
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        lines = f.readlines()
                        if len(lines) > 300:
                            log("ANTIGRAVITY", f"Arquivo violando regras canônicas (> 300 linhas): {file_path}", Colors.RED)
                            has_violations = True
                except Exception as e:
                    pass

            if has_violations:
                log("GIT", "Commit abortado devido a violações arquiteturais.", Colors.RED)
                return

        if git._run_git(["git", "commit", "-m", message]).returncode == 0:
            print(f"{Colors.GREEN}✔ Commit realizado com sucesso!{Colors.RESET}")
        else:
            log("GIT", "Erro ao realizar commit.", Colors.RED)

    elif sub == "hooks":
        from .hooks_handler import handle_cmd_hooks
        handle_cmd_hooks(args)

    else:
        print("Subcomando do Git inválido. Use 'amb git --help'.")
