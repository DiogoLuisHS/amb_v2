import pytest
from unittest.mock import MagicMock, patch
from amb_cli.integrations.jules.jules_core.session_state import SessionState
from amb_cli.integrations.jules.jules_core.session_monitor import SessionMonitor
from amb_cli.integrations.jules.jules_client import JulesClient

@pytest.fixture
def mock_client():
    client = MagicMock(spec=JulesClient)
    return client

def test_poll_until_terminal_success(mock_client):
    mock_client.get_session.side_effect = [
        {"state": "IN_PROGRESS"},
        {"state": "COMPLETED"}
    ]

    monitor = SessionMonitor(client=mock_client, session_id="session/123")

    with patch("time.sleep", return_value=None):
        final_state, data = monitor.poll_until_terminal(interval_seconds=0)

    assert final_state == SessionState.COMPLETED
    assert final_state.is_terminal()
    assert final_state.is_success()
    assert data == {"state": "COMPLETED"}
    assert mock_client.get_session.call_count == 2

def test_poll_until_terminal_failure(mock_client):
    mock_client.get_session.side_effect = [
        {"state": "IN_PROGRESS"},
        {"state": "FAILED"}
    ]

    monitor = SessionMonitor(client=mock_client, session_id="session/123")

    with patch("time.sleep", return_value=None):
        final_state, data = monitor.poll_until_terminal(interval_seconds=0)

    assert final_state == SessionState.FAILED
    assert final_state.is_terminal()
    assert not final_state.is_success()
    assert data == {"state": "FAILED"}

def test_poll_until_terminal_timeout(mock_client):
    mock_client.get_session.return_value = {"state": "IN_PROGRESS"}

    monitor = SessionMonitor(client=mock_client, session_id="session/123")

    # Mock time.time to simulate timeout immediately after first check
    side_effects = [0, 10, 2000, 2000]
    def mock_time():
        return side_effects.pop(0)

    with patch("time.time", side_effect=mock_time):
        with patch("time.sleep", return_value=None):
            final_state, data = monitor.poll_until_terminal(interval_seconds=0, max_wait_seconds=1000)

    assert final_state == SessionState.IN_PROGRESS
    assert data == {"state": "IN_PROGRESS"}

def test_poll_until_terminal_callback(mock_client):
    mock_client.get_session.side_effect = [
        {"state": "IN_PROGRESS"},
        {"state": "AWAITING_INPUT"},
        {"state": "COMPLETED"}
    ]

    monitor = SessionMonitor(client=mock_client, session_id="session/123")
    callback_mock = MagicMock()

    with patch("time.sleep", return_value=None):
        final_state, data = monitor.poll_until_terminal(interval_seconds=0, on_state_change=callback_mock)

    assert final_state == SessionState.COMPLETED
    assert callback_mock.call_count == 3

    states_passed = [call.args[0] for call in callback_mock.call_args_list]
    assert states_passed == [SessionState.IN_PROGRESS, SessionState.AWAITING_INPUT, SessionState.COMPLETED]

def test_poll_until_terminal_transient_error(mock_client):
    mock_client.get_session.side_effect = [
        {"state": "IN_PROGRESS"},
        Exception("Network Error"),
        {"state": "COMPLETED"}
    ]

    monitor = SessionMonitor(client=mock_client, session_id="session/123")

    with patch("time.sleep", return_value=None):
        final_state, data = monitor.poll_until_terminal(interval_seconds=0)

    assert final_state == SessionState.COMPLETED
    assert mock_client.get_session.call_count == 3


def test_session_state_extract_metrics():
    sess_data = {
        "id": "12345",
        "state": "COMPLETED",
        "outputs": [
            {
                "pullRequest": {"url": "https://github.com/org/repo/pull/10", "number": 10},
                "changeSet": {
                    "filesChanged": ["app.py", "test_app.py"],
                    "gitPatch": {
                        "unidiffPatch": "--- a/app.py\n+++ b/app.py\n+line1\n+line2\n-old_line\n"
                    }
                }
            }
        ]
    }
    metrics = SessionState.extract_metrics(sess_data, duration_seconds=42.5)
    assert metrics["session_id"] == "12345"
    assert metrics["state"] == "COMPLETED"
    assert metrics["runtime"] == 42.5
    assert metrics["files_changed"] == 2
    assert metrics["lines_added"] == 2
    assert metrics["lines_removed"] == 1
    assert metrics["pr_url"] == "https://github.com/org/repo/pull/10"


def test_poll_until_terminal_records_telemetry(mock_client):
    mock_client.get_session.side_effect = [
        {"state": "IN_PROGRESS"},
        {"state": "COMPLETED", "id": "sess_99", "outputs": [{"changeSet": {"filesChanged": ["a.py"]}}]}
    ]
    monitor = SessionMonitor(client=mock_client, session_id="session/sess_99")
    with patch("time.sleep", return_value=None), \
         patch("core.local_telemetry.LocalTelemetry.record_session_metrics") as mock_record:
        final_state, data = monitor.poll_until_terminal(interval_seconds=0)
        assert final_state == SessionState.COMPLETED
        mock_record.assert_called_once()
        call_kwargs = mock_record.call_args.kwargs
        assert call_kwargs["session_id"] == "session/sess_99"
        assert call_kwargs["files_changed"] == 1

