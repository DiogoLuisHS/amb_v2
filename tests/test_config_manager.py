import os
import pytest
from unittest.mock import patch, MagicMock
from amb_cli.core.config_manager import ConfigManager
from amb_cli.core.exceptions import ConfigurationError


@pytest.fixture(autouse=True)
def reset_config_manager():
    """Ensure ConfigManager is reset before and after each test."""
    ConfigManager._instance = None
    yield
    ConfigManager._instance = None


def test_singleton_pattern():
    """Testa se get_instance sempre retorna a mesma referência de memória."""
    instance1 = ConfigManager.get_instance()
    instance2 = ConfigManager.get_instance()
    assert instance1 is instance2


@patch("amb_cli.core.config_manager.load_env_file")
@patch("amb_cli.core.config_manager.load_project_json")
def test_reload_loads_correctly(mock_load_proj, mock_load_env):
    """Testa o comportamento de reload preenchendo os caches corretamente."""
    mock_load_proj.return_value = {"project_key": "project_value"}
    os.environ["ENV_KEY"] = "env_value"

    config = ConfigManager.get_instance()

    assert config.get("ENV_KEY") == "env_value"
    assert config.get("project_key") == "project_value"

    mock_load_env.assert_called_once()
    mock_load_proj.assert_called_once()


@patch("amb_cli.core.config_manager.load_env_file")
@patch("amb_cli.core.config_manager.load_project_json")
def test_cache_efficiency(mock_load_proj, mock_load_env):
    """Testa se chamadas subsequentes ao get não disparam leitura em disco."""
    mock_load_proj.return_value = {"key": "val"}

    config = ConfigManager.get_instance()

    val1 = config.get("key")
    val2 = config.get("key")
    val3 = config.get("key")

    assert val1 == "val"
    assert val2 == "val"
    assert val3 == "val"

    # Even after 3 get() calls, it should only be called once when instantiated/reloaded
    mock_load_proj.assert_called_once()
    mock_load_env.assert_called_once()


@patch("amb_cli.core.config_manager.load_env_file")
@patch("amb_cli.core.config_manager.load_project_json")
def test_require_success(mock_load_proj, mock_load_env):
    """Testa se require retorna o valor esperado caso exista."""
    os.environ["REQ_KEY"] = "existing"
    config = ConfigManager.get_instance()

    val = config.require("REQ_KEY")
    assert val == "existing"


@patch("amb_cli.core.config_manager.load_env_file")
@patch("amb_cli.core.config_manager.load_project_json")
def test_require_failure_raises_error(mock_load_proj, mock_load_env):
    """Testa se require lança ConfigurationError quando não acha o valor."""
    config = ConfigManager.get_instance()

    with pytest.raises(ConfigurationError, match="Variável mandatória ausente: 'MISSING_KEY'"):
        config.require("MISSING_KEY")


@patch("amb_cli.core.config_manager.load_env_file")
@patch("amb_cli.core.config_manager.load_project_json")
def test_priority(mock_load_proj, mock_load_env):
    """Testa se env tem prioridade sobre project json."""
    os.environ["CONFLICT"] = "env_wins"
    mock_load_proj.return_value = {"CONFLICT": "proj_loses"}

    config = ConfigManager.get_instance()

    assert config.get("CONFLICT") == "env_wins"
