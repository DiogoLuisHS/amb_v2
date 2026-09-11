#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🚀 AMB_V2 - CLI Global e Unificada de Automação de Engenharia
Comando: `amb`
Responsabilidade Única: Ponto de entrada CLI que detecta o repositório onde o terminal
está aberto, configura os paths do Python e invoca o parser de CLI.
"""

import os
import sys

# Injeta a raiz do AMB_V2 e todos os submódulos no sys.path
_AMB_ROOT = os.path.abspath(os.path.dirname(__file__))
if _AMB_ROOT not in sys.path:
    sys.path.insert(0, _AMB_ROOT)

for _sub in [
    "config",
    "config/setup_modules",
    "agents",
    "architecture",
    "pipeline",
    "gui",
    "integrations/jules",
    "integrations/jules/tools",
    "integrations/stitch",
    "integrations/stitch/tools",
    "integrations/antigravity",
    "integrations/antigravity/tools",
    "integrations/render",
    "integrations/render/tools",
    "cli_modules",
]:
    _p = os.path.normpath(os.path.join(_AMB_ROOT, *_sub.split("/")))
    if os.path.exists(_p) and _p not in sys.path:
        sys.path.insert(0, _p)
from config import (
    Colors,
    log_error,
    find_repo_root,
    load_env_file,
    get_repo_name,
    AmbError,
)  # noqa: E402
from cli_modules.cli_parsers import create_parser  # noqa: E402


def banner():
    print(
        f"\n{Colors.BOLD}{Colors.CYAN}==========================================================================={Colors.RESET}"
    )
    print(
        f"{Colors.BOLD}{Colors.CYAN}🚀 AMB_V2 CLI — SISTEMA UNIFICADO DE AUTOMAÇÃO E AGENTES{Colors.RESET}"
    )
    print(
        f"📁 Repositório Ativo: {Colors.GREEN}{get_repo_name()}{Colors.RESET} ({find_repo_root()})"
    )
    print(
        f"{Colors.BOLD}{Colors.CYAN}==========================================================================={Colors.RESET}\n"
    )


# -------------------------------------------------------------
# MAIN CLI ENTRYPOINT
# -------------------------------------------------------------
def main():
    load_env_file()

    parser = create_parser()
    args = parser.parse_args()

    if not getattr(args, "command", None):
        banner()
        parser.print_help()
        sys.exit(0)

    try:
        if hasattr(args, "func"):
            args.func(args)
        else:
            parser.print_help()
    except AmbError as ae:
        log_error("AMB", str(ae), getattr(ae, "hint", None))
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n👋 Operação cancelada pelo usuário.")
        sys.exit(0)
    except Exception as e:
        log_error("AMB", f"Erro inesperado: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
