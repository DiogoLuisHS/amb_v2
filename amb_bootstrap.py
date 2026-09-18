#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
⚡ AMB_V2 - Shim de Compatibilidade para Bootstrap
Redireciona para o bootstrap canônico dentro de amb_cli.
"""
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent
PKG_DIR = ROOT_DIR / "amb_cli"
for p in [str(PKG_DIR), str(ROOT_DIR)]:
    if p not in sys.path:
        sys.path.insert(0, p)

from amb_cli.core.bootstrap import (
    ensure_amb_env,
    get_amb_root,
    get_amb_package_dir,
    add_to_sys_path,
    CANONICAL_SUBMODULES,
)

ensure_amb_env()

__all__ = [
    "ensure_amb_env",
    "get_amb_root",
    "get_amb_package_dir",
    "add_to_sys_path",
    "CANONICAL_SUBMODULES",
]
