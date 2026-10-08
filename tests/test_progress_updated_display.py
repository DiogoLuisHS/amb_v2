import pytest
from unittest.mock import patch, MagicMock

from amb_cli.integrations.jules.jules_core.session_helpers import extract_progress_update
from amb_cli.integrations.jules.jules_watcher import stream_session_activities
from amb_cli.core import Colors

def test_extract_progress_update_full():
    act = {
        "progressUpdated": {
            "title": "Installing dependencies",
            "description": "Running npm install"
        }
    }
    assert extract_progress_update(act) == ("Installing dependencies", "Running npm install")

def test_extract_progress_update_title_only():
    act = {
        "progressUpdated": {
            "title": "Compiling project "
        }
    }
    assert extract_progress_update(act) == ("Compiling project", "")

def test_extract_progress_update_desc_only():
    act = {
        "progressUpdated": {
            "description": " Just some desc "
        }
    }
    assert extract_progress_update(act) == ("", "Just some desc")

def test_extract_progress_update_missing():
    act = {
        "description": "Some generic action",
        "type": "bash"
    }
    assert extract_progress_update(act) is None

def test_extract_progress_update_empty_dict():
    act = {
        "progressUpdated": {}
    }
    assert extract_progress_update(act) is None


@patch("amb_cli.integrations.jules.jules_watcher.SessionMonitor")
@patch("amb_cli.integrations.jules.jules_watcher.JulesClient")
@patch("builtins.print")
def test_stream_session_activities_progress_updated(mock_print, MockJulesClient, MockSessionMonitor):
    mock_client = MagicMock()
    mock_client.get_session.return_value = {"title": "Test Sess", "state": "IN_PROGRESS"}

    mock_monitor = MagicMock()
    MockSessionMonitor.return_value = mock_monitor

    # We will trigger the on_tick_callback manually using a side effect or just capture it
    def fake_poll(interval_seconds, on_tick, stop_condition):
        # Fake session state
        class FakeState:
            def is_awaiting_feedback(self): return False
            def is_success(self): return False
            def __eq__(self, other): return False

        # Give some activities
        mock_client.list_activities.return_value = [
            {
                "id": "act1",
                "createTime": "2023-10-10T12:00:00Z",
                "progressUpdated": {
                    "title": "Working on it",
                    "description": "Doing hard stuff"
                }
            }
        ]
        on_tick(FakeState(), {"state": "IN_PROGRESS"})

    mock_monitor.poll_until_terminal.side_effect = fake_poll

    stream_session_activities("sessions/123", client=mock_client)

    # Check if print was called with the right format
    # The expected output string:
    ctime = "2023-10-10 12:00:00"
    expected_str = f"{Colors.BOLD}{Colors.CYAN}[{ctime}] ⏳ Working on it{Colors.RESET}{Colors.DIM} — Doing hard stuff{Colors.RESET}"

    mock_print.assert_any_call(expected_str)
