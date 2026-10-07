import os
import sys
import pytest
from unittest.mock import patch, MagicMock

from amb_cli.cli_modules.handlers_core.antigravity_handler import handle_cmd_antigravity
from amb_cli.cli_modules.handlers_core.hooks_handler import handle_cmd_hooks


class DummyArgs:
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)


@patch("workspace.get_rules_manager")
@patch("integrations.antigravity.tools.validate_architecture.run_validate_architecture")
def test_validate_staged_with_violation(mock_run, mock_get_rules_manager):
    # Setup mocks
    mock_mgr = MagicMock()
    mock_mgr.get_staged_files.return_value = ["file1.py"]
    mock_get_rules_manager.return_value = mock_mgr

    # Mock the return of validation to include a violation keyword
    mock_run.return_value = "Arquivo muito grande. Violação da regra de 300 linhas."

    args = DummyArgs(agy_cmd="validate", staged=True, file=None, json=False)

    with pytest.raises(SystemExit) as excinfo:
        handle_cmd_antigravity(args)

    assert excinfo.value.code == 1
    mock_mgr.get_staged_files.assert_called_once()
    mock_run.assert_called_once_with(file_path="file1.py")


@patch("workspace.get_rules_manager")
@patch("integrations.antigravity.tools.validate_architecture.run_validate_architecture")
def test_validate_staged_clean(mock_run, mock_get_rules_manager, capsys):
    # Setup mocks
    mock_mgr = MagicMock()
    mock_mgr.get_staged_files.return_value = []
    mock_get_rules_manager.return_value = mock_mgr

    args = DummyArgs(agy_cmd="validate", staged=True, file=None, json=False)

    # Should not raise SystemExit
    handle_cmd_antigravity(args)

    captured = capsys.readouterr()
    assert "Nenhum arquivo no stage" in captured.out
    mock_mgr.get_staged_files.assert_called_once()
    mock_run.assert_not_called()


@patch("amb_cli.cli_modules.handlers_core.hooks_handler.find_repo_root")
def test_hooks_install_creation(mock_find_repo_root, tmp_path, capsys):
    mock_find_repo_root.return_value = str(tmp_path)

    # Create mock .git directory
    git_dir = tmp_path / ".git"
    git_dir.mkdir()

    args = DummyArgs(hooks_cmd="install")

    handle_cmd_hooks(args)

    pre_commit_path = git_dir / "hooks" / "pre-commit"
    assert pre_commit_path.exists()

    with open(pre_commit_path, "r") as f:
        content = f.read()

    assert "#!/bin/sh" in content
    assert "python -m amb_cli.cli validate --staged" in content

    if os.name != "nt":
        # Check if executable
        assert os.access(pre_commit_path, os.X_OK)

    captured = capsys.readouterr()
    assert "instalado com sucesso" in captured.out
