# -*- coding: utf-8 -*-
"""Unit tests for integrations/git/git_service.py."""

import json
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

_root = Path(__file__).resolve().parent.parent
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))
from core.bootstrap import ensure_amb_env
ensure_amb_env()

import pytest
from core import ApiExecutionError
from integrations.git.git_service import GitService
from integrations.git.tools.git_status import run_git_status
from integrations.git.tools.pr_manager import run_pr_manager
from integrations.git.tools.sync_branch import run_sync_branch
from cli_modules.cli_handlers import cmd_git


def test_get_current_branch():
    git = GitService()
    mock_res = MagicMock(returncode=0, stdout="feature/my-branch\n")
    with patch("subprocess.run", return_value=mock_res):
        branch = git.get_current_branch()
        assert branch == "feature/my-branch"


def test_detect_github_repo():
    git = GitService()
    mock_res = MagicMock(returncode=0, stdout="git@github.com:DiogoLuisHS/amb_v2.git\n")
    with patch("subprocess.run", return_value=mock_res):
        repo = git.detect_github_repo()
        assert repo == "DiogoLuisHS/amb_v2"


def test_is_clean():
    git = GitService()
    # Limpo
    with patch("subprocess.run", return_value=MagicMock(returncode=0, stdout="")):
        assert git.is_clean() is True

    # Com alterações
    with patch("subprocess.run", return_value=MagicMock(returncode=0, stdout=" M file.py\n")):
        assert git.is_clean() is False


def test_checkout_and_pull():
    git = GitService()
    with patch("subprocess.run", return_value=MagicMock(returncode=0)) as mock_run:
        assert git.checkout("develop", create=True) is True
        assert git.pull("origin", "develop") is True
        assert mock_run.call_count == 2


def test_check_gh_auth_failure():
    git = GitService()
    with patch("shutil.which", return_value=None):
        with pytest.raises(ApiExecutionError) as exc_info:
            git.check_gh_auth()
        assert "não encontrada" in str(exc_info.value)

        # fail_silently=True deve retornar False sem raise
        assert git.check_gh_auth(fail_silently=True) is False

    with patch("shutil.which", return_value="/usr/bin/gh"), \
         patch("subprocess.run", return_value=MagicMock(returncode=1)):
        with pytest.raises(ApiExecutionError) as exc_info:
            git.check_gh_auth()
        assert "não autenticada" in str(exc_info.value)

        # fail_silently=True deve retornar False sem raise
        assert git.check_gh_auth(fail_silently=True) is False


def test_list_open_prs():
    git = GitService()
    prs_data = [
        {"number": 42, "title": "Add feature", "createdAt": "2026-09-16T10:00:00Z"},
        {"number": 43, "title": "Fix bug", "createdAt": "2026-09-16T11:00:00Z"},
    ]
    mock_res = MagicMock(returncode=0, stdout=json.dumps(prs_data))
    with patch("subprocess.run", return_value=mock_res):
        prs = git.list_open_prs("my-org/my-repo")
        assert len(prs) == 2
        # Mais recente primeiro
        assert prs[0]["number"] == 43

        latest = git.get_latest_open_pr("my-org/my-repo")
        assert latest["number"] == 43


def test_pr_workflow_ready_approve_merge():
    git = GitService()
    with patch("subprocess.run", return_value=MagicMock(returncode=0)) as mock_run:
        assert git.mark_pr_ready(42, "my-org/my-repo") is True
        assert git.approve_pr(42, "my-org/my-repo") is True
        assert git.merge_pr(42, "my-org/my-repo") is True
        assert mock_run.call_count == 3


def test_get_detailed_status_and_upstream():
    git = GitService()
    with patch.object(git, "get_current_branch", return_value="main"), \
         patch.object(git, "get_upstream_branch", return_value="origin/main"), \
         patch.object(git, "get_ahead_behind", return_value=(2, 1)), \
         patch.object(git, "get_status", return_value="M  staged.py\n M unstaged.py\n?? untracked.py"):

        detailed = git.get_detailed_status()
        assert detailed["branch"] == "main"
        assert detailed["upstream"] == "origin/main"
        assert detailed["ahead"] == 2
        assert detailed["behind"] == 1
        assert detailed["is_clean"] is False
        assert "M staged.py" in detailed["staged"]
        assert "M unstaged.py" in detailed["unstaged"]
        assert "untracked.py" in detailed["untracked"]


def test_get_diff_and_stash():
    git = GitService()
    mock_diff = MagicMock(returncode=0, stdout="diff --git a/f b/f\n+new line")
    with patch("subprocess.run", return_value=mock_diff):
        diff = git.get_diff(cached=True)
        assert "+new line" in diff

    with patch("subprocess.run", return_value=MagicMock(returncode=0)) as mock_run:
        assert git.fetch(remote="origin", prune=True) is True
        assert git.stash(action="push", message="test stash") is True
        assert git.stash(action="pop") is True
        assert git.create_branch("feature/new", checkout=True) is True
        assert mock_run.call_count == 4


def test_pr_get_create_close():
    git = GitService()
    pr_sample = {"number": 101, "title": "My PR", "state": "OPEN"}
    with patch("subprocess.run", return_value=MagicMock(returncode=0, stdout=json.dumps(pr_sample))):
        pr = git.get_pr(101, repo_name="owner/repo")
        assert pr["number"] == 101
        assert pr["title"] == "My PR"

    create_res = MagicMock(returncode=0, stdout="https://github.com/owner/repo/pull/102\n")
    with patch("subprocess.run", return_value=create_res):
        created = git.create_pr(title="Test PR", body="PR description", repo_name="owner/repo")
        assert created["success"] is True
        assert created["number"] == 102
        assert created["url"] == "https://github.com/owner/repo/pull/102"

    with patch("subprocess.run", return_value=MagicMock(returncode=0)):
        closed = git.close_pr(102, comment="Closed by test", repo_name="owner/repo")
        assert closed is True


def test_git_facade_tools():
    # 1. run_git_status
    with patch("integrations.git.tools.git_status.GitService.get_detailed_status", return_value={"branch": "main", "upstream": None, "ahead": 0, "behind": 0, "is_clean": True, "staged": [], "unstaged": [], "untracked": [], "github_repo": "owner/repo"}), \
         patch("integrations.git.tools.git_status.GitService.is_gh_installed", return_value=True), \
         patch("integrations.git.tools.git_status.GitService.check_gh_auth", return_value=True):
        st = run_git_status(as_json=True)
        assert st["branch"] == "main"
        assert st["github_cli"]["authenticated"] is True

    # 2. run_pr_manager
    with patch("integrations.git.tools.pr_manager.GitService.check_gh_auth", return_value=True), \
         patch("integrations.git.tools.pr_manager.GitService.list_open_prs", return_value=[{"number": 1}]):
        res = run_pr_manager(action="list")
        assert len(res) == 1
        assert res[0]["number"] == 1

    # 3. run_sync_branch
    with patch("integrations.git.tools.sync_branch.GitService.is_clean", return_value=True), \
         patch("integrations.git.tools.sync_branch.GitService.get_current_branch", return_value="main"), \
         patch("integrations.git.tools.sync_branch.GitService.fetch", return_value=True), \
         patch("integrations.git.tools.sync_branch.GitService.pull", return_value=True):
        assert run_sync_branch() is True


def test_git_cli_handlers(capsys):
    # amb git status --json
    with patch("integrations.git.tools.git_status.run_git_status", return_value={"branch": "main"}):
        cmd_git(MagicMock(git_cmd="status", json=True))

    # amb git diff
    with patch("integrations.git.git_service.GitService.get_diff", return_value="diff output"):
        cmd_git(MagicMock(git_cmd="diff", file=None, base=None, cached=False))
        captured = capsys.readouterr()
        assert "diff output" in captured.out
