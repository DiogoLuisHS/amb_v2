import os
import pytest
import tempfile
from unittest.mock import MagicMock
from cli_modules.handlers_core.antigravity_handler import handle_cmd_antigravity

class MockArgs:
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)

def test_antigravity_run_inline_string(monkeypatch):
    """Test inference execution with inline string."""
    mock_generate = MagicMock(return_value="Mocked response")
    monkeypatch.setattr(
        "integrations.antigravity.antigravity_client.AntigravityClient.generate_text",
        mock_generate
    )

    args = MockArgs(
        agy_cmd="run",
        prompt="Explain microservices",
        system=None,
        model=None,
        temperature=0.2,
        output=None
    )

    handle_cmd_antigravity(args)

    mock_generate.assert_called_once_with(
        prompt="Explain microservices",
        system_instruction=None,
        temperature=0.2
    )

def test_antigravity_run_file_prompt(monkeypatch):
    """Test inference execution passing an existing .md file for automatic reading."""
    mock_generate = MagicMock(return_value="Mocked response")
    monkeypatch.setattr(
        "integrations.antigravity.antigravity_client.AntigravityClient.generate_text",
        mock_generate
    )

    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
        f.write("Complex prompt from file\n")
        f_name = f.name

    try:
        args = MockArgs(
            agy_cmd="run",
            prompt=f_name,
            system=None,
            model=None,
            temperature=0.2,
            output=None
        )

        handle_cmd_antigravity(args)

        mock_generate.assert_called_once_with(
            prompt="Complex prompt from file",
            system_instruction=None,
            temperature=0.2
        )
    finally:
        if os.path.exists(f_name):
            os.remove(f_name)

def test_antigravity_run_file_system(monkeypatch):
    """Test file reading support for the --system (-s) flag."""
    mock_generate = MagicMock(return_value="Mocked response")
    monkeypatch.setattr(
        "integrations.antigravity.antigravity_client.AntigravityClient.generate_text",
        mock_generate
    )

    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f_system:
        f_system.write("You are a helpful assistant.\n")
        f_sys_name = f_system.name

    try:
        args = MockArgs(
            agy_cmd="run",
            prompt="Simple prompt",
            system=f_sys_name,
            model=None,
            temperature=0.2,
            output=None
        )

        handle_cmd_antigravity(args)

        mock_generate.assert_called_once_with(
            prompt="Simple prompt",
            system_instruction="You are a helpful assistant.",
            temperature=0.2
        )
    finally:
        if os.path.exists(f_sys_name):
            os.remove(f_sys_name)

def test_antigravity_run_missing_prompt(monkeypatch, capsys):
    """Test graceful handling when the prompt argument is omitted/empty."""
    mock_generate = MagicMock()
    monkeypatch.setattr(
        "integrations.antigravity.antigravity_client.AntigravityClient.generate_text",
        mock_generate
    )

    args = MockArgs(
        agy_cmd="run",
        prompt="",
        system=None,
        model=None,
        temperature=0.2,
        output=None
    )

    handle_cmd_antigravity(args)

    mock_generate.assert_not_called()

    # We can check that the log_error printed something to output
    captured = capsys.readouterr()
    out = captured.err or captured.out
    assert "Nenhum prompt fornecido" in out
