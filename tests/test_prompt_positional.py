import argparse
import sys
from unittest.mock import patch, MagicMock
import pytest

from amb_cli.cli_modules.cli_handlers import cmd_prompt


@patch("amb_cli.cli_modules.cli_handlers.sys.stdin.isatty", return_value=False)
@patch("cli_modules.handlers_core.antigravity_handler.handle_cmd_antigravity")
def test_cmd_prompt_with_positional_idea(mock_handle_cmd_antigravity, mock_isatty):
    args = argparse.Namespace(idea="Minha Feature", synthesize=None, image=None)
    cmd_prompt(args)

    mock_handle_cmd_antigravity.assert_called_once_with(args)
    assert args.agy_cmd == "prompt"
    assert args.idea == "Minha Feature"


@patch("amb_cli.cli_modules.cli_handlers.sys.stdin.isatty", return_value=False)
@patch("cli_modules.handlers_core.antigravity_handler.handle_cmd_antigravity")
def test_cmd_prompt_with_synthesize_flag_retrocompatibility(mock_handle_cmd_antigravity, mock_isatty):
    args = argparse.Namespace(idea=None, synthesize="Minha Feature Antiga", image=None)
    cmd_prompt(args)

    mock_handle_cmd_antigravity.assert_called_once_with(args)
    assert args.agy_cmd == "prompt"
    assert args.idea == "Minha Feature Antiga"


@patch("amb_cli.cli_modules.cli_handlers.sys.stdin.isatty", return_value=False)
@patch("cli_modules.handlers_core.antigravity_handler.handle_cmd_antigravity")
def test_cmd_prompt_with_image_flag(mock_handle_cmd_antigravity, mock_isatty):
    args = argparse.Namespace(idea=None, synthesize=None, image="mockup.png")
    cmd_prompt(args)

    mock_handle_cmd_antigravity.assert_called_once_with(args)
    assert args.agy_cmd == "prompt"
    assert args.idea is None


@patch("amb_cli.cli_modules.cli_handlers.sys.stdin.isatty", return_value=True)
@patch("builtins.input", return_value="Minha Ideia Interativa")
@patch("cli_modules.handlers_core.antigravity_handler.handle_cmd_antigravity")
def test_cmd_prompt_interactive(mock_handle_cmd_antigravity, mock_input, mock_isatty):
    args = argparse.Namespace(idea=None, synthesize=None, image=None)
    cmd_prompt(args)

    mock_handle_cmd_antigravity.assert_called_once_with(args)
    assert args.agy_cmd == "prompt"
    assert args.idea == "Minha Ideia Interativa"


@patch("amb_cli.cli_modules.cli_handlers.sys.stdin.isatty", return_value=False)
@patch("builtins.print")
def test_cmd_prompt_non_interactive_no_args_prints_usage(mock_print, mock_isatty):
    args = argparse.Namespace(idea=None, synthesize=None, image=None)
    cmd_prompt(args)

    assert any("Uso do comando 'amb prompt':" in call[0][0] for call in mock_print.call_args_list)


@patch("amb_cli.cli_modules.cli_handlers.sys.stdin.isatty", return_value=True)
@patch("builtins.input", return_value="")
@patch("builtins.print")
def test_cmd_prompt_interactive_no_input(mock_print, mock_input, mock_isatty):
    args = argparse.Namespace(idea=None, synthesize=None, image=None)
    cmd_prompt(args)

    assert any("Nenhuma ideia fornecida" in call[0][0] for call in mock_print.call_args_list)
