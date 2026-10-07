import os
from typing import Any
from core.bootstrap import ensure_amb_env
from core import Colors, log
from workspace.project_context import find_repo_root

ensure_amb_env()

def handle_cmd_hooks(args: Any) -> None:
    sub = getattr(args, "hooks_cmd", None)

    if sub == "install":
        root = find_repo_root()
        if not root:
            print(f"{Colors.RED}Erro: Não foi possível determinar a raiz do repositório Git.{Colors.RESET}")
            return

        git_dir = os.path.join(root, ".git")
        if not os.path.isdir(git_dir):
            print(f"{Colors.RED}Erro: Diretório .git não encontrado em {root}.{Colors.RESET}")
            return

        hooks_dir = os.path.join(git_dir, "hooks")
        os.makedirs(hooks_dir, exist_ok=True)

        pre_commit_path = os.path.join(hooks_dir, "pre-commit")

        hook_script = """#!/bin/sh
python -m amb_cli.cli validate --staged
"""
        try:
            with open(pre_commit_path, "w") as f:
                f.write(hook_script)

            # Configura permissões de execução (0o755) se não estiver no Windows (que ignora via os.chmod)
            if os.name != "nt":
                os.chmod(pre_commit_path, 0o755)

            print(f"{Colors.GREEN}✅ Git hook 'pre-commit' instalado com sucesso em: {pre_commit_path}{Colors.RESET}")
        except Exception as e:
            print(f"{Colors.RED}Erro ao instalar o hook: {e}{Colors.RESET}")
    else:
        print("Subcomando de hooks inválido. Use 'amb hooks --help'.")
