# -*- coding: utf-8 -*-
"""Unit tests for agents/auto_reply.py."""

import os
import sys
from pathlib import Path

# Add project root to sys.path
_root = Path(__file__).resolve().parent.parent
for sub in ["config", "agents", "architecture", "pipeline", "integrations"]:
    p = str(_root / sub)
    if p not in sys.path:
        sys.path.insert(0, p)
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))

from auto_reply import extract_activity_text, get_last_conversation_turn


def test_extract_activity_text_agent_dict():
    activity = {
        "agentMessaged": {
            "agentMessage": "Qual a porta do servidor?"
        }
    }
    assert extract_activity_text(activity, role="agent") == "Qual a porta do servidor?"


def test_extract_activity_text_agent_text_key():
    activity = {
        "agentMessaged": {
            "text": "Executando migrações..."
        }
    }
    assert extract_activity_text(activity, role="agent") == "Executando migrações..."


def test_extract_activity_text_agent_direct_string():
    activity = {
        "agentMessaged": "Pronto para iniciar."
    }
    assert extract_activity_text(activity, role="agent") == "Pronto para iniciar."


def test_extract_activity_text_user_message():
    activity = {
        "userMessaged": {
            "userMessage": "Pode usar a porta 3000."
        }
    }
    assert extract_activity_text(activity, role="user") == "Pode usar a porta 3000."


def test_extract_activity_text_empty_and_mismatch():
    assert extract_activity_text({}, role="agent") == ""
    assert extract_activity_text({"userMessaged": "Olá"}, role="agent") == ""


def test_get_last_conversation_turn_user_last():
    acts = [
        {"id": "act-2", "userMessaged": {"userMessage": "Sim, confirmado."}},
        {"id": "act-1", "agentMessaged": {"agentMessage": "Posso prosseguir?"}},
    ]
    turn = get_last_conversation_turn(acts)
    assert turn["is_awaiting_user_action"] is False
    assert turn["last_user_msg"] == "Sim, confirmado."


def test_get_last_conversation_turn_agent_last():
    acts = [
        {"id": "act-2", "agentMessaged": {"agentMessage": "Preciso de permissão para criar arquivo."}},
        {"id": "act-1", "userMessaged": {"userMessage": "Inicie o projeto."}},
    ]
    turn = get_last_conversation_turn(acts)
    assert turn["is_awaiting_user_action"] is True
    assert turn["last_agent_msg"] == "Preciso de permissão para criar arquivo."


def test_get_last_conversation_turn_pending_plan():
    acts = [
        {
            "id": "act-3",
            "planGenerated": {
                "plan": {
                    "title": "Refatoração de Schemas",
                    "state": "PENDING_USER_APPROVAL"
                }
            }
        },
        {"id": "act-1", "userMessaged": {"userMessage": "Analise os schemas."}},
    ]
    turn = get_last_conversation_turn(acts)
    assert turn["is_awaiting_user_action"] is True
    assert turn["has_unapproved_plan"] is True
    assert turn["unapproved_plan_title"] == "Refatoração de Schemas"
