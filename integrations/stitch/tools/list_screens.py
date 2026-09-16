#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""🎨 Stitch Tool: list_screens (Facade)"""
import sys
import json
import argparse

from config.bootstrap import ensure_amb_env
ensure_amb_env()

from stitch_client import list_screens, Colors, log, log_error

run_list_screens = list_screens


def main():
    p = argparse.ArgumentParser(description="Lista todas as telas criadas no projeto Stitch.")
    p.add_argument("--project-id", help="ID do projeto Stitch (padrão: lê do .env).")
    p.add_argument("--json", action="store_true", help="Exibe a saída em formato JSON puro.")
    args = p.parse_args()
    try:
        screens = list_screens(project_id=args.project_id)
        if args.json:
            print(json.dumps(screens, indent=2, ensure_ascii=False))
            return

        print(f"\n{Colors.BOLD}{Colors.CYAN}=== TELAS DO PROJETO STITCH ({len(screens)} encontrada(s)) ==={Colors.RESET}\n")
        if not screens:
            print("  Nenhuma tela encontrada no projeto ativo.")
            return

        for s in screens:
            sid = s.get("id") or s.get("screenId") or (s.get("name", "").split("/")[-1])
            title = s.get("title") or s.get("label") or "Sem título"
            dims = f" ({s.get('width')}x{s.get('height')})" if s.get("width") and s.get("height") else ""
            desc = f" - {s.get('description')}" if s.get("description") else ""
            print(f"  • {Colors.GREEN}{sid:<14}{Colors.RESET} {Colors.BOLD}{title}{Colors.RESET}{dims}{desc}")
        print()
    except Exception as e:
        log_error("STITCH", str(e))
        sys.exit(1)


if __name__ == "__main__":
    main()
