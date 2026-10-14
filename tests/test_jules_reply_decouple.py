import pytest
from unittest.mock import patch, MagicMock
from amb_cli.cli_modules.handlers_core.jules_handler import handle_cmd_jules

class DummyArgs:
    def __init__(self, **kwargs):
        self.jules_cmd = "reply"
        self.session_id_flag = None
        self.session_id = None
        self.chat = False
        self.message = None
        self.auto_approve = False
        self.force = False
        for k, v in kwargs.items():
            setattr(self, k, v)

@patch("cli_modules.cli_handlers.cmd_advisor")
def test_jules_reply_no_id_delegates_to_hub(mock_cmd_advisor):
    """
    Chamada a `amb jules reply` sem ID delegando com sucesso para `cmd_advisor`.
    """
    args = DummyArgs()

    handle_cmd_jules(args)

    mock_cmd_advisor.assert_called_once_with(args)

@patch("agents.auto_reply.advise_and_reply")
@patch("integrations.jules.jules_client.JulesClient")
def test_jules_reply_with_id_calls_advise(mock_jules_client, mock_advise_and_reply):
    """
    Chamada a `amb jules reply <id>` mantendo o comportamento de consulta e resposta pontual.
    """
    mock_jules_client.normalize_session_id.return_value = "session-123"
    args = DummyArgs(session_id="session-123")

    handle_cmd_jules(args)

    mock_jules_client.normalize_session_id.assert_called_once_with("session-123")
    mock_advise_and_reply.assert_called_once_with(session_id="session-123", auto_approve=False)

@patch("integrations.jules.tools.send_message.run_send_message")
@patch("integrations.jules.jules_client.JulesClient")
def test_jules_reply_with_id_and_message_calls_send_message(mock_jules_client, mock_run_send_message):
    """
    Chamada a `amb jules reply <id> -m "msg"` mantendo o envio direto da mensagem.
    """
    mock_jules_client.normalize_session_id.return_value = "session-123"
    args = DummyArgs(session_id="session-123", message="hello world", force=True)

    handle_cmd_jules(args)

    mock_jules_client.normalize_session_id.assert_called_once_with("session-123")
    mock_run_send_message.assert_called_once_with(session_id="session-123", message="hello world", force=True)

@patch("amb_cli.cli_modules.handlers_core.jules_handler.log_error")
def test_jules_reply_message_without_id_logs_error(mock_log_error):
    """
    Erro amigável ao tentar passar `--message` sem especificar o ID da sessão.
    """
    args = DummyArgs(message="hello world")

    handle_cmd_jules(args)

    mock_log_error.assert_called_once_with("JULES", "Informe o ID da sessão ao usar --message direta.")
