#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🤖 AMB_V2 - Assistente de Sessão (SRP Core)
Localização: amb_cli/agents/loop_core/session_assistant.py
Responsabilidade Única: Monitorar, aprovar planos e despachar respostas cognitivas (Auto-Reply)
durante o ciclo de vida autônomo de uma sessão no Jules.
"""
import time
from typing import Optional, Dict, Any

from core.bootstrap import ensure_amb_env
ensure_amb_env()

from core import Colors, log, log_error
from integrations.jules.jules_client import JulesClient
from agents.auto_reply import advise_and_reply, get_last_conversation_turn
from integrations.jules.jules_core.plan_auditor import PlanAuditor

POLL_INTERVAL_SECONDS = 8
POST_ACTION_INTERVAL_SECONDS = 3


def monitor_and_assist_session(
    client: JulesClient, session_id: str, auto_reply_ai: bool = True, quiet: bool = False
) -> str:
    """
    Monitora a sessão no Jules, verificando seu estado.
    Se a sessão solicitar feedback, utiliza o AntiGravity SDK para formular uma resposta autônoma e prosseguir.
    """
    if not quiet:
        log("LOOP-MONITOR", f"Iniciando monitoramento da sessão {session_id}...", Colors.CYAN)

    last_state = None
    last_answered_agent_msg_id = None
    plan_challenges_count: Dict[str, int] = {}

    while True:
        try:
            session = client.get_session(session_id)
            state = session.get("state", "UNKNOWN")

            if state != last_state:
                if not quiet:
                    log(
                        "LOOP-MONITOR",
                        f"Sessão {session_id} alterou estado de {last_state} para {state}",
                        Colors.CYAN,
                    )
                last_state = state

            if state in ["COMPLETED", "SUCCEEDED", "CLOSED"]:
                if not quiet:
                    log("LOOP-MONITOR", f"🎉 Sessão {session_id} CONCLUÍDA com sucesso ({state})!", Colors.GREEN)
                return state

            if state in ["FAILED", "ERROR", "ABORTED"]:
                if not quiet:
                    log_error("LOOP-MONITOR", f"Sessão {session_id} encerrou com estado de falha: {state}")
                return state

            is_feedback_state = (
                state in [
                    "AWAITING_USER_FEEDBACK",
                    "Awaiting User Feedback",
                    "AWAITING_USER_ACTION",
                    "AWAITING_INPUT",
                    "AWAITING_PLAN_APPROVAL",
                ]
                or "AWAITING" in (state or "").upper()
            )

            if is_feedback_state:
                log("LOOP-MONITOR", f"Agente pausou aguardando decisão/feedback (Estado: {state}).", Colors.YELLOW)

                acts_resp = client.list_activities(session_id=session_id)
                acts = acts_resp if isinstance(acts_resp, list) else acts_resp.get("activities", [])
                turn_info = get_last_conversation_turn(acts)

                if not turn_info.get("is_awaiting_user_action", True):
                    log(
                        "LOOP-MONITOR",
                        "A última ação já foi do usuário. Aguardando o Jules processar...",
                        Colors.DIM,
                    )
                    time.sleep(POLL_INTERVAL_SECONDS)
                    continue

                if last_answered_agent_msg_id and turn_info.get("last_agent_msg_id") == last_answered_agent_msg_id:
                    log(
                        "LOOP-MONITOR",
                        "A última mensagem do agente já foi respondida recentemente. Aguardando atualização de estado...",
                        Colors.DIM,
                    )
                    time.sleep(POLL_INTERVAL_SECONDS)
                    continue

                if turn_info.get("has_unapproved_plan") and turn_info.get("last_speaker") == "PLAN":
                    # Extrair o texto completo do plano para auditoria
                    plan_text = ""
                    for a in acts:
                        plan_obj = a.get("plan") or a.get("planGenerated", {}).get("plan")
                        if plan_obj:
                            plan_title = plan_obj.get("title", "")
                            steps = plan_obj.get("steps", [])
                            steps_desc = " ".join([s.get("description", "") for s in steps])
                            plan_text = f"{plan_title} {steps_desc}"
                            break

                    is_compliant, feedback = PlanAuditor.audit_plan(plan_text)

                    if not is_compliant and plan_challenges_count.get(session_id, 0) < 1:
                        log("LOOP-MONITOR", f"Plano contestado pela auditoria: {feedback}", Colors.YELLOW)
                        try:
                            client.send_message(session_id, feedback)
                            plan_challenges_count[session_id] = plan_challenges_count.get(session_id, 0) + 1
                        except Exception as e:
                            log_error("LOOP-MONITOR", f"Falha ao enviar feedback corretivo: {e}")
                    else:
                        log(
                            "LOOP-MONITOR",
                            f"Detectado plano pendente: '{turn_info.get('unapproved_plan_title')}'. Aprovando via API...",
                            Colors.CYAN,
                        )
                        try:
                            client.approve_plan(session_id)
                            log("LOOP-MONITOR", "✔ Plano aprovado via API com sucesso.", Colors.GREEN)
                            plan_challenges_count[session_id] = 0
                            last_answered_agent_msg_id = turn_info.get("last_agent_msg_id")
                        except Exception as e:
                            log_error("LOOP-MONITOR", f"Falha ao aprovar plano via client.approve_plan: {e}")
                elif auto_reply_ai and turn_info.get("last_speaker") == "AGENT":
                    log(
                        "LOOP-MONITOR",
                        "Sessão aguarda resposta/dúvida do agente. Acionando Auto-Reply Cognitivo (Gemini)...",
                        Colors.HEADER,
                    )
                    try:
                        advise_and_reply(session_id=session_id, auto_approve=True, force=True)
                        log("LOOP-MONITOR", "✔ Resposta enviada com sucesso para destravar o agente.", Colors.GREEN)
                        last_answered_agent_msg_id = turn_info.get("last_agent_msg_id")
                    except Exception as ar_err:
                        log_error("LOOP-MONITOR", f"Falha no Auto-Reply: {ar_err}")
                time.sleep(POST_ACTION_INTERVAL_SECONDS)
                continue

            time.sleep(POLL_INTERVAL_SECONDS)

        except KeyboardInterrupt:
            raise
        except Exception as e:
            log_error("LOOP-MONITOR", f"Erro ao checar status: {e}")
            time.sleep(POLL_INTERVAL_SECONDS)
