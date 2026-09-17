# -*- coding: utf-8 -*-
"""Unit tests for config/bootstrap.py and amb_bootstrap.py."""

import sys
from pathlib import Path

# Garante que o diretório raiz está no path para carregar o módulo em teste
_root = Path(__file__).resolve().parent.parent
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))

from config.bootstrap import get_amb_root, get_amb_package_dir, ensure_amb_env, add_to_sys_path, CANONICAL_SUBMODULES


def test_get_amb_root():
    root = get_amb_root()
    assert root.exists()
    assert (root / "pyproject.toml").exists() or (root / "cli.py").exists()


def test_ensure_amb_env():
    root = ensure_amb_env()
    assert root.exists()
    assert str(root) in sys.path
    
    pkg_dir = get_amb_package_dir()
    # Verifica se os submódulos que existem fisicamente foram adicionados ao sys.path
    for sub in CANONICAL_SUBMODULES:
        parts = sub.replace("\\", "/").split("/")
        sub_dir = pkg_dir.joinpath(*parts)
        if not sub_dir.exists():
            sub_dir = root.joinpath(*parts)
        if sub_dir.exists():
            assert str(sub_dir) in sys.path


def test_canonical_submodules_list():
    expected_submodules = [
        "config",
        "config/config_core",
        "config/setup_modules",
        "agents",
        "agents/auto_reply_core",
        "agents/loop_core",
        "architecture",
        "architecture/context_core",
        "pipeline",
        "gui",
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
    assert CANONICAL_SUBMODULES == expected_submodules


def test_add_to_sys_path():
    pkg_dir = get_amb_package_dir()
    # Adicionar caminho existente
    config_dir = pkg_dir / "config"
    result = add_to_sys_path(config_dir)
    assert str(config_dir) in sys.path
    
    # Adicionar novamente deve retornar False (idempotente)
    assert add_to_sys_path(config_dir) is False



def test_amb_bootstrap_import():
    import amb_bootstrap
    assert hasattr(amb_bootstrap, "ensure_amb_env")
    assert hasattr(amb_bootstrap, "get_amb_root")


def test_migrated_sentinel_modules():
    """Valida se os módulos migrados do sentinela/monitor utilizam o bootstrap e carregam sem erros."""
    import cli_modules.alert_notifier as an
    import integrations.jules.jules_watcher as jw
    import agents.monitor as um

    assert hasattr(an, "notify_attention")
    assert hasattr(jw, "JulesWatcher")
    assert hasattr(um, "run_monitor")
    assert hasattr(um, "UnifiedMonitor")

