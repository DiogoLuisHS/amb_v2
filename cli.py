#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🚀 AMB_V2 - Wrapper Raiz de Compatibilidade
Permite a execução direta via `python cli.py` delegando para o pacote `amb_cli`.
"""
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent
PKG_DIR = ROOT_DIR / "amb_cli"
for p in [str(PKG_DIR), str(ROOT_DIR)]:
    if p not in sys.path:
        sys.path.insert(0, p)

from amb_cli.core.bootstrap import ensure_amb_env
ensure_amb_env()

from amb_cli.cli import main

if __name__ == "__main__":
    sys.exit(main())
