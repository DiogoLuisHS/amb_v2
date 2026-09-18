#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Facade Module para retrocompatibilidade.
"""

from workspace.setup.setup_project import run_setup, print_setup_prompt

def main() -> None:
    import argparse
    parser = argparse.ArgumentParser(description="Assistente de Setup AMB_V2.")
    parser.add_argument("--auto", action="store_true", help="Executa o setup de forma automática/não-interativa.")
    parser.add_argument("--path", help="Caminho do diretório alvo a ser configurado.")
    parser.add_argument("--force", action="store_true", help="Sobrescreve arquivos de template existentes.")
    parser.add_argument("--dry-run", action="store_true", help="Simula o setup sem modificar o disco.")
    parser.add_argument("--prompt", action="store_true", help="Exibe o Prompt Mestre para IAs.")

    args = parser.parse_args()
    if args.prompt:
        print_setup_prompt()
    else:
        run_setup(
            interactive=not args.auto,
            target_dir=args.path,
            force=args.force,
            dry_run=args.dry_run
        )

if __name__ == "__main__":
    main()
