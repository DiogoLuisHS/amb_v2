#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
⚡ AMB_V2 - Módulo de Compatibilidade Reversa de Bootstrap (F1-M1)
Este arquivo garante que importações legadas de `amb_cli.config.bootstrap`
continuem funcionando. A lógica real foi movida para `amb_cli.core.bootstrap`.
"""

from amb_cli.core.bootstrap import (
    get_amb_root,
    get_amb_package_dir,
    add_to_sys_path,
    ensure_amb_env,
    CANONICAL_SUBMODULES
)

__all__ = [
    "get_amb_root",
    "get_amb_package_dir",
    "add_to_sys_path",
    "ensure_amb_env",
    "CANONICAL_SUBMODULES"
]
