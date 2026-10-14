import pytest
from unittest.mock import patch, MagicMock
from amb_cli.cli_modules.cli_parsers import create_parser
from amb_cli.cli_modules.handlers_core.git_handler import handle_cmd_git

@pytest.fixture
def parser():
    return create_parser()

@patch("integrations.git.tools.pr_manager.run_pr_manager")
def test_amb_git_pr_default_list(mock_run, parser):
    """Garante que a execução de 'amb git pr' sem subcomando dispara a listagem de PRs abertos."""
    args = parser.parse_args(["git", "pr"])
    handle_cmd_git(args)
    mock_run.assert_called_once()
    assert mock_run.call_args[1]["action"] == "list"

@patch("integrations.git.tools.pr_manager.run_pr_manager")
def test_amb_git_pr_default_list_with_flags(mock_run, parser, capsys):
    """Garante suporte a flags combinadas como --no-drafts e --json."""
    args = parser.parse_args(["git", "pr", "--json", "--no-drafts"])
    mock_run.return_value = [{"number": 1, "title": "Test PR"}]

    handle_cmd_git(args)

    mock_run.assert_called_once()
    kwargs = mock_run.call_args[1]
    assert kwargs["action"] == "list"
    assert kwargs["include_drafts"] is False

    captured = capsys.readouterr()
    assert "Test PR" in captured.out
    assert "[\n" in captured.out # check JSON formatting

@patch("integrations.git.tools.pr_manager.run_pr_manager")
def test_amb_git_pr_explicit_list(mock_run, parser):
    """Garante a preservação da execução explícita de subcomandos como 'amb git pr list'."""
    args = parser.parse_args(["git", "pr", "list", "--json", "--no-drafts"])
    mock_run.return_value = [{"number": 1, "title": "Test PR"}]

    handle_cmd_git(args)

    mock_run.assert_called_once()
    kwargs = mock_run.call_args[1]
    assert kwargs["action"] == "list"
    assert kwargs["include_drafts"] is False

@patch("integrations.git.tools.pr_manager.run_pr_manager")
def test_amb_git_pr_explicit_create(mock_run, parser):
    """Garante a preservação da execução explícita de outros subcomandos como 'amb git pr create'."""
    args = parser.parse_args(["git", "pr", "create", "--title", "New PR", "--draft"])

    handle_cmd_git(args)

    mock_run.assert_called_once()
    kwargs = mock_run.call_args[1]
    assert kwargs["action"] == "create"
    assert kwargs["title"] == "New PR"
    assert kwargs["draft"] is True
