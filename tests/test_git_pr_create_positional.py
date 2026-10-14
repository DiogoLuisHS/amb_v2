import pytest
from unittest.mock import patch, MagicMock

from amb_cli.integrations.git.tools.pr_manager import run_pr_manager
from core.exceptions import ApiExecutionError


@patch("amb_cli.integrations.git.tools.pr_manager.GitService")
def test_create_pr_positional_title(MockGitService):
    mock_git = MockGitService.return_value
    mock_git._run_git.return_value.returncode = 0
    mock_git._run_git.return_value.stdout = "a1b2c3d commit test\n"
    mock_git.get_upstream_branch.return_value = "main"

    run_pr_manager(
        action="create",
        title_pos="Feature XYZ Posicional",
        title=None,
        body="Corpo fixo"
    )

    mock_git.create_pr.assert_called_once_with(
        title="Feature XYZ Posicional",
        body="Corpo fixo",
        base=None,
        head=None,
        draft=False,
        repo_name=None
    )


@patch("amb_cli.integrations.git.tools.pr_manager.GitService")
def test_create_pr_fallback_title(MockGitService):
    mock_git = MockGitService.return_value

    def side_effect_run_git(args, *a, **kw):
        mock_res = MagicMock()
        if "log" in args and "-1" in args and "--pretty=%B" in args:
            mock_res.returncode = 0
            mock_res.stdout = "feat: Auto Title Commit\n\nSome body info"
            return mock_res
        if "log" in args and "--oneline" in args:
            mock_res.returncode = 0
            mock_res.stdout = "a1b2c3d feat: Auto Title Commit"
            return mock_res
        mock_res.returncode = 1
        return mock_res

    mock_git._run_git.side_effect = side_effect_run_git
    mock_git.get_upstream_branch.return_value = "main"

    run_pr_manager(
        action="create",
        title=None,
        title_pos=None,
        body="Corpo fixo"
    )

    mock_git.create_pr.assert_called_once_with(
        title="feat: Auto Title Commit",
        body="Corpo fixo",
        base=None,
        head=None,
        draft=False,
        repo_name=None
    )


@patch("amb_cli.integrations.git.tools.pr_manager.GitService")
def test_create_pr_auto_body(MockGitService):
    mock_git = MockGitService.return_value

    def side_effect_run_git(args, *a, **kw):
        mock_res = MagicMock()
        if "log" in args and "--oneline" in args:
            mock_res.returncode = 0
            mock_res.stdout = "1111111 commit auto 1\n2222222 commit auto 2\n"
            return mock_res
        if "log" in args and "-1" in args and "--pretty=%B" in args:
            mock_res.returncode = 0
            mock_res.stdout = "My Last Commit"
            return mock_res
        mock_res.returncode = 1
        return mock_res

    mock_git._run_git.side_effect = side_effect_run_git
    mock_git.get_upstream_branch.return_value = "main"

    run_pr_manager(
        action="create",
        title="Feature XYZ",
        body=None
    )

    expected_body = "### 📋 Resumo das Alterações\nPull Request gerado automaticamente pelo AMB_V2.\n\n### 📦 Commits Integrados:\n- 1111111 commit auto 1\n- 2222222 commit auto 2"
    mock_git.create_pr.assert_called_once_with(
        title="Feature XYZ",
        body=expected_body,
        base=None,
        head=None,
        draft=False,
        repo_name=None
    )


@patch("amb_cli.integrations.git.tools.pr_manager.GitService")
def test_create_pr_preserves_flags(MockGitService):
    mock_git = MockGitService.return_value

    run_pr_manager(
        action="create",
        title="Feature Explicit Title",
        body="Feature Explicit Body"
    )

    mock_git.create_pr.assert_called_once_with(
        title="Feature Explicit Title",
        body="Feature Explicit Body",
        base=None,
        head=None,
        draft=False,
        repo_name=None
    )

@patch("amb_cli.integrations.git.tools.pr_manager.GitService")
def test_create_pr_no_title_raises_error(MockGitService):
    mock_git = MockGitService.return_value
    mock_git._run_git.return_value.returncode = 1
    mock_git._run_git.return_value.stdout = ""

    with pytest.raises(ApiExecutionError, match="Título é obrigatório para criação de PR e não pôde ser inferido."):
        run_pr_manager(
            action="create",
            title=None,
            title_pos=None
        )
