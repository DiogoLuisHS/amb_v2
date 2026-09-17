import sys
import pytest
from unittest.mock import patch, MagicMock

from amb_cli.cli_modules.alert_notifier import play_beep, notify_attention, notify_info

def test_play_beep_win32():
    with patch("sys.platform", "win32"):
        with patch.dict("sys.modules", {"winsound": MagicMock()}):
            play_beep()
            # If no exception, it works gracefully

def test_play_beep_non_win32(capsys):
    with patch("sys.platform", "linux"):
        play_beep()
        captured = capsys.readouterr()
        assert captured.out == "\a"

def test_play_beep_exception(capsys):
    with patch("sys.platform", "win32"):
        # Make the import fail
        with patch.dict("sys.modules", {"winsound": None}):
            # Should not raise exception
            play_beep()
            captured = capsys.readouterr()
            assert captured.out == ""

@patch("amb_cli.cli_modules.alert_notifier.play_beep")
def test_notify_attention_without_action(mock_play_beep, capsys):
    notify_attention(
        source="TEST_SOURCE",
        title="Test Title",
        details="Test Details"
    )

    mock_play_beep.assert_called_once()
    captured = capsys.readouterr()

    assert "[ATENÇÃO REQUERIDA] — FONTE: TEST_SOURCE" in captured.out
    assert "MOTIVO:" in captured.out
    assert "Test Title" in captured.out
    assert "Test Details" in captured.out
    assert "COMANDO PARA RESPONDER/AGIR" not in captured.out

@patch("amb_cli.cli_modules.alert_notifier.play_beep")
def test_notify_attention_with_action(mock_play_beep, capsys):
    notify_attention(
        source="TEST_SOURCE",
        title="Test Title",
        details="Test Details",
        action_command="do something"
    )

    mock_play_beep.assert_called_once()
    captured = capsys.readouterr()

    assert "[ATENÇÃO REQUERIDA] — FONTE: TEST_SOURCE" in captured.out
    assert "COMANDO PARA RESPONDER/AGIR:" in captured.out
    assert "do something" in captured.out

def test_notify_info(capsys):
    notify_info("Test Message Info")
    captured = capsys.readouterr()
    assert "✔ Test Message Info" in captured.out
