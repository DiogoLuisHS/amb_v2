#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""🎨 Stitch Tool: sync_design_system (Facade)"""
import sys
import argparse

from core.bootstrap import ensure_amb_env
ensure_amb_env()

from stitch_client import sync_design_system, Colors, log, log_error

run_sync_design_system = sync_design_system


def main():
    p = argparse.ArgumentParser(description="Sincroniza design tokens do design.md com o Design System do Stitch.")
    p.add_argument("--file", "-f", help="Caminho do arquivo design.md.")
    args = p.parse_args()
    try:
        res = sync_design_system(design_md_path=args.file)
        log("STITCH", "✅ Design System sincronizado com sucesso!", Colors.GREEN)
    except Exception as e:
        log_error("STITCH", str(e))
        sys.exit(1)


if __name__ == "__main__":
    main()
