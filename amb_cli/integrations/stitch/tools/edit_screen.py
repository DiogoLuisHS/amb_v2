#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""🎨 Stitch Tool: edit_screen (Facade)"""
import sys
import argparse

from config.bootstrap import ensure_amb_env
ensure_amb_env()

from stitch_client import edit_screen, Colors, log, log_error

run_edit_screen = edit_screen


def main():
    p = argparse.ArgumentParser(description="Refina e edita uma tela existente no Google Stitch.")
    p.add_argument("--screen-id", "-s", required=True, help="ID da tela a ser editada.")
    p.add_argument("--prompt", "-p", required=True, help="Instruções visuais de refinamento.")
    p.add_argument("--output", "-o", help="Caminho do arquivo para salvar o novo HTML refinado.")
    args = p.parse_args()
    try:
        res = edit_screen(screen_id=args.screen_id, prompt=args.prompt, output_file=args.output)
        log("STITCH", f"Tela {args.screen_id} refinada com sucesso!", Colors.GREEN)
        if res.get("screenshotUrl"):
            print(f"  • Nova Screenshot: {res['screenshotUrl']}")
        if args.output:
            print(f"  • HTML salvo em: {args.output}")
    except Exception as e:
        log_error("STITCH", str(e))
        sys.exit(1)


if __name__ == "__main__":
    main()
