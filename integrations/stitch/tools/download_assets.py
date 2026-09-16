#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""🎨 Stitch Tool: download_assets (Facade)"""
import sys
import argparse

from config.bootstrap import ensure_amb_env
ensure_amb_env()

from stitch_client import download_assets, Colors, log, log_error

run_download_assets = download_assets


def main():
    p = argparse.ArgumentParser(description="Baixa telas e assets do projeto Stitch para um diretório local.")
    p.add_argument("--output", "-o", default="./stitch_assets", help="Diretório de destino dos assets.")
    p.add_argument("--project-id", help="ID do projeto Stitch (padrão: lê do .env).")
    args = p.parse_args()
    try:
        res = download_assets(output_dir=args.output, project_id=args.project_id)
        log("STITCH", f"Assets baixados com sucesso para: {args.output}", Colors.GREEN)
    except Exception as e:
        log_error("STITCH", str(e))
        sys.exit(1)


if __name__ == "__main__":
    main()
