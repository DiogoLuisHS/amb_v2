# -*- coding: utf-8 -*-
"""Unit tests for continuous chat in amb advisor."""

import os
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

_root = Path(__file__).resolve().parent.parent
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))
from core.bootstrap import ensure_amb_env
ensure_amb_env()

from cli_modules.cli_parsers import create_parser
from agents.auto_reply_core.feedback_dispatcher import JulesFeedbackDispatcher
from agents.auto_reply import start_advisor_chat

def test_cli_parser_chat_flag():
    parser = create_parser()
    args = parser.parse_args(["advisor", "--chat"])
    assert getattr(args, "chat", False) is True

    args2 = parser.parse_args(["jules", "reply", "-c"])
    assert getattr(args2, "chat", False) is True


@patch("builtins.input", side_effect=["exit"])
@patch("agents.auto_reply_core.feedback_dispatcher.TurnHistoryExtractor.get_full_session_history")
@patch("core.env.require_env", return_value="dummy_key")
@patch("core.env.get_env", return_value="dummy_key")
def test_continuous_chat_exit(mock_get_env, mock_require_env, mock_history, mock_input):
    dispatcher = JulesFeedbackDispatcher()
    dispatcher.jules_client = MagicMock()
    mock_history.return_value = (None, None, None, None, {"last_agent_msg_id": "123"})
    dispatcher.run_continuous_chat("session_1")
    mock_history.assert_called_once()
    dispatcher.jules_client.send_message.assert_not_called()


@patch("builtins.input", side_effect=["Hello", "q"])
@patch("time.sleep", return_value=None)
@patch("agents.auto_reply_core.feedback_dispatcher.TurnHistoryExtractor.get_full_session_history")
@patch("core.env.require_env", return_value="dummy_key")
@patch("core.env.get_env", return_value="dummy_key")
def test_continuous_chat_send_and_poll(mock_get_env, mock_require_env, mock_history, mock_sleep, mock_input):
    dispatcher = JulesFeedbackDispatcher()
    dispatcher.jules_client = MagicMock()
    mock_history.side_effect = [
        (None, None, None, None, {"last_agent_msg_id": "123"}),
        (None, None, None, None, {"last_agent_msg_id": "124", "last_speaker": "AGENT", "last_agent_msg": "Hi"}),
    ]
    dispatcher.run_continuous_chat("session_1")
    dispatcher.jules_client.send_message.assert_called_once_with(session_id="session_1", message="Hello")
    assert mock_history.call_count == 2


@patch("builtins.input", side_effect=["", KeyboardInterrupt()])
@patch("agents.auto_reply_core.feedback_dispatcher.TurnHistoryExtractor.get_full_session_history")
@patch("core.env.require_env", return_value="dummy_key")
@patch("core.env.get_env", return_value="dummy_key")
def test_continuous_chat_keyboard_interrupt(mock_get_env, mock_require_env, mock_history, mock_input):
    dispatcher = JulesFeedbackDispatcher()
    dispatcher.jules_client = MagicMock()
    mock_history.return_value = (None, None, None, None, {})
    dispatcher.run_continuous_chat("session_1")
    assert mock_input.call_count == 2
    dispatcher.jules_client.send_message.assert_not_called()


@patch("agents.auto_reply_core.feedback_dispatcher.JulesFeedbackDispatcher.run_continuous_chat")
@patch("core.env.require_env", return_value="dummy_key")
@patch("core.env.get_env", return_value="dummy_key")
def test_start_advisor_chat_with_session(mock_get_env, mock_require_env, mock_run):
    start_advisor_chat("session_123")
    mock_run.assert_called_once_with(session_id="session_123")


@patch("builtins.input", side_effect=["1"])
@patch("agents.auto_reply_core.feedback_dispatcher.JulesFeedbackDispatcher.get_pending_sessions")
@patch("agents.auto_reply_core.feedback_dispatcher.JulesFeedbackDispatcher.run_continuous_chat")
@patch("core.env.require_env", return_value="dummy_key")
@patch("core.env.get_env", return_value="dummy_key")
def test_start_advisor_chat_without_session_select_one(mock_get_env, mock_require_env, mock_run, mock_get_pending, mock_input):
    mock_get_pending.return_value = [{"session_id": "sid_1", "title": "S1"}]
    start_advisor_chat()
    mock_run.assert_called_once_with(session_id="sid_1")


@patch("builtins.input", side_effect=["0"])
@patch("agents.auto_reply_core.feedback_dispatcher.JulesFeedbackDispatcher.get_pending_sessions")
@patch("agents.auto_reply_core.feedback_dispatcher.JulesFeedbackDispatcher.run_continuous_chat")
@patch("core.env.require_env", return_value="dummy_key")
@patch("core.env.get_env", return_value="dummy_key")
def test_start_advisor_chat_without_session_exit(mock_get_env, mock_require_env, mock_run, mock_get_pending, mock_input):
    mock_get_pending.return_value = [{"session_id": "sid_1", "title": "S1"}]
    start_advisor_chat()
    mock_run.assert_not_called()
