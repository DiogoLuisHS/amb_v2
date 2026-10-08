import pytest
from unittest.mock import patch, MagicMock

from integrations.jules.jules_client import JulesClient
from cli_modules.handlers_core.jules_handler import handle_cmd_jules
from integrations.jules.tools.create_session import run_create_session

class ArgsMock:
    def __init__(self, **kwargs):
        self.jules_cmd = "create"
        self.prompt = "Create a test session"
        self.title = None
        self.branch = None
        self.source = None
        self.json = False
        self.no_auto_pr = False
        self.require_approval = False
        self.no_repo = False
        for k, v in kwargs.items():
            setattr(self, k, v)


@patch("integrations.jules.jules_client.JulesClient._request")
def test_jules_client_create_session_repoless(mock_request):
    """
    Testa se ao passar repoless=True o payload JSON é construído
    SEM o campo sourceContext e SEM automationMode.
    """
    client = JulesClient(api_key="fake-key")

    # Mock para não ler arquivo real caso confunda o prompt
    with patch("os.path.isfile", return_value=False):
        client.create_session(
            prompt="Hello world",
            repoless=True,
            automation_mode="AUTO_CREATE_PR"
        )

    mock_request.assert_called_once()
    args, kwargs = mock_request.call_args
    assert args[0] == "POST"
    assert args[1] == "sessions"

    payload = kwargs.get("data", {})
    assert "prompt" in payload
    assert payload["prompt"] == "Hello world"
    assert "sourceContext" not in payload
    assert "automationMode" not in payload


@patch("integrations.jules.jules_client.JulesClient._request")
@patch("workspace.get_repo_name", return_value="owner/repo")
@patch("integrations.git.git_service.GitService.get_current_branch", return_value="main")
def test_jules_client_create_session_standard(mock_branch, mock_repo, mock_request):
    """
    Testa a criação de sessão padrão (repoless=False) preservando sourceContext.
    """
    client = JulesClient(api_key="fake-key")

    with patch("os.path.isfile", return_value=False):
        client.create_session(
            prompt="Hello normal",
            repoless=False,
            automation_mode="AUTO_CREATE_PR"
        )

    mock_request.assert_called_once()
    args, kwargs = mock_request.call_args

    payload = kwargs.get("data", {})
    assert "sourceContext" in payload
    assert payload["sourceContext"]["source"] == "sources/github/owner/repo"
    assert "automationMode" in payload
    assert payload["automationMode"] == "AUTO_CREATE_PR"


@patch("integrations.jules.tools.create_session.run_create_session")
def test_jules_handler_repoless_flag(mock_run_create_session):
    """
    Testa o repasse da flag --no-repo a partir do handler jules_handler para o run_create_session.
    """
    args = ArgsMock(no_repo=True)
    handle_cmd_jules(args)

    mock_run_create_session.assert_called_once()
    kwargs = mock_run_create_session.call_args[1]
    assert kwargs.get("repoless") is True

@patch("integrations.jules.tools.create_session.run_create_session")
def test_jules_handler_repoless_flag_false(mock_run_create_session):
    """
    Testa o repasse da flag --no-repo=False a partir do handler jules_handler.
    """
    args = ArgsMock(no_repo=False)
    handle_cmd_jules(args)

    mock_run_create_session.assert_called_once()
    kwargs = mock_run_create_session.call_args[1]
    assert kwargs.get("repoless") is False
