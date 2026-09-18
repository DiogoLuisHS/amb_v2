import pytest
from unittest.mock import patch

# 1. Importações Limpas via core e workspace
from amb_cli.core import Colors as CoreColors
from amb_cli.core.exceptions import AmbError as CoreAmbError
from amb_cli.workspace.rules_manager import RulesManager as WorkspaceRulesManager

# 2. Importações Legadas via config
from amb_cli.config.config import Colors as LegacyColors
from amb_cli.config.config import AmbError as LegacyAmbError
from amb_cli.config.rules_manager import RulesManager as LegacyRulesManager

def test_config_facade_identities():
    """Valida que a fachada (config) reexporta exatamente os mesmos símbolos do core e workspace."""
    assert LegacyColors is CoreColors
    assert LegacyAmbError is CoreAmbError
    assert LegacyRulesManager is WorkspaceRulesManager

def test_get_env_fallback():
    """Valida o fallback de get_env implementado na fachada (config)."""
    from amb_cli.config.config import get_env

    with patch("amb_cli.config.config.core_get_env", return_value=None):
        with patch("amb_cli.config.config.load_project_json", return_value={"TEST_KEY": "fallback_val"}):
            assert get_env("TEST_KEY") == "fallback_val"

    with patch("amb_cli.config.config.core_get_env", return_value="core_val"):
        assert get_env("TEST_KEY") == "core_val"
