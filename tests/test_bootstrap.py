# -*- coding: utf-8 -*-
"""Unit tests for config/bootstrap.py and amb_bootstrap.py."""

import sys
from pathlib import Path

# Garante que o diretório raiz está no path para carregar o módulo em teste
_root = Path(__file__).resolve().parent.parent
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))

from config.bootstrap import get_amb_root, ensure_amb_env, add_to_sys_path, CANONICAL_SUBMODULES


def test_get_amb_root():
    root = get_amb_root()
    assert root.exists()
    assert (root / "pyproject.toml").exists() or (root / "cli.py").exists()


def test_ensure_amb_env():
    root = ensure_amb_env()
    assert root.exists()
    assert str(root) in sys.path
    
    # Verifica se os submódulos que existem fisicamente foram adicionados ao sys.path
    for sub in CANONICAL_SUBMODULES:
        parts = sub.replace("\\", "/").split("/")
        sub_dir = root.joinpath(*parts)
        if sub_dir.exists():
            assert str(sub_dir) in sys.path


def test_add_to_sys_path():
    root = get_amb_root()
    # Adicionar caminho existente
    config_dir = root / "config"
    result = add_to_sys_path(config_dir)
    assert str(config_dir) in sys.path
    
    # Adicionar novamente deve retornar False (idempotente)
    assert add_to_sys_path(config_dir) is False


def test_amb_bootstrap_import():
    import amb_bootstrap
    assert hasattr(amb_bootstrap, "ensure_amb_env")
    assert hasattr(amb_bootstrap, "get_amb_root")
