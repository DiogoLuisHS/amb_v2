import pytest
import sys
import io
from unittest.mock import MagicMock
from integrations.jules.tools.get_session import run_get_session

class MockJulesClient:
    def __init__(self, mock_data):
        self.mock_data = mock_data

    def normalize_session_id(self, session_id):
        return session_id

    def get_session(self, session_id):
        return self.mock_data

    @staticmethod
    def extract_pull_request(data):
        return data.get("pull_request", {})


def test_run_get_session_with_timestamps(capsys):
    mock_data = {
        "name": "sessions/sess_12345",
        "id": "sess_12345",
        "state": "COMPLETED",
        "title": "Test Session",
        "createTime": "2023-10-27T10:00:00Z",
        "updateTime": "2023-10-27T10:05:00Z",
    }
    client = MockJulesClient(mock_data)

    run_get_session("sess_12345", watch=False, as_json=False, client=client)

    captured = capsys.readouterr()
    output = captured.out

    assert "Criada em:     2023-10-27T10:00:00Z" in output
    assert "Atualizada em: 2023-10-27T10:05:00Z" in output
    assert "Painel Web:  https://jules.google.com/session/sess_12345" in output


def test_run_get_session_without_timestamps(capsys):
    mock_data = {
        "name": "sessions/sess_12345",
        "id": "sess_12345",
        "state": "COMPLETED",
        "title": "Test Session",
    }
    client = MockJulesClient(mock_data)

    run_get_session("sess_12345", watch=False, as_json=False, client=client)

    captured = capsys.readouterr()
    output = captured.out

    assert "Criada em:" not in output
    assert "Atualizada em:" not in output
    assert "Painel Web:  https://jules.google.com/session/sess_12345" in output


def test_run_get_session_json_mode(capsys):
    mock_data = {
        "name": "sessions/sess_12345",
        "id": "sess_12345",
        "state": "COMPLETED",
        "title": "Test Session",
        "createTime": "2023-10-27T10:00:00Z",
        "updateTime": "2023-10-27T10:05:00Z",
    }
    client = MockJulesClient(mock_data)

    result = run_get_session("sess_12345", watch=False, as_json=True, client=client)

    captured = capsys.readouterr()
    output = captured.out

    assert '"createTime": "2023-10-27T10:00:00Z"' in output
    assert '"updateTime": "2023-10-27T10:05:00Z"' in output
    assert "Criada em:" not in output  # Text formatting should not be printed

    assert result == mock_data
