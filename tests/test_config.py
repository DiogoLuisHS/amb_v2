import os
import pytest
from unittest.mock import patch, mock_open

from amb_cli.config.config import (
    Colors,
    AmbError,
    ConfigurationError,
    ApiExecutionError,
    find_repo_root,
    get_env,
    require_env,
    parse_design_tokens_from_text,
    get_design_system_config,
    main
)

def test_colors_ansi():
    assert Colors.HEADER == "\033[95m"
    assert Colors.BLUE == "\033[94m"
    assert Colors.CYAN == "\033[96m"
    assert Colors.GREEN == "\033[92m"
    assert Colors.YELLOW == "\033[93m"
    assert Colors.RED == "\033[91m"
    assert Colors.BOLD == "\033[1m"
    assert Colors.DIM == "\033[2m"
    assert Colors.RESET == "\033[0m"

def test_error_formatting():
    # AmbError with hint
    err = AmbError("Something went wrong", hint="Try doing X")
    assert "Something went wrong" in str(err)
    assert "👉 COMO RESOLVER: Try doing X" in str(err)
    assert err.message == "Something went wrong"
    assert err.hint == "Try doing X"

    # AmbError without hint
    err2 = AmbError("No hint here")
    assert "No hint here" in str(err2)
    assert "👉 COMO RESOLVER:" not in str(err2)
    assert err2.hint is None

    assert issubclass(ConfigurationError, AmbError)
    assert issubclass(ApiExecutionError, AmbError)

def test_find_repo_root(tmp_path):
    repo_dir = tmp_path / "my_repo"
    repo_dir.mkdir()
    (repo_dir / ".git").mkdir()

    sub_dir = repo_dir / "src" / "deep"
    sub_dir.mkdir(parents=True)

    assert find_repo_root(str(sub_dir)) == str(repo_dir)

@patch("amb_cli.core.env.os.environ", {"MY_VAR": "my_val"})
def test_get_env():
    assert get_env("MY_VAR") == "my_val"
    assert get_env("MISSING_VAR", "default_val") == "default_val"
    assert get_env("MISSING_VAR") is None

@patch("amb_cli.core.env.os.environ", {"REQ_VAR": "req_val"})
def test_require_env():
    assert require_env("REQ_VAR") == "req_val"
    with pytest.raises(ConfigurationError) as exc:
        require_env("MISSING_VAR", hint="Missing it")
    assert "Variável mandatória ausente: 'MISSING_VAR'" in str(exc.value)
    assert "Missing it" in str(exc.value)

def test_parse_design_tokens_from_text():
    md = """
    # Design
    primaryColor: #123456
    colorMode: DARK
    font: SORA
    roundness: FULL
    """
    tokens = parse_design_tokens_from_text(md)
    assert tokens.get("customColor") == "#123456"
    assert tokens.get("colorMode") == "DARK"
    assert tokens.get("headlineFont") == "SORA"
    assert tokens.get("bodyFont") == "SORA"
    assert tokens.get("roundness") == "ROUND_FULL"

def test_parse_design_tokens_from_text_empty():
    assert parse_design_tokens_from_text("") == {}

@patch("amb_cli.workspace.design_tokens.os.path.exists")
def test_get_design_system_config(mock_exists):
    with patch("amb_cli.workspace.project_context.find_repo_root") as mock_find:
        with patch("amb_cli.workspace.project_context.load_project_json") as mock_load:
            mock_find.return_value = "/fake/repo"
            mock_load.return_value = {"design_system": {"displayName": "My System"}}
            mock_exists.return_value = False # no design.md

            cfg = get_design_system_config()
            assert cfg.get("displayName") == "My System"

@patch("amb_cli.config.config.find_repo_root")
@patch("amb_cli.config.config.load_project_json")
def test_main_as_json(mock_load, mock_find):
    mock_find.return_value = "/fake/repo"
    mock_load.return_value = {}
    report = main(as_json=True)
    assert "root" in report
    assert report["root"] == "/fake/repo"
    assert "keys" in report
    assert "git" in report
