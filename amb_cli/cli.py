#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🚀 AMB_V2 - CLI Global e Unificada de Automação de Engenharia
Comando: `amb`
Responsabilidade Única: Ponto de entrada CLI que detecta o repositório onde o terminal
está aberto, configura os paths do Python e invoca o parser de CLI.
"""

import sys
from pathlib import Path

_cur = Path(__file__).resolve()
_pkg = _cur.parent
_root = _pkg.parent
for _p in [str(_pkg), str(_root)]:
    if _p not in sys.path:
        sys.path.insert(0, _p)

from config.bootstrap import ensure_amb_env
ensure_amb_env()

from config import Colors, log_error, find_repo_root, load_env_file, get_repo_name, AmbError  # noqa: E402
from cli_modules.cli_parsers import create_parser  # noqa: E402


def banner() -> None:
    """Exibe o cabeçalho resumido da CLI com o repositório ativo detectado."""
    print(f"\n{Colors.BOLD}{Colors.CYAN}==========================================================================={Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.CYAN}🚀 AMB_V2 CLI — SISTEMA UNIFICADO DE AUTOMAÇÃO E AGENTES{Colors.RESET}")
    print(f"📁 Repositório Ativo: {Colors.GREEN}{get_repo_name()}{Colors.RESET} ({find_repo_root()})")
    print(f"{Colors.BOLD}{Colors.CYAN}==========================================================================={Colors.RESET}\n")


def main() -> None:
    """Ponto de entrada principal da CLI."""
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
