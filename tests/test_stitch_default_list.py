import pytest
import json
from unittest.mock import MagicMock, patch
from amb_cli.cli_modules.handlers_core.stitch_handler import handle_cmd_stitch

class DummyArgs:
    def __init__(self, stitch_cmd=None, json=False, project_id=None):
        self.stitch_cmd = stitch_cmd
        self.json = json
        self.project_id = project_id

@patch("integrations.stitch.stitch_client.StitchClient")
def test_stitch_default_list_formatted(mock_stitch_client_cls, capsys):
    # Setup mock
    mock_client = MagicMock()
    mock_stitch_client_cls.return_value = mock_client

    mock_client.list_screens.return_value = [
        {"id": "screen1", "title": "Dashboard", "width": 1920, "height": 1080, "description": "Main dash"},
        {"id": "screen2", "title": "Login"}
    ]

    args = DummyArgs(stitch_cmd=None)
    handle_cmd_stitch(args)

    mock_client.list_screens.assert_called_once_with(project_id=None)

    captured = capsys.readouterr()
    output = captured.out

    assert "=== TELAS DO PROJETO STITCH (2 encontrada(s)) ===" in output
    assert "screen1" in output
    assert "Dashboard" in output
    assert "(1920x1080)" in output
    assert "- Main dash" in output
    assert "screen2" in output
    assert "Login" in output

@patch("integrations.stitch.stitch_client.StitchClient")
def test_stitch_default_list_json(mock_stitch_client_cls, capsys):
    # Setup mock
    mock_client = MagicMock()
    mock_stitch_client_cls.return_value = mock_client

    mock_screens = [
        {"id": "screen1", "title": "Dashboard"}
    ]
    mock_client.list_screens.return_value = mock_screens

    args = DummyArgs(stitch_cmd=None, json=True)
    handle_cmd_stitch(args)

    mock_client.list_screens.assert_called_once_with(project_id=None)

    captured = capsys.readouterr()
    output = captured.out

    parsed_json = json.loads(output)
    assert parsed_json == mock_screens
