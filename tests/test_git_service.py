# -*- coding: utf-8 -*-
"""Unit tests for integrations/git/git_service.py."""

import json
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

_root = Path(__file__).resolve().parent.parent
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))
from config.bootstrap import ensure_amb_env
ensure_amb_env()

import pytest
from config import ApiExecutionError
from integrations.git.git_service import GitService


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

    with patch("shutil.which", return_value="/usr/bin/gh"), \
         patch("subprocess.run", return_value=MagicMock(returncode=1)):
        with pytest.raises(ApiExecutionError) as exc_info:
            git.check_gh_auth()
        assert "não autenticada" in str(exc_info.value)


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
