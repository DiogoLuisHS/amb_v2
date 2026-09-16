# -*- coding: utf-8 -*-
"""
Pytest configuration and environment bootstrap for AMB_V2 test suite.
"""
import sys
from pathlib import Path

# Garante que a raiz do repositório e o diretório amb_cli estão no sys.path
ROOT_DIR = Path(__file__).resolve().parent.parent
PKG_DIR = ROOT_DIR / "amb_cli"

for p in [str(ROOT_DIR), str(PKG_DIR)]:
    if p not in sys.path:
        sys.path.insert(0, p)

from amb_cli.config.bootstrap import ensure_amb_env

ensure_amb_env()
