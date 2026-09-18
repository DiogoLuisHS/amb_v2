#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""🎨 Stitch Tool: get_screen (Facade)"""
import sys
import argparse

from core.bootstrap import ensure_amb_env
ensure_amb_env()

from stitch_client import get_screen, Colors, log, log_error

run_get_screen = get_screen


def main():
    p = argparse.ArgumentParser(description="Consulta detalhes e obtém o HTML de uma tela no Stitch.")
    p.add_argument("--screen-id", "-s", required=True, help="ID da tela.")
    p.add_argument("--output", "-o", help="Caminho do arquivo para salvar o HTML da tela.")
    args = p.parse_args()
    try:
        res = get_screen(screen_id=args.screen_id, output_file=args.output)
        log("STITCH", f"Detalhes da tela {args.screen_id} obtidos com sucesso.", Colors.GREEN)
        if res.get("title"):
            print(f"  • Título: {res['title']}")
        if res.get("screenshotUrl"):
            print(f"  • Screenshot: {res['screenshotUrl']}")
        if res.get("htmlCode"):
            print(f"  • DOM HTML: {len(res['htmlCode'])} caracteres")
        if args.output:
            print(f"  • HTML salvo em: {args.output}")
    except Exception as e:
        log_error("STITCH", str(e))
        sys.exit(1)


if __name__ == "__main__":
    main()
