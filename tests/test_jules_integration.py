import pytest
from unittest.mock import MagicMock, patch
from integrations.jules.jules_client import JulesClient
from integrations.jules.jules_watcher import JulesWatcher
from integrations.jules.tools.cleanup_sessions import run_cleanup_sessions


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
