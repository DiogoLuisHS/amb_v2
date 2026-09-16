#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🚀 AMB_V2 - Sistema Unificado de Automação de Engenharia e Agentes Cognitivos
Pacote principal da CLI e módulos de orquestração.
"""
import sys
from pathlib import Path

__version__ = "2.3.0"
__author__ = "AMB_V2 Team"

# Garante que o diretório amb_cli e a raiz do repositório estejam em sys.path imediatamente
_amb_cli_dir = Path(__file__).resolve().parent
_amb_root_dir = _amb_cli_dir.parent

for _p in [str(_amb_cli_dir), str(_amb_root_dir)]:
    if _p not in sys.path:
        sys.path.insert(0, _p)

# Garante a inicialização automática do ambiente AMB_V2
from config.bootstrap import ensure_amb_env, get_amb_root, get_amb_package_dir

ensure_amb_env()

__all__ = [
    "__version__",
    "ensure_amb_env",
    "get_amb_root",
    "get_amb_package_dir",
]
