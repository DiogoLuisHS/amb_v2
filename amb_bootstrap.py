#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
⚡ AMB_V2 - Atalho Global de Bootstrap de Ambiente
Permite inicialização imediata via:
    import amb_bootstrap
ou:
    from amb_bootstrap import ensure_amb_env, get_amb_root
"""

from config.bootstrap import ensure_amb_env, get_amb_root, add_to_sys_path, CANONICAL_SUBMODULES

# Executa automaticamente o bootstrap padrão no momento da importação
ensure_amb_env()

__all__ = [
    "ensure_amb_env",
    "get_amb_root",
    "add_to_sys_path",
    "CANONICAL_SUBMODULES",
]
