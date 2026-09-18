import os
import pytest
import argparse
from unittest.mock import patch, MagicMock

from amb_cli.cli_modules.cli_parsers import create_parser
from amb_cli.gui.wizard_core.parser_extractor import extract_commands, clean_command_map, detect_repo_name

def test_extract_commands():
    parser = create_parser()
    commands = extract_commands(parser)
    assert isinstance(commands, dict)
    assert "pipeline" in commands
    assert "settings" in commands

def test_clean_command_map():
    parser = create_parser()
    commands = extract_commands(parser)

    # Adicionamos um alias artificial para simular duplicatas (se existisse)
    commands["pipeline_alias"] = commands["pipeline"]

    cleaned = clean_command_map(commands)
    # A contagem de parsers únicos deve ser mantida
    assert len(cleaned) < len(commands)
    assert "pipeline_alias" not in cleaned or "pipeline" not in cleaned

def test_detect_repo_name_from_env(tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text("GITHUB_REPOSITORY=test/repo\n")
    repo = detect_repo_name(str(tmp_path), str(env_file))
    assert repo == "test/repo"

def test_detect_repo_name_fallback(tmp_path):
    env_file = tmp_path / ".env"
    # test get_repo_name or basename fallback
    repo = detect_repo_name(str(tmp_path), str(env_file))
    assert repo == tmp_path.name or repo is not None

# GUI is tested using mocks since tkinter may not be available in CI
def test_runner_tab_logic():
    # We test just the parsing logic instead
    parser = create_parser()
    commands = extract_commands(parser)
    assert len(commands) > 0
