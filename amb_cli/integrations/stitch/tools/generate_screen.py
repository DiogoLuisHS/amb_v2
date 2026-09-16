#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""🎨 Stitch Tool: generate_screen (Facade)"""
import sys
import argparse

from config.bootstrap import ensure_amb_env
ensure_amb_env()

from stitch_client import generate_screen, Colors, log, log_error

run_generate_screen = generate_screen


def main():
    p = argparse.ArgumentParser(description="Gera uma nova tela visual no Google Stitch.")
    p.add_argument("--prompt", "-p", required=True, help="Descrição visual da tela.")
    p.add_argument("--device", "-d", choices=["DESKTOP", "MOBILE", "TABLET", "AGNOSTIC"], default=None, help="Tipo de dispositivo (DESKTOP, MOBILE, TABLET, AGNOSTIC; padrão: lê do projeto ou .env).")
    p.add_argument("--model", "-m", default=None, help="Modelo visual de geração (ex: GEMINI_3_FLASH, GEMINI_3_1_PRO; padrão: Stitch SDK default).")
    p.add_argument("--output", "-o", help="Caminho do arquivo para salvar o HTML da tela gerada.")
    args = p.parse_args()
    try:
        res = generate_screen(prompt=args.prompt, device_type=args.device, model_id=args.model, output_file=args.output)
        log("STITCH", f"Tela gerada com sucesso! ID: {res.get('screenId')}", Colors.GREEN)
        if res.get("screenshotUrl"):
            print(f"  • Screenshot: {res['screenshotUrl']}")
        if args.output:
            print(f"  • HTML salvo em: {args.output}")
    except Exception as e:
        log_error("STITCH", str(e))
        sys.exit(1)


if __name__ == "__main__":
    main()
