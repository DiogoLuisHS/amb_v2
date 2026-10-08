import pytest
from unittest.mock import MagicMock, patch
from amb_cli.integrations.jules.jules_core.session_helpers import check_branch_exists_in_source
from amb_cli.integrations.jules.tools.create_session import run_create_session

def test_check_branch_exists_in_source_existing():
    source_data = {
        "githubRepo": {
            "defaultBranch": {"displayName": "main"},
            "branches": [
                {"displayName": "main"},
                {"displayName": "feature-123"}
            ]
        }
    }
    exists, default_branch = check_branch_exists_in_source(source_data, "feature-123")
    assert exists is True
    assert default_branch == "main"

def test_check_branch_exists_in_source_missing():
    source_data = {
        "githubRepo": {
            "defaultBranch": {"displayName": "main"},
            "branches": [
                {"displayName": "main"},
                {"displayName": "feature-123"}
            ]
        }
    }
    exists, default_branch = check_branch_exists_in_source(source_data, "missing-branch")
    assert exists is False
    assert default_branch == "main"

def test_check_branch_exists_in_source_empty_branches():
    source_data = {
        "githubRepo": {
            "defaultBranch": {"displayName": "main"},
            "branches": []
        }
    }
    exists, default_branch = check_branch_exists_in_source(source_data, "some-branch")
    assert exists is True
    assert default_branch == "main"

@patch('amb_cli.integrations.jules.tools.create_session.JulesClient')
@patch('amb_cli.integrations.jules.tools.create_session.check_branch_exists_in_source')
def test_run_create_session_alert_preventive(mock_check_branch, MockJulesClient, capsys):
    mock_client = MockJulesClient.return_value
    mock_client.create_session.return_value = {"name": "sessions/123", "id": "123"}
    mock_client.get_source.return_value = {"fake": "source"}

    mock_check_branch.return_value = (False, "main")

    # Executar e verificar comportamento (não deve quebrar)
    res = run_create_session(
        prompt="Test prompt",
        base_branch="missing-branch",
        source_name="sources/github/test/test",
        client=mock_client
    )

    assert res["id"] == "123"
    mock_check_branch.assert_called_once()

    # Verificar se o alerta preventivo foi exibido (se existir na saída)
    captured = capsys.readouterr()
    assert "Aviso: A branch 'missing-branch' não foi encontrada" in captured.out
    assert "Branch padrão detectada: 'main'" in captured.out


@patch('amb_cli.integrations.jules.tools.create_session.JulesClient')
def test_run_create_session_skip_branch_check(MockJulesClient):
    mock_client = MockJulesClient.return_value
    mock_client.create_session.return_value = {"name": "sessions/123", "id": "123"}

    with patch('amb_cli.integrations.jules.tools.create_session.check_branch_exists_in_source') as mock_check_branch:
        # Quando skip_branch_check for True, get_source/check_branch... não devem ser chamados
        run_create_session(
            prompt="Test prompt",
            base_branch="missing-branch",
            source_name="sources/github/test/test",
            client=mock_client,
            skip_branch_check=True
        )

        mock_check_branch.assert_not_called()
        mock_client.get_source.assert_not_called()

@patch('amb_cli.integrations.jules.tools.create_session.JulesClient')
def test_run_create_session_get_source_exception(MockJulesClient):
    mock_client = MockJulesClient.return_value
    mock_client.create_session.return_value = {"name": "sessions/123", "id": "123"}
    # Simular falha em get_source
    mock_client.get_source.side_effect = Exception("Not found")

    with patch('amb_cli.integrations.jules.tools.create_session.check_branch_exists_in_source') as mock_check_branch:
        # A exceção deve ser tratada silenciosamente e não quebrar a execução
        run_create_session(
            prompt="Test prompt",
            base_branch="missing-branch",
            source_name="sources/github/test/test",
            client=mock_client
        )

        mock_check_branch.assert_not_called()
        mock_client.create_session.assert_called_once()
