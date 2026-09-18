#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
⚡ AMB_V2 - Módulo Central de Bootstrap de Ambiente (F1-M1)
Responsabilidade Única: Garantir que o diretório raiz do AMB_V2 e todos os
seus submódulos estejam no sys.path de forma centralizada, determinística e idempotente.
"""

import os
import sys
from pathlib import Path
from typing import List, Optional, Union

# Auto-injeção imediata de sys.path no nível do módulo
_bootstrap_file = Path(__file__).resolve()
_pkg_candidate = _bootstrap_file.parent.parent
_repo_candidate = _pkg_candidate.parent
for _candidate_path in [_pkg_candidate, _repo_candidate]:
    _c_str = str(_candidate_path)
    if _candidate_path.exists() and _c_str not in sys.path:
        sys.path.insert(0, _c_str)

# Lista canônica de submódulos do AMB_V2 que devem estar disponíveis para importação
CANONICAL_SUBMODULES: List[str] = [
    "core",
    "core/exceptions",
    "core/logger",
    "core/env",
    "core/bootstrap",
    "workspace",
    "workspace/project_context",
    "workspace/setup",
    "config",
    "config/config_core",
    "config/setup_modules",
    "agents",
    "agents/auto_reply_core",
    "agents/loop_core",
    "architecture",
    "architecture/context_core",
    "pipeline",
    "pipeline/pipeline_core",
    "gui",
    "gui/wizard_core",
    "integrations",
    "integrations/common",
    "integrations/git",
    "integrations/git/tools",
    "integrations/jules",
    "integrations/jules/tools",
    "integrations/stitch",
    "integrations/stitch/tools",
    "integrations/antigravity",
    "integrations/antigravity/tools",
    "cli_modules",
    "cli_modules/handlers_core",
]

_ROOT_CACHE: Optional[Path] = None
_BOOTSTRAPPED: bool = False


def get_amb_root() -> Path:
    """Localiza a raiz do repositório AMB_V2 de forma determinística."""
    global _ROOT_CACHE
    if _ROOT_CACHE is not None:
        return _ROOT_CACHE

    current_file = Path(__file__).resolve()

    # 1. Âncora direta: se este arquivo reside em amb_cli/core/bootstrap.py ou amb_cli/config/bootstrap.py
    candidate_repo = current_file.parent.parent.parent
    if (candidate_repo / "pyproject.toml").exists() or (candidate_repo / ".git").exists():
        _ROOT_CACHE = candidate_repo
        return _ROOT_CACHE

    # 2. Âncora legado: se este arquivo reside em core/bootstrap.py
    candidate = current_file.parent.parent
    if (candidate / "pyproject.toml").exists() or (candidate / "cli.py").exists():
        _ROOT_CACHE = candidate
        return _ROOT_CACHE

    # 3. Busca ascendente por marcos de projeto
    curr = current_file.parent
    while curr != curr.parent:
        if (curr / "pyproject.toml").exists() and ((curr / ".git").exists() or (curr / "amb_cli").is_dir()):
            _ROOT_CACHE = curr
            return _ROOT_CACHE
        curr = curr.parent

    # 4. Fallback defensivo
    _ROOT_CACHE = candidate_repo if (candidate_repo / "amb_cli").is_dir() else current_file.parent.parent
    return _ROOT_CACHE


def get_amb_package_dir() -> Path:
    """Retorna o diretório do pacote amb_cli onde residem os módulos."""
    root = get_amb_root()
    pkg = root / "amb_cli"
    if pkg.is_dir():
        return pkg
    return root


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
    """Configura o sys.path com a raiz do AMB_V2, o pacote amb_cli e todos os seus submódulos canônicos.

    Operação idempotente. Se já executada, apenas processa subdiretórios adicionais,
    a menos que force_reload=True.
    """
    global _BOOTSTRAPPED
    amb_root = get_amb_root()
    pkg_dir = get_amb_package_dir()
    amb_root_str = str(amb_root)
    pkg_dir_str = str(pkg_dir)

    # Garante que a raiz do AMB_V2 e o pacote amb_cli estão no sys.path
    if amb_root_str not in sys.path:
        sys.path.insert(0, amb_root_str)
    if pkg_dir_str != amb_root_str and pkg_dir_str not in sys.path:
        sys.path.insert(0, pkg_dir_str)

    if not _BOOTSTRAPPED or force_reload:
        for sub in CANONICAL_SUBMODULES:
            parts = sub.replace("\\", "/").split("/")
            sub_path = pkg_dir.joinpath(*parts)
            if not sub_path.exists():
                sub_path = amb_root.joinpath(*parts)
            if sub_path.exists():
                add_to_sys_path(sub_path, prepend=False)
        _BOOTSTRAPPED = True

    if additional_subdirs:
        for extra in additional_subdirs:
            parts = extra.replace("\\", "/").split("/")
            extra_path = pkg_dir.joinpath(*parts)
            if not extra_path.exists():
                extra_path = amb_root.joinpath(*parts)
            if extra_path.exists():
                add_to_sys_path(extra_path, prepend=False)

    return amb_root
