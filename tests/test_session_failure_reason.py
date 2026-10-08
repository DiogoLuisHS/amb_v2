import pytest
from unittest.mock import MagicMock, patch

from amb_cli.integrations.jules.jules_core.session_extractor import SessionExtractor
from amb_cli.integrations.jules.tools.get_session import run_get_session
from amb_cli.core import Colors


def test_extract_failure_reason_with_valid_reason():
    activities = [
        {"name": "act1", "originator": "user"},
        {"name": "act2", "sessionFailed": {"reason": "Execution timed out"}},
        {"name": "act3", "originator": "system"}
    ]
    reason = SessionExtractor.extract_failure_reason(activities)
    assert reason == "Execution timed out"

def test_extract_failure_reason_no_failure_event():
    activities = [
        {"name": "act1"},
        {"name": "act2", "otherEvent": {}}
    ]
    reason = SessionExtractor.extract_failure_reason(activities)
    assert reason is None

def test_extract_failure_reason_resilience():
    # Should handle empty list, None, and malformed items
    assert SessionExtractor.extract_failure_reason(None) is None
    assert SessionExtractor.extract_failure_reason([]) is None

    activities = [
        "not-a-dict",
        {"name": "act", "sessionFailed": "not-a-dict"},
        {"name": "act", "sessionFailed": {"reason": None}},
        {"name": "act", "sessionFailed": {"reason": 123}},
    ]
    assert SessionExtractor.extract_failure_reason(activities) is None


@patch("amb_cli.integrations.jules.tools.get_session.JulesClient")
def test_run_get_session_failed(MockJulesClient, capsys):
    mock_client = MockJulesClient.return_value
    mock_client.normalize_session_id.return_value = "sessions/123"
    mock_client.get_session.return_value = {
        "name": "sessions/123",
        "state": "FAILED",
        "title": "Test session"
    }

    mock_client.list_activities.return_value = [
        {"sessionFailed": {"reason": "Out of memory"}}
    ]

    run_get_session("123", client=mock_client)

    captured = capsys.readouterr()
    expected_msg = f"Motivo da Falha: {Colors.RED}Out of memory{Colors.RESET}"
    assert expected_msg in captured.out
