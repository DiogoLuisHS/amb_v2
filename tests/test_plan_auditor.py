import pytest
from amb_cli.integrations.jules.jules_core.plan_auditor import PlanAuditor

def test_audit_plan_valid():
    plan_text = "I will write a unit test for this using pytest. Also, I will ensure the file respects the 300 linhas rule."
    is_compliant, feedback = PlanAuditor.audit_plan(plan_text)
    assert is_compliant is True
    assert feedback == ""

def test_audit_plan_missing_tests():
    plan_text = "I will fix the bug and keep it under 300 lines."
    is_compliant, feedback = PlanAuditor.audit_plan(plan_text)
    assert is_compliant is False
    assert feedback == "Atenção às regras de engenharia do AGENTS.md: certifique-se de incluir a criação de testes unitários em pytest e garantir que nenhum arquivo ultrapasse o limite de 300 linhas."

def test_audit_plan_missing_rules():
    plan_text = "I will write a pytest to verify this."
    is_compliant, feedback = PlanAuditor.audit_plan(plan_text)
    assert is_compliant is False
    assert feedback == "Atenção às regras de engenharia do AGENTS.md: certifique-se de incluir a criação de testes unitários em pytest e garantir que nenhum arquivo ultrapasse o limite de 300 linhas."

def test_audit_plan_missing_both():
    plan_text = "I will just write the code."
    is_compliant, feedback = PlanAuditor.audit_plan(plan_text)
    assert is_compliant is False
    assert feedback == "Atenção às regras de engenharia do AGENTS.md: certifique-se de incluir a criação de testes unitários em pytest e garantir que nenhum arquivo ultrapasse o limite de 300 linhas."

from unittest.mock import MagicMock, patch
from amb_cli.agents.loop_core.session_assistant import monitor_and_assist_session


@patch("amb_cli.agents.loop_core.session_assistant.get_last_conversation_turn")
@patch("amb_cli.agents.loop_core.session_assistant.time.sleep", return_value=None)
@patch("amb_cli.agents.loop_core.session_assistant.log")
@patch("amb_cli.agents.loop_core.session_assistant.log_error")
def test_session_monitor_integration_valid_plan(mock_log_error, mock_log, mock_sleep, mock_turn):
    mock_turn.return_value = {'is_awaiting_user_action': True, 'has_unapproved_plan': True, 'last_speaker': 'PLAN', 'last_agent_msg_id': 'act_1', 'unapproved_plan_title': 'Plan'}
    client = MagicMock()

    client.get_session.side_effect = [
        {"state": "AWAITING_PLAN_APPROVAL"},
        {"state": "COMPLETED"}
    ]

    valid_plan_act = {
        "id": "act_1",
        "plan": {
            "title": "Fix bug",
            "steps": [
                {"description": "Write pytest"},
                {"description": "Keep it under 300 linhas"}
            ]
        }
    }

    client.list_activities.return_value = [valid_plan_act]

    res = monitor_and_assist_session(client, "sess_1")

    assert res == "COMPLETED"
    client.approve_plan.assert_called_once_with("sess_1")
    client.send_message.assert_not_called()

@patch("amb_cli.agents.loop_core.session_assistant.get_last_conversation_turn")
@patch("amb_cli.agents.loop_core.session_assistant.time.sleep", return_value=None)
@patch("amb_cli.agents.loop_core.session_assistant.log")
@patch("amb_cli.agents.loop_core.session_assistant.log_error")
def test_session_monitor_integration_invalid_plan_challenge(mock_log_error, mock_log, mock_sleep, mock_turn):
    mock_turn.return_value = {'is_awaiting_user_action': True, 'has_unapproved_plan': True, 'last_speaker': 'PLAN', 'last_agent_msg_id': 'act_1', 'unapproved_plan_title': 'Plan'}
    client = MagicMock()

    # Simulates: AWAITING -> we send message, circuit breaker triggers
    # Next loop iteration: it's still AWAITING -> but circuit breaker is active, so we approve
    # Next loop iteration: it's COMPLETED
    client.get_session.side_effect = [
        {"state": "AWAITING_PLAN_APPROVAL"},
        {"state": "AWAITING_PLAN_APPROVAL"},
        {"state": "COMPLETED"}
    ]

    invalid_plan_act = {
        "id": "act_1",
        "plan": {
            "title": "Fix bug",
            "steps": [
                {"description": "Just writing code"}
            ]
        }
    }

    client.list_activities.return_value = [invalid_plan_act]

    res = monitor_and_assist_session(client, "sess_1")

    assert res == "COMPLETED"

    client.send_message.assert_called_once()
    assert client.send_message.call_args[0][1] == "Atenção às regras de engenharia do AGENTS.md: certifique-se de incluir a criação de testes unitários em pytest e garantir que nenhum arquivo ultrapasse o limite de 300 linhas."

    client.approve_plan.assert_called_once_with("sess_1")
