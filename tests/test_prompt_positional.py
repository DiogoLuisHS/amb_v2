import argparse
import sys
from unittest.mock import patch, MagicMock
import pytest

from amb_cli.cli_modules.cli_handlers import cmd_prompt


@patch("amb_cli.cli_modules.cli_handlers.sys.stdin.isatty", return_value=False)
@patch("integrations.antigravity.tools.synthesize_prompt.run_synthesize_prompt")
def test_cmd_prompt_with_positional_idea(mock_run_synthesize_prompt, mock_isatty):
    args = argparse.Namespace(idea="Minha Feature", synthesize=None, image=None)
    cmd_prompt(args)

    mock_run_synthesize_prompt.assert_called_once_with(
        raw_idea="Minha Feature",
        role="general",
        output_file=None,
        image_path=None,
        queue=False
    )
    assert getattr(args, "agy_cmd", None) is None


@patch("amb_cli.cli_modules.cli_handlers.sys.stdin.isatty", return_value=False)
@patch("integrations.antigravity.tools.synthesize_prompt.run_synthesize_prompt")
def test_cmd_prompt_with_synthesize_flag_retrocompatibility(mock_run_synthesize_prompt, mock_isatty):
    args = argparse.Namespace(idea=None, synthesize="Minha Feature Antiga", image=None)
    cmd_prompt(args)

    mock_run_synthesize_prompt.assert_called_once_with(
        raw_idea="Minha Feature Antiga",
        role="general",
        output_file=None,
        image_path=None,
        queue=False
    )
    assert getattr(args, "agy_cmd", None) is None


@patch("amb_cli.cli_modules.cli_handlers.sys.stdin.isatty", return_value=False)
@patch("integrations.antigravity.tools.synthesize_prompt.run_synthesize_prompt")
def test_cmd_prompt_with_image_flag(mock_run_synthesize_prompt, mock_isatty):
    args = argparse.Namespace(idea=None, synthesize=None, image="mockup.png")
    cmd_prompt(args)

    mock_run_synthesize_prompt.assert_called_once_with(
        raw_idea=None,
        role="general",
        output_file=None,
        image_path="mockup.png",
        queue=False
    )
    assert getattr(args, "agy_cmd", None) is None


@patch("amb_cli.cli_modules.cli_handlers.sys.stdin.isatty", return_value=True)
@patch("builtins.input", return_value="Minha Ideia Interativa")
@patch("integrations.antigravity.tools.synthesize_prompt.run_synthesize_prompt")
def test_cmd_prompt_interactive(mock_run_synthesize_prompt, mock_input, mock_isatty):
    args = argparse.Namespace(idea=None, synthesize=None, image=None)
    cmd_prompt(args)

    mock_run_synthesize_prompt.assert_called_once_with(
        raw_idea="Minha Ideia Interativa",
        role="general",
        output_file=None,
        image_path=None,
        queue=False
    )
    assert getattr(args, "agy_cmd", None) is None


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
