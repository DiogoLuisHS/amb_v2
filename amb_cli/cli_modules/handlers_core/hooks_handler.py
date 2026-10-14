import os
from typing import Any
from core.bootstrap import ensure_amb_env
from core import Colors, log
from workspace.project_context import find_repo_root

ensure_amb_env()

def handle_cmd_hooks(args: Any) -> None:
    sub = getattr(args, "hooks_cmd", None)
    if not sub:
        sub = getattr(args, "hooks_action", None)

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
    elif sub == "status":
        root = find_repo_root()
        if not root:
            print(f"{Colors.RED}Erro: Não foi possível determinar a raiz do repositório Git.{Colors.RESET}")
            return

        pre_commit_path = os.path.join(root, ".git", "hooks", "pre-commit")
        if os.path.exists(pre_commit_path):
            try:
                with open(pre_commit_path, "r") as f:
                    content = f.read()

                # Check for execution permissions
                is_executable = os.access(pre_commit_path, os.X_OK)
                if os.name == "nt":
                    is_executable = True # Ignore execute permissions on windows

                if "amb_cli.cli validate --staged" in content and is_executable:
                    print(f"{Colors.GREEN}✅ Hook pre-commit: Ativo e configurado.{Colors.RESET}")
                else:
                    print(f"{Colors.YELLOW}⚠️ Hook pre-commit: Instalado, mas não parece estar configurado corretamente para o AMB_V2 ou falta permissão de execução.{Colors.RESET}")
            except Exception as e:
                print(f"{Colors.RED}Erro ao verificar o hook: {e}{Colors.RESET}")
        else:
            print(f"{Colors.YELLOW}⚠️ Hook pre-commit: Não instalado.{Colors.RESET}")
    else:
        print("Subcomando de hooks inválido. Use 'amb hooks --help'.")
