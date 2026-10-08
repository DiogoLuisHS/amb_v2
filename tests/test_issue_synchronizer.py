# -*- coding: utf-8 -*-
"""Unit tests for workspace/issue_synchronizer.py and Git issue operations."""

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
from workspace.issue_synchronizer import IssueSynchronizer, natural_sort_key
from integrations.git.git_service import GitService
from integrations.git.git_core.gh_cli import (
    list_issues, get_issue, create_issue, close_issue
)


def test_natural_sort_key():
    files = [
        Path("10_relatorios.md"),
        Path("1_auth.md"),
        Path("2_dashboard.md"),
        Path("03_settings.md"),
    ]
    sorted_files = sorted(files, key=natural_sort_key)
    names = [f.name for f in sorted_files]
    assert names == ["1_auth.md", "2_dashboard.md", "03_settings.md", "10_relatorios.md"]


def test_extract_prompt_title():
    syncer = IssueSynchronizer()
    content_with_h1 = "# Implementar Autenticação JWT\n\nDetalhes do requisito..."
    title = syncer.extract_prompt_title(Path("01_auth.md"), content_with_h1)
    assert title == "Implementar Autenticação JWT"

    content_without_h1 = "Apenas texto corrido sem título markdown."
    title_fallback = syncer.extract_prompt_title(Path("02_user_profile.md"), content_without_h1)
    assert title_fallback == "02 User Profile"


def test_make_prompt_marker():
    marker = IssueSynchronizer.make_prompt_marker("01_login.md")
    assert marker == "<!-- amb:prompt: 01_login.md -->"


def test_find_matching_issue():
    syncer = IssueSynchronizer()
    open_issues = [
        {"number": 10, "title": "Old Task", "body": "random content"},
        {"number": 42, "title": "Login Task", "body": "Content\n<!-- amb:prompt: 01_login.md -->"},
    ]
    match = syncer.find_matching_issue(open_issues, "01_login.md")
    assert match is not None
    assert match["number"] == 42

    no_match = syncer.find_matching_issue(open_issues, "02_logout.md")
    assert no_match is None


def test_discover_prompt_files(tmp_path):
    p1 = tmp_path / "01_init.md"
    p2 = tmp_path / "02_api.md"
    p_readme = tmp_path / "README.md"
    p_draft = tmp_path / "_draft.md"
    p_dot = tmp_path / ".hidden.md"

    for p in (p1, p2, p_readme, p_draft, p_dot):
        p.write_text("content", encoding="utf-8")

    syncer = IssueSynchronizer(repo_root=str(tmp_path))
    files = syncer.discover_prompt_files(tmp_path)
    file_names = [f.name for f in files]

    assert "01_init.md" in file_names
    assert "02_api.md" in file_names
    assert "README.md" not in file_names
    assert "_draft.md" not in file_names
    assert ".hidden.md" not in file_names


def test_sync_prompts_idempotent(tmp_path):
    p1 = tmp_path / "01_login.md"
    p1.write_text("# US-01: Login\nRequisitos de login.", encoding="utf-8")
    p2 = tmp_path / "02_checkout.md"
    p2.write_text("# US-02: Checkout\nRequisitos de checkout.", encoding="utf-8")

    syncer = IssueSynchronizer(repo_root=str(tmp_path))

    existing_issues = [
        {
            "number": 42,
            "title": "US-01: Login",
            "url": "https://github.com/org/repo/issues/42",
            "body": "Existing body\n<!-- amb:prompt: 01_login.md -->",
        }
    ]

    with patch.object(syncer.git, "list_issues", return_value=existing_issues), \
         patch.object(syncer.git, "create_issue", return_value={"number": 43, "url": "https://github.com/org/repo/issues/43"}) as mock_create:

        queue = syncer.sync_prompts(tmp_path)
        assert len(queue) == 2

        # 01_login.md deve ser reaproveitado
        assert queue[0]["issue_number"] == 42
        assert queue[0]["is_new"] is False

        # 02_checkout.md deve ser criado
        assert queue[1]["issue_number"] == 43
        assert queue[1]["is_new"] is True
        mock_create.assert_called_once()


def test_sync_prompts_dry_run(tmp_path):
    p = tmp_path / "01_feat.md"
    p.write_text("# Feature X", encoding="utf-8")

    syncer = IssueSynchronizer(repo_root=str(tmp_path))
    with patch.object(syncer.git, "list_issues", return_value=[]), \
         patch.object(syncer.git, "create_issue") as mock_create:

        queue = syncer.sync_prompts(tmp_path, dry_run=True)
        assert len(queue) == 1
        assert queue[0]["issue_number"] == 0
        assert queue[0]["is_new"] is True
        mock_create.assert_not_called()


def test_list_open_issue_queue():
    syncer = IssueSynchronizer()
    mock_issues = [
        {"number": 15, "title": "Task 15", "body": "body 15", "url": "url15"},
        {"number": 10, "title": "Task 10", "body": "body 10", "url": "url10"},
    ]
    with patch.object(syncer.git, "list_issues", return_value=mock_issues):
        queue = syncer.list_open_issue_queue()
        assert len(queue) == 2
        # Ordenado por número crescente
        assert queue[0]["issue_number"] == 10
        assert queue[1]["issue_number"] == 15


def test_resolve_items_queue_modes(tmp_path):
    p = tmp_path / "01_task.md"
    p.write_text("# Tarefa 1", encoding="utf-8")
    syncer = IssueSynchronizer(repo_root=str(tmp_path))

    # Modo 1: Prompts locais (sem issues)
    items_local = syncer.resolve_items_queue(tmp_path, use_issues=False)
    assert len(items_local) == 1
    assert items_local[0]["type"] == "prompt"
    assert items_local[0]["name"] == "01_task"

    # Modo 2: Com issues ativadas e caminho
    with patch.object(syncer, "sync_prompts", return_value=[{"issue_number": 99, "title": "T99", "file_name": "01_task.md", "path": p, "content": "c"}]):
        items_issues = syncer.resolve_items_queue(tmp_path, use_issues=True)
        assert len(items_issues) == 1
        assert items_issues[0]["type"] == "issue"
        assert items_issues[0]["issue_number"] == 99

    # Modo 3: Com issues ativadas sem caminho (fila remota do GitHub)
    with patch.object(syncer, "list_open_issue_queue", return_value=[{"issue_number": 101, "title": "T101", "file_name": "issue_101.md", "path": None, "content": "c"}]):
        items_remote = syncer.resolve_items_queue(None, use_issues=True)
        assert len(items_remote) == 1
        assert items_remote[0]["type"] == "issue"
        assert items_remote[0]["issue_number"] == 101


def test_close_issue():
    syncer = IssueSynchronizer()
    with patch.object(syncer.git, "close_issue", return_value=True) as mock_close:
        assert syncer.close_issue(42, comment="Done") is True
        mock_close.assert_called_once_with(issue_number=42, comment="Done")

    # Issue <= 0 não deve tentar fechar
    assert syncer.close_issue(0) is False


def test_gh_cli_issue_functions():
    # list_issues
    with patch("integrations.git.git_core.gh_cli._run_gh") as mock_run:
        mock_run.return_value = MagicMock(returncode=0, stdout=json.dumps([{"number": 1, "title": "Issue 1"}]))
        issues = list_issues(state="open", labels=["amb:prompt"])
        assert len(issues) == 1
        assert issues[0]["number"] == 1

    # get_issue
    with patch("integrations.git.git_core.gh_cli._run_gh") as mock_run:
        mock_run.return_value = MagicMock(returncode=0, stdout=json.dumps({"number": 5, "title": "Issue 5"}))
        iss = get_issue(5)
        assert iss.get("number") == 5

    # create_issue
    with patch("integrations.git.git_core.gh_cli._run_gh") as mock_run:
        mock_run.return_value = MagicMock(returncode=0, stdout="https://github.com/org/repo/issues/77\n")
        res = create_issue("Title", "Body", labels=["amb:prompt"])
        assert res["number"] == 77
        assert res["success"] is True

    # close_issue
    with patch("integrations.git.git_core.gh_cli._run_gh") as mock_run:
        mock_run.return_value = MagicMock(returncode=0)
        assert close_issue(77, comment="Closed by test") is True
