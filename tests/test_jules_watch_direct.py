import pytest
from unittest.mock import patch, MagicMock
from amb_cli.cli_modules.handlers_core.jules_handler import handle_cmd_jules

class ArgsMock:
    def __init__(self, jules_cmd, session_id=None, session_id_flag=None, json=False):
        self.jules_cmd = jules_cmd
        self.session_id = session_id
        self.session_id_flag = session_id_flag
        self.json = json

def test_jules_watch_direct_success():
    args = ArgsMock(jules_cmd="watch", session_id="sess-123", json=False)
    with patch("integrations.jules.tools.get_session.run_get_session") as mock_run:
        handle_cmd_jules(args)
        mock_run.assert_called_once_with(session_id="sess-123", watch=True, as_json=False)

def test_jules_logs_alias_success():
    args = ArgsMock(jules_cmd="logs", session_id="sess-456", json=True)
    with patch("integrations.jules.tools.get_session.run_get_session") as mock_run:
        handle_cmd_jules(args)
        mock_run.assert_called_once_with(session_id="sess-456", watch=True, as_json=True)

def test_jules_watch_missing_session_id():
    args = ArgsMock(jules_cmd="watch", session_id=None)
    with patch("amb_cli.cli_modules.handlers_core.jules_handler.log_error") as mock_log_error:
        handle_cmd_jules(args)
        mock_log_error.assert_called_once_with("JULES", "Informe o ID da sessão para acompanhar os logs.")

def test_jules_watch_session_id_flag():
    args = ArgsMock(jules_cmd="watch", session_id=None, session_id_flag="sess-789", json=False)
    with patch("integrations.jules.tools.get_session.run_get_session") as mock_run:
        handle_cmd_jules(args)
        mock_run.assert_called_once_with(session_id="sess-789", watch=True, as_json=False)
