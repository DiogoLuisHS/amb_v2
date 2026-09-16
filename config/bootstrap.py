#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
⚡ AMB_V2 - Módulo Central de Bootstrap de Ambiente (F1-M1)
Localização: amb_v2/config/bootstrap.py
Responsabilidade Única: Garantir que o diretório raiz do AMB_V2 e todos os
seus submódulos estejam no sys.path de forma centralizada, determinística e idempotente.
"""

import os
import sys
from pathlib import Path
from typing import List, Optional, Union

# Lista canônica de submódulos do AMB_V2 que devem estar disponíveis para importação
CANONICAL_SUBMODULES: List[str] = [
    "config",
    "config/setup_modules",
    "agents",
    "agents/auto_reply_core",
    "architecture",
    "pipeline",
    "gui",
    "integrations",
    "integrations/common",
    "integrations/git",
    "integrations/jules",
    "integrations/jules/tools",
    "integrations/stitch",
    "integrations/stitch/tools",
    "integrations/antigravity",
    "integrations/antigravity/tools",
    "cli_modules",
]

_ROOT_CACHE: Optional[Path] = None
_BOOTSTRAPPED: bool = False


def get_amb_root() -> Path:
    """Localiza a raiz do AMB_V2 de forma determinística."""
    global _ROOT_CACHE
    if _ROOT_CACHE is not None:
        return _ROOT_CACHE

    # 1. Âncora direta: este arquivo reside em amb_v2/config/bootstrap.py
    current_file = Path(__file__).resolve()
    candidate = current_file.parent.parent
    if (candidate / "pyproject.toml").exists() or (candidate / "cli.py").exists():
        _ROOT_CACHE = candidate
        return _ROOT_CACHE

    # 2. Busca ascendente por marcos de projeto
    curr = current_file.parent
    while curr != curr.parent:
        if (curr / "pyproject.toml").exists() and (curr / "cli.py").exists():
            _ROOT_CACHE = curr
            return _ROOT_CACHE
        curr = curr.parent

    # 3. Fallback defensivo: assume o diretório pai de config
    _ROOT_CACHE = current_file.parent.parent
    return _ROOT_CACHE


def add_to_sys_path(path: Union[str, Path], prepend: bool = True) -> bool:
    """Adiciona um caminho ao sys.path de forma idempotente.
    
    Retorna True se o caminho foi inserido, False se já existia ou é inválido.
    """
    p_str = str(Path(path).resolve())
    if os.path.exists(p_str) and p_str not in sys.path:
        if prepend:
            sys.path.insert(0, p_str)
        else:
            sys.path.append(p_str)
        return True
    return False


def ensure_amb_env(
    additional_subdirs: Optional[List[str]] = None,
    force_reload: bool = False
) -> Path:
    """Configura o sys.path com a raiz do AMB_V2 e todos os seus submódulos canônicos.
    
    Operação idempotente. Se já executada, apenas processa subdiretórios adicionais,
    a menos que force_reload=True.
    """
    global _BOOTSTRAPPED
    amb_root = get_amb_root()
    amb_root_str = str(amb_root)

    # Garante que a própria raiz do AMB_V2 está no sys.path
    if amb_root_str not in sys.path:
        sys.path.insert(0, amb_root_str)

    if not _BOOTSTRAPPED or force_reload:
        for sub in CANONICAL_SUBMODULES:
            parts = sub.replace("\\", "/").split("/")
            sub_path = amb_root.joinpath(*parts)
            if sub_path.exists():
                add_to_sys_path(sub_path, prepend=False)
        _BOOTSTRAPPED = True

    if additional_subdirs:
        for extra in additional_subdirs:
            parts = extra.replace("\\", "/").split("/")
            extra_path = amb_root.joinpath(*parts)
            if extra_path.exists():
                add_to_sys_path(extra_path, prepend=False)

    return amb_root
