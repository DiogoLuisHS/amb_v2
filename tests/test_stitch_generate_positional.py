import pytest
from unittest.mock import MagicMock, patch
import os
import argparse
from amb_cli.cli_modules.handlers_core.stitch_handler import handle_cmd_stitch

@pytest.fixture
def mock_stitch_client():
    with patch("integrations.stitch.stitch_client.StitchClient") as mock_client_class:
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        yield mock_client

@pytest.fixture
def mock_log_error():
    with patch("core.log_error") as mock_log:
        yield mock_log

def test_stitch_generate_positional_string(mock_stitch_client):
    """Test generating passing descriptive string directly in positional argument."""
    mock_stitch_client.generate_screen.return_value = {"screenId": "s_123"}

    args = argparse.Namespace(
        stitch_cmd="generate",
        prompt="Dashboard Dark Mode com cards de KPI",
        prompt_flag=None,
        device=None,
        output=None,
        json=False
    )

    handle_cmd_stitch(args)

    mock_stitch_client.generate_screen.assert_called_once_with(
        prompt="Dashboard Dark Mode com cards de KPI",
        device_type=None,
        output_file=None
    )

def test_stitch_generate_positional_file(mock_stitch_client, tmp_path):
    """Test generating passing existing .md file path with auto-read."""
    mock_stitch_client.generate_screen.return_value = {"screenId": "s_456"}

    prompt_file = tmp_path / "specs_dashboard_ui.md"
    prompt_file.write_text("Conteúdo do arquivo de prompt com utf-8", encoding="utf-8")

    args = argparse.Namespace(
        stitch_cmd="generate",
        prompt=str(prompt_file),
        prompt_flag=None,
        device=None,
        output=None,
        json=False
    )

    handle_cmd_stitch(args)

    mock_stitch_client.generate_screen.assert_called_once_with(
        prompt="Conteúdo do arquivo de prompt com utf-8",
        device_type=None,
        output_file=None
    )

def test_stitch_generate_missing_prompt(mock_stitch_client):
    """Test graceful handling when no prompt is provided."""

    args = argparse.Namespace(
        stitch_cmd="generate",
        prompt=None,
        prompt_flag=None,
        device=None,
        output=None,
        json=False
    )

    with patch("core.log_error") as mock_log_error:
        handle_cmd_stitch(args)

        mock_log_error.assert_called_once_with("O argumento posicional 'prompt' ou a flag '--prompt' são obrigatórios.")
        mock_stitch_client.generate_screen.assert_not_called()

def test_stitch_generate_with_flag(mock_stitch_client):
    """Test generating with the --prompt flag still works."""
    mock_stitch_client.generate_screen.return_value = {"screenId": "s_789"}

    args = argparse.Namespace(
        stitch_cmd="generate",
        prompt=None,
        prompt_flag="Prompt pela flag",
        device=None,
        output=None,
        json=False
    )

    handle_cmd_stitch(args)

    mock_stitch_client.generate_screen.assert_called_once_with(
        prompt="Prompt pela flag",
        device_type=None,
        output_file=None
    )
