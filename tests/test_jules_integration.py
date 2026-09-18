import pytest
from unittest.mock import MagicMock, patch
from integrations.jules.jules_client import JulesClient
from integrations.jules.jules_watcher import JulesWatcher
from integrations.jules.tools.cleanup_sessions import run_cleanup_sessions
from integrations.jules.tools.create_session import run_create_session
from integrations.jules.tools.get_session import run_get_session
from integrations.jules.tools.list_sessions import run_list_sessions
from integrations.jules.tools.list_sources import run_list_sources
from integrations.jules.tools.approve_plan import run_approve_plan
from integrations.jules.tools.send_message import run_send_message
from cli_modules.cli_handlers import cmd_jules


def test_jules_client_extract_pull_request_from_outputs_list():
    session_data = {
        "id": "123",
        "outputs": [
            {
                "pullRequest": {
                    "url": "https://github.com/org/repo/pull/42",
                    "title": "feat: test PR"
                }
            }
        ]
    }
    pr = JulesClient.extract_pull_request(session_data)
    assert pr is not None
    assert pr["url"] == "https://github.com/org/repo/pull/42"


def test_jules_client_extract_pull_request_from_outputs_dict():
    session_data = {
        "id": "123",
        "outputs": {
            "pullRequest": {
                "url": "https://github.com/org/repo/pull/99"
            }
        }
    }
    pr = JulesClient.extract_pull_request(session_data)
    assert pr is not None
    assert pr["url"] == "https://github.com/org/repo/pull/99"


def test_jules_client_extract_pull_request_from_activities_fallback():
    session_data = {
        "id": "123",
        "outputs": []
    }
    activities = [
        {"type": "action", "description": "Criado o PR https://github.com/org/repo/pull/105 no GitHub."}
    ]
    pr = JulesClient.extract_pull_request(session_data, activities=activities)
    assert pr is not None
    assert pr["number"] == 105
    assert "https://github.com/org/repo/pull/105" in pr["url"]


def test_jules_client_extract_pull_request_none_when_empty():
    session_data = {"id": "123", "outputs": []}
    pr = JulesClient.extract_pull_request(session_data, activities=[])
    assert pr is None


def test_jules_watcher_extract_pull_request_delegates():
    session_data = {
        "outputs": [
            {"pullRequest": {"url": "https://github.com/org/repo/pull/77"}}
        ]
    }
    pr = JulesWatcher.extract_pull_request(session_data)
    assert pr is not None
    assert pr["url"] == "https://github.com/org/repo/pull/77"


def test_normalize_session_id():
    assert JulesClient.normalize_session_id("12345") == "12345"
    assert JulesClient.normalize_session_id("sessions/12345") == "12345"
    assert JulesClient.normalize_session_id("https://jules.google.com/session/12345") == "12345"
    assert JulesClient.normalize_session_id("https://jules.google.com/session/12345/") == "12345"
    assert JulesClient.normalize_session_id("https://jules.google.com/session/12345?foo=bar") == "12345"
    assert JulesClient.normalize_session_id("") == ""


def test_create_session_respects_explicit_branch():
    mock_client = MagicMock(spec=JulesClient)
    mock_client.create_session = JulesClient.create_session.__get__(mock_client)
    mock_client._request = MagicMock(return_value={"id": "999"})

    with patch("config.get_repo_name", return_value="org/repo"):
        # Explicit branch provided: must NOT call GitService
        with patch("integrations.git.git_service.GitService.get_current_branch") as mock_git:
            mock_client.create_session("Meu prompt", base_branch="custom-branch")
            mock_git.assert_not_called()

        assert mock_client._request.call_count == 1
        _, kwargs = mock_client._request.call_args
        payload = kwargs["data"]
        assert payload["sourceContext"]["githubRepoContext"]["startingBranch"] == "custom-branch"


def test_create_session_auto_detects_branch():
    mock_client = MagicMock(spec=JulesClient)
    mock_client.create_session = JulesClient.create_session.__get__(mock_client)
    mock_client._request = MagicMock(return_value={"id": "999"})

    with patch("config.get_repo_name", return_value="org/repo"):
        with patch("integrations.git.git_service.GitService.get_current_branch", return_value="feature-x"):
            mock_client.create_session("Meu prompt", base_branch=None)

        _, kwargs = mock_client._request.call_args
        payload = kwargs["data"]
        assert payload["sourceContext"]["githubRepoContext"]["startingBranch"] == "feature-x"


def test_list_sessions_strict_filtering():
    mock_client = MagicMock(spec=JulesClient)
    mock_client.list_sessions = JulesClient.list_sessions.__get__(mock_client)
    mock_client._request = MagicMock(return_value={
        "sessions": [
            {"id": "1", "state": "COMPLETED", "sourceContext": {"source": "sources/github/org/my-repo"}},
            {"id": "2", "state": "FAILED", "sourceContext": {"source": "sources/github/org/other-repo"}},
            {"id": "3", "state": "IN_PROGRESS"},  # Missing sourceContext - must NOT leak!
        ]
    })

    # Strict repo filter: only session 1 matches
    res = mock_client.list_sessions(repo_filter="my-repo")
    assert len(res) == 1
    assert res[0]["id"] == "1"

    # State filter
    res_state = mock_client.list_sessions(repo_filter="my-repo", state_filter="COMPLETED")
    assert len(res_state) == 1

    res_fail = mock_client.list_sessions(repo_filter="my-repo", state_filter="FAILED")
    assert len(res_fail) == 0


def test_get_status_and_sources():
    mock_client = MagicMock(spec=JulesClient)
    mock_client.get_status = JulesClient.get_status.__get__(mock_client)
    mock_client.list_sources = MagicMock(return_value=[
        {"name": "sources/github/org/repo"}
    ])
    mock_client.list_sessions = MagicMock(return_value=[
        {"id": "1", "state": "AWAITING_USER_FEEDBACK"}
    ])

    with patch("config.get_env", return_value="test-key"):
        status = mock_client.get_status(repo_filter="org/repo")
        assert status["api_key_configured"] is True
        assert status["api_reachable"] is True
        assert status["sources_count"] == 1
        assert status["repo_connected"] is True
        assert status["sessions_total"] == 1
        assert status["sessions_awaiting_feedback"] == 1


def test_approve_plan_guardrails():
    mock_client = MagicMock()
    mock_client.normalize_session_id.side_effect = lambda x: str(x)
    mock_client.get_session.return_value = {"state": "IN_PROGRESS"}
    mock_client.list_activities.return_value = {"activities": []}

    # Should raise ValueError because there's no pending plan
    with pytest.raises(ValueError, match="Error: There is no pending plan to approve"):
        run_approve_plan("123", force=False, client=mock_client)

    # Force should bypass check
    mock_client.approve_plan.return_value = {"approved": True}
    res = run_approve_plan("123", force=True, client=mock_client)
    assert res == {"approved": True}
    mock_client.approve_plan.assert_called_once_with("123")


def test_send_message_guardrails():
    mock_client = MagicMock()
    mock_client.normalize_session_id.side_effect = lambda x: str(x)
    mock_client.list_activities.return_value = {
        "activities": [{"originator": "user", "text": "last message"}]
    }

    # Should raise ValueError because last activity is from user
    with pytest.raises(ValueError, match="Please wait for the agent to reply"):
        run_send_message("123", "Hello again", force=False, client=mock_client)

    # Force should bypass check
    mock_client.send_message.return_value = {"sent": True}
    res = run_send_message("123", "Hello again", force=True, client=mock_client)
    assert res == {"sent": True}
    mock_client.send_message.assert_called_once_with(session_id="123", message="Hello again")


def test_jules_facade_tools():
    mock_client = MagicMock()
    mock_client.normalize_session_id.side_effect = lambda x: str(x)
    mock_client.list_sources.return_value = [{"name": "sources/github/a/b"}]
    mock_client.list_sessions.return_value = [{"id": "s1", "title": "test", "state": "COMPLETED"}]
    mock_client.get_session.return_value = {"id": "s1", "title": "test", "state": "COMPLETED"}
    mock_client.create_session.return_value = {"name": "sessions/s2"}

    # run_list_sources
    sources = run_list_sources(as_json=True, client=mock_client)
    assert len(sources) == 1

    # run_list_sessions
    sessions = run_list_sessions(limit=5, all_repos=True, as_json=True, client=mock_client)
    assert len(sessions) == 1

    # run_get_session
    sess = run_get_session("s1", watch=False, as_json=True, client=mock_client)
    assert sess["id"] == "s1"

    # run_create_session
    created = run_create_session(prompt="Test prompt", title="Test", as_json=True, client=mock_client)
    assert created["name"] == "sessions/s2"


@patch("integrations.jules.jules_client.require_env", return_value="dummy_key")
def test_jules_cli_handlers(mock_get_env):
    with patch("integrations.jules.jules_client.JulesClient.get_status") as mock_status:
        mock_status.return_value = {
            "api_key_configured": True,
            "api_reachable": True,
            "sources_count": 2,
            "active_repo": "my/repo",
            "repo_connected": True,
            "sessions_total": 0,
            "sessions_awaiting_feedback": 0,
            "sessions_in_progress": 0,
            "sessions_completed": 0,
            "sessions_failed": 0,
            "error": None
        }
        args = MagicMock()
        args.jules_cmd = "status"
        args.repo = None
        args.json = True
        cmd_jules(args)
        mock_status.assert_called_once()

    with patch("integrations.jules.tools.list_sources.run_list_sources") as mock_src:
        args = MagicMock()
        args.jules_cmd = "sources"
        args.json = True
        cmd_jules(args)
        mock_src.assert_called_once()


def test_cleanup_sessions_service_dry_run():
    mock_client = MagicMock()
    mock_client.list_sessions.return_value = [
        {
            "name": "sessions/1001",
            "title": "Fix bug",
            "state": "COMPLETED",
            "outputs": [{"pullRequest": {"url": "https://github.com/org/repo/pull/10"}}]
        }
    ]

    with patch("integrations.jules.tools.cleanup_sessions.get_git_merge_history", return_value="#10 merge commit"):
        res = run_cleanup_sessions(delete_mode="merged", dry_run=True, client=mock_client)
        assert isinstance(res, dict)
        assert "merged" in res
        assert len(res["merged"]) == 1
        assert res["merged"][0]["session_id"] == "1001"
        # Since dry_run=True, delete_session must not be called
        mock_client.delete_session.assert_not_called()
