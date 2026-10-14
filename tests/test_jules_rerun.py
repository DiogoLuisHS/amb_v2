import pytest
from unittest.mock import patch, MagicMock

from integrations.jules.tools.rerun_session import run_rerun_session


@patch("integrations.jules.tools.rerun_session.run_create_session")
@patch("integrations.jules.tools.rerun_session.JulesClient")
def test_rerun_session_success(mock_client_class, mock_create):
    mock_client = MagicMock()
    mock_client_class.return_value = mock_client

    mock_client.normalize_session_id.return_value = "session_123"
    mock_client.get_session.return_value = {
        "id": "session_123",
        "title": "Fix bug X",
        "prompt": "Please fix bug X",
        "sourceContext": {
            "source": "sources/github/owner/repo",
            "gitContext": {
                "targetBranch": "feat-x"
            }
        }
    }

    mock_create.return_value = {"id": "new_session_456"}

    result = run_rerun_session(session_id="session_123")

    mock_client.get_session.assert_called_once_with("session_123")
    mock_create.assert_called_once_with(
        prompt="Please fix bug X",
        title="[Rerun] Fix bug X",
        base_branch="feat-x",
        source_name="sources/github/owner/repo",
        as_json=False,
        client=mock_client
    )
    assert result == {"id": "new_session_456"}


@patch("integrations.jules.tools.rerun_session.run_create_session")
@patch("integrations.jules.tools.rerun_session.JulesClient")
def test_rerun_session_override_prompt_and_branch(mock_client_class, mock_create):
    mock_client = MagicMock()
    mock_client_class.return_value = mock_client

    mock_client.normalize_session_id.return_value = "session_123"
    mock_client.get_session.return_value = {
        "id": "session_123",
        "title": "Fix bug X",
        "prompt": "Please fix bug X",
        "sourceContext": {
            "source": "sources/github/owner/repo",
            "gitContext": {
                "targetBranch": "feat-x"
            }
        }
    }

    mock_create.return_value = {"id": "new_session_456"}

    result = run_rerun_session(
        session_id="session_123",
        new_prompt="New prompt!",
        new_branch="new-branch"
    )

    mock_create.assert_called_once_with(
        prompt="New prompt!",
        title="[Rerun] Fix bug X",
        base_branch="new-branch",
        source_name="sources/github/owner/repo",
        as_json=False,
        client=mock_client
    )


@patch("integrations.jules.tools.rerun_session.run_create_session")
@patch("integrations.jules.tools.rerun_session.JulesClient")
def test_rerun_session_prompt_from_activities(mock_client_class, mock_create):
    mock_client = MagicMock()
    mock_client_class.return_value = mock_client

    mock_client.normalize_session_id.return_value = "session_123"
    mock_client.get_session.return_value = {
        "id": "session_123",
        "title": "Fix bug X",
        "sourceContext": {
            "source": "sources/github/owner/repo",
            "gitContext": {
                "targetBranch": "feat-x"
            }
        }
    }

    # Prompt not in session, return it from activities
    mock_client.list_activities.return_value = {
        "activities": [
            {"type": "OTHER"},
            {"type": "PROMPT", "prompt": "Prompt from activities"}
        ]
    }

    mock_create.return_value = {"id": "new_session_456"}

    run_rerun_session(session_id="session_123")

    mock_create.assert_called_once_with(
        prompt="Prompt from activities",
        title="[Rerun] Fix bug X",
        base_branch="feat-x",
        source_name="sources/github/owner/repo",
        as_json=False,
        client=mock_client
    )


@patch("integrations.jules.tools.rerun_session.run_create_session")
@patch("integrations.jules.tools.rerun_session.JulesClient")
def test_rerun_session_not_found(mock_client_class, mock_create):
    mock_client = MagicMock()
    mock_client_class.return_value = mock_client

    mock_client.normalize_session_id.return_value = "session_123"
    mock_client.get_session.side_effect = Exception("404 NOT_FOUND")

    result = run_rerun_session(session_id="session_123")

    assert result == {}
    mock_create.assert_not_called()
