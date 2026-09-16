#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""🎨 Stitch Tool: generate_variants (Facade)"""
import sys
import argparse

from config.bootstrap import ensure_amb_env
ensure_amb_env()

from stitch_client import generate_variants, Colors, log, log_error

run_generate_variants = generate_variants


def main():
    p = argparse.ArgumentParser(description="Gera variantes visuais no Google Stitch.")
    p.add_argument("--screen-id", "-s", required=True, help="ID da tela base.")
    p.add_argument("--prompt", "-p", required=True, help="Instruções de variação visual fornecidas pelo projeto/usuário.")
    p.add_argument("--count", "-c", type=int, default=3, help="Quantidade de variantes (padrão: 3).")
    p.add_argument("--device", "-d", choices=["DESKTOP", "MOBILE", "TABLET", "AGNOSTIC"], default=None, help="Tipo de dispositivo alvo.")
    args = p.parse_args()
    try:
        res = generate_variants(screen_id=args.screen_id, prompt=args.prompt, count=args.count, device_type=args.device)
        log("STITCH", f"Variantes geradas com sucesso! ID: {res.get('screenId')}", Colors.GREEN)
        if res.get("screenshotUrl"):
            print(f"  • Screenshot: {res['screenshotUrl']}")
    except Exception as e:
        log_error("STITCH", str(e))
        sys.exit(1)


if __name__ == "__main__":
    main()
