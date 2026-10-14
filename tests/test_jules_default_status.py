import json
from unittest.mock import patch, MagicMock
from amb_cli.cli_modules.handlers_core.jules_handler import handle_cmd_jules

def test_jules_default_status(capsys: MagicMock) -> None:
    class DummyArgs:
        jules_cmd = None
        json = False
        repo = None

    args = DummyArgs()

    mock_status_data = {
        "api_key_configured": True,
        "api_reachable": True,
        "sources_count": 5,
        "active_repo": "meu_repo",
        "repo_connected": True,
        "sessions_total": 10,
        "sessions_awaiting_feedback": 1,
        "sessions_in_progress": 2,
        "sessions_completed": 5,
        "sessions_failed": 2
    }

    with patch('integrations.jules.jules_client.JulesClient.__init__', return_value=None), \
         patch('integrations.jules.jules_client.JulesClient.get_status', return_value=mock_status_data) as mock_get_status:
        handle_cmd_jules(args)

        out, _ = capsys.readouterr()

        assert "=== ☁️ DIAGNÓSTICO GOOGLE JULES ===" in out
        assert "API Key:" in out
        assert "Configurada" in out
        mock_get_status.assert_called_once()


def test_jules_default_status_json(capsys: MagicMock) -> None:
    class DummyArgs:
        jules_cmd = None
        json = True
        repo = None

    args = DummyArgs()

    mock_status_data = {
        "api_key_configured": True,
        "api_reachable": True,
        "sources_count": 5,
        "active_repo": "meu_repo",
        "repo_connected": True,
        "sessions_total": 10,
        "sessions_awaiting_feedback": 1,
        "sessions_in_progress": 2,
        "sessions_completed": 5,
        "sessions_failed": 2
    }

    with patch('integrations.jules.jules_client.JulesClient.__init__', return_value=None), \
         patch('integrations.jules.jules_client.JulesClient.get_status', return_value=mock_status_data) as mock_get_status:
        handle_cmd_jules(args)

        out, _ = capsys.readouterr()

        parsed_out = json.loads(out)
        assert parsed_out == mock_status_data
        mock_get_status.assert_called_once()

def test_jules_invalid_subcommand(capsys: MagicMock) -> None:
    class DummyArgs:
        jules_cmd = "invalid"

    args = DummyArgs()

    handle_cmd_jules(args)

    out, _ = capsys.readouterr()

    assert "Subcomando do Jules inválido. Use 'amb jules --help'." in out
