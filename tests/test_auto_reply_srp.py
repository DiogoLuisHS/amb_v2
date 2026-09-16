# -*- coding: utf-8 -*-
"""Unit tests for agents/auto_reply_core (SRP decomposition)."""

import sys
from pathlib import Path
from unittest.mock import MagicMock

_root = Path(__file__).resolve().parent.parent
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))
from config.bootstrap import ensure_amb_env
ensure_amb_env()

from agents.auto_reply_core import (
    TurnHistoryExtractor,
    CognitiveAdvisor,
    JulesFeedbackDispatcher,
)


# ---------------------------------------------------------------------------
# Tests for TurnHistoryExtractor
# ---------------------------------------------------------------------------

def test_turn_extractor_activity_text():
    act_agent = {"agentMessaged": {"text": "Qual a porta do servidor?"}}
    assert TurnHistoryExtractor.extract_activity_text(act_agent, role="agent") == "Qual a porta do servidor?"

    act_user = {"userMessaged": {"userMessage": "Porta 8080."}}
    assert TurnHistoryExtractor.extract_activity_text(act_user, role="user") == "Porta 8080."


def test_turn_extractor_last_turn():
    acts = [
        {"id": "a2", "agentMessaged": {"text": "Deseja que eu crie o arquivo?"}},
        {"id": "a1", "userMessaged": {"text": "Comece pelo schema."}},
    ]
    turn = TurnHistoryExtractor.get_last_conversation_turn(acts)
    assert turn["last_speaker"] == "AGENT"
    assert turn["is_awaiting_user_action"] is True
    assert turn["last_agent_msg"] == "Deseja que eu crie o arquivo?"


def test_turn_extractor_full_history():
    mock_jules = MagicMock()
    mock_jules.get_session.return_value = {"title": "Fix bug", "prompt": "Conserte o bug de tipagem"}
    mock_jules.list_activities.return_value = [
        {"id": "1", "agentMessaged": {"text": "Posso abrir o PR?"}, "createTime": "2026-09-16T12:00:00Z"}
    ]

    session, prompt, history, question, turn_info = TurnHistoryExtractor.get_full_session_history(
        mock_jules, "session-123"
    )
    assert session["title"] == "Fix bug"
    assert "Conserte o bug" in prompt
    assert question == "Posso abrir o PR?"
    assert turn_info["is_awaiting_user_action"] is True


# ---------------------------------------------------------------------------
# Tests for CognitiveAdvisor
# ---------------------------------------------------------------------------

def test_cognitive_advisor_filter_rules():
    rules_text = """# Regras de Tipagem
- Usar TypeScript estrito.

## Version Control Rules
- Nunca faça push direto para main.
- Não altere histórico.

## Arquitetura
- Seguir SRP rigorosamente.
"""
    filtered = CognitiveAdvisor.filter_rules_for_jules(rules_text)
    assert "Regras de Tipagem" in filtered
    assert "Seguir SRP rigorosamente" in filtered
    assert "Version Control Rules" not in filtered
    assert "Nunca faça push" not in filtered


def test_cognitive_advisor_fallback():
    mock_antigravity = MagicMock()
    mock_antigravity.generate_text.side_effect = Exception("API Quota Error")

    advisor = CognitiveAdvisor(antigravity_client=mock_antigravity)
    suggestion = advisor.generate_suggestion(
        session_title="Refactor",
        initial_prompt="Refatore as rotas",
        full_chat_history="",
        current_question="Should I proceed to open the PR?",
    )
    assert "proceed to open the Pull Request" in suggestion


# ---------------------------------------------------------------------------
# Tests for JulesFeedbackDispatcher
# ---------------------------------------------------------------------------

def test_feedback_dispatcher_send_reply():
    mock_jules = MagicMock()
    dispatcher = JulesFeedbackDispatcher(jules_client=mock_jules)

    dispatcher.send_reply("sess-1", "Olá Jules!")
    mock_jules.send_message.assert_called_once_with(session_id="sess-1", message="Olá Jules!")


def test_feedback_dispatcher_approve_plan():
    mock_jules = MagicMock()
    dispatcher = JulesFeedbackDispatcher(jules_client=mock_jules)

    dispatcher.approve_plan("sess-1")
    mock_jules.approve_plan.assert_called_once_with("sess-1")
