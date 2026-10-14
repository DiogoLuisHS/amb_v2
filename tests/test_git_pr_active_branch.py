import pytest
from unittest.mock import patch

from amb_cli.integrations.git.tools.pr_manager import run_pr_manager
from core.exceptions import ApiExecutionError


@patch("amb_cli.integrations.git.tools.pr_manager.GitService")
def test_pr_get_auto_detect(MockGitService):
    mock_git = MockGitService.return_value
    mock_git.get_current_branch.return_value = "feature/auth"
    mock_git.list_open_prs.return_value = [{"number": 42, "headRefName": "feature/auth"}]

    run_pr_manager(action="get", pr_number=None)

    mock_git.get_pr.assert_called_once_with(pr_number=42, repo_name=None)
    mock_git.get_current_branch.assert_called_once()
    mock_git.list_open_prs.assert_called_once_with(repo_name=None)

@patch("amb_cli.integrations.git.tools.pr_manager.GitService")
def test_pr_merge_auto_detect(MockGitService):
    mock_git = MockGitService.return_value
    mock_git.get_current_branch.return_value = "feature/auth"
    mock_git.list_open_prs.return_value = [{"number": 99, "headRefName": "feature/auth"}]

    run_pr_manager(
        action="merge",
        pr_number=None,
        squash=True,
        delete_branch=True,
        admin=True
    )

    mock_git.merge_pr.assert_called_once_with(
        pr_number=99, repo_name=None, squash=True, delete_branch=True, admin=True
    )
    mock_git.get_current_branch.assert_called_once()
    mock_git.list_open_prs.assert_called_once_with(repo_name=None)


@patch("amb_cli.integrations.git.tools.pr_manager.GitService")
def test_pr_auto_detect_default_branch_error(MockGitService):
    mock_git = MockGitService.return_value
    mock_git.get_current_branch.return_value = "main"

    with pytest.raises(ApiExecutionError, match="A branch ativa é 'main'. Informe o número do PR explicitamente."):
        run_pr_manager(action="get", pr_number=None)

    mock_git.get_current_branch.assert_called_once()
    mock_git.list_open_prs.assert_not_called()
    mock_git.get_pr.assert_not_called()

@patch("amb_cli.integrations.git.tools.pr_manager.GitService")
def test_pr_auto_detect_no_pr_found_error(MockGitService):
    mock_git = MockGitService.return_value
    mock_git.get_current_branch.return_value = "feature/auth"
    mock_git.list_open_prs.return_value = [{"number": 10, "headRefName": "feature/other"}]

    with pytest.raises(ApiExecutionError, match="Nenhum PR aberto associado à branch ativa 'feature/auth'. Use 'amb git pr create'."):
        run_pr_manager(action="get", pr_number=None)

    mock_git.get_current_branch.assert_called_once()
    mock_git.list_open_prs.assert_called_once_with(repo_name=None)
    mock_git.get_pr.assert_not_called()


@patch("amb_cli.integrations.git.tools.pr_manager.GitService")
def test_pr_explicit_number(MockGitService):
    mock_git = MockGitService.return_value

    run_pr_manager(action="get", pr_number=123)

    mock_git.get_pr.assert_called_once_with(pr_number=123, repo_name=None)
    mock_git.get_current_branch.assert_not_called()
    mock_git.list_open_prs.assert_not_called()
