import pytest
from unittest.mock import MagicMock, patch
from integrations.jules.tools.merge_session_pr import (
    detect_pr_from_session,
    detect_pr_from_github,
    detect_and_create_pr_from_branch,
    approve_and_merge_pr,
)


def test_detect_pr_from_session():
    mock_client = MagicMock()
    mock_client.normalize_session_id.return_value = "12345"
    mock_client.get_session.return_value = {
        "outputs": [{"pullRequest": {"url": "https://github.com/org/repo/pull/77", "number": 77}}]
    }
    mock_client.list_activities.return_value = []

    with patch("integrations.jules.tools.merge_session_pr.JulesClient") as mock_cls:
        mock_cls.return_value = mock_client
        mock_cls.normalize_session_id = lambda sid: sid
        mock_cls.extract_pull_request.return_value = {"number": 77, "url": "https://github.com/org/repo/pull/77"}
        pr_num = detect_pr_from_session("12345")
        assert pr_num == 77


def test_detect_pr_from_github_head_ref():
    mock_git = MagicMock()
    mock_git.list_open_prs.return_value = [
        {"number": 42, "headRefName": "fix-something-12345", "title": "Fix something"}
    ]

    with patch("integrations.jules.tools.merge_session_pr.GitService", return_value=mock_git):
        pr_num = detect_pr_from_github("12345", repo_name="org/repo")
        assert pr_num == 42


def test_detect_pr_from_github_title():
    mock_git = MagicMock()
    mock_git.list_open_prs.return_value = [
        {"number": 55, "headRefName": "some-branch", "title": "Auditoria de sessão 12345"}
    ]

    with patch("integrations.jules.tools.merge_session_pr.GitService", return_value=mock_git):
        pr_num = detect_pr_from_github("12345", repo_name="org/repo")
        assert pr_num == 55


def test_detect_and_create_pr_from_branch():
    mock_git = MagicMock()
    mock_git.create_pr.return_value = {"number": 88, "url": "https://github.com/org/repo/pull/88"}

    mock_run = MagicMock()
    mock_run.returncode = 0
    mock_run.stdout = "  origin/main\n  origin/fix-task-12345\n"

    with patch("integrations.jules.tools.merge_session_pr.GitService", return_value=mock_git), \
         patch("subprocess.run", return_value=mock_run):
        pr_num = detect_and_create_pr_from_branch("12345", target_branch="main", repo_name="org/repo")
        assert pr_num == 88
        mock_git.create_pr.assert_called_once()


def test_approve_and_merge_pr_success():
    with patch("integrations.jules.tools.merge_session_pr.detect_pr_from_github", return_value=99), \
         patch("integrations.jules.tools.merge_session_pr.find_repo_root", return_value="/tmp/repo"), \
         patch("integrations.jules.tools.merge_session_pr.get_repo_name", return_value="org/repo"), \
         patch("integrations.jules.tools.merge_session_pr.GitService") as mock_git_cls, \
         patch("pipeline.quality_gatekeeper.QualityGatekeeper.run_qa", return_value=True):

        mock_git = mock_git_cls.return_value
        mock_git.approve_pr.return_value = True
        mock_git.merge_pr.return_value = True
        mock_git.checkout.return_value = True
        mock_git.pull.return_value = True

        result = approve_and_merge_pr(session_id="12345", target_branch="main")
        assert result is True
        mock_git.mark_pr_ready.assert_called_with(99, repo_name="org/repo")
        mock_git.approve_pr.assert_called_once()
        mock_git.merge_pr.assert_called_once()
        mock_git.checkout.assert_called_with("main")
        mock_git.pull.assert_called_with("origin", "main")
