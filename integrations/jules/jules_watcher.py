#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
📡 AMB_V2 - Google Jules: Sentinela e Inspetor de Sessões (SRP)
Localização: amb_v2/integrations/jules/jules_watcher.py
Responsabilidade Única: Inspecionar sessões e atividades do Jules em busca de perguntas,
solicitações de aprovação de plano, falhas e PRs pendentes de integração.
"""

import sys
import os
from typing import List, Dict, Any, Optional

from config.bootstrap import ensure_amb_env
ensure_amb_env()

from config import get_env, log_error, get_repo_name  # noqa: E402
from integrations.jules.jules_client import JulesClient  # noqa: E402
from cli_modules.alert_notifier import notify_attention  # noqa: E402


class JulesWatcher:
    """Vigia o estado das sessões do Jules no repositório ativo."""

    FEEDBACK_STATES = {
        "AWAITING_USER_FEEDBACK",
        "Awaiting User Feedback",
        "AWAITING_INPUT",
        "AWAITING_PLAN_APPROVAL",
    }

    TERMINAL_FAILURE_STATES = {
        "FAILED",
        "CANCELLED",
    }

    SUCCESS_STATES = {
        "COMPLETED",
        "SUCCEEDED",
    }

    def __init__(self, client: Optional[JulesClient] = None):
        self.client = client or (JulesClient() if get_env("JULES_API_KEY") else None)
        self.notified_events = set()

    @staticmethod
    def extract_pull_request(session_dict: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Extrai metadados do Pull Request dos outputs da sessão."""
        outputs = session_dict.get("outputs", [])
        if isinstance(outputs, list):
            for item in outputs:
                if isinstance(item, dict) and "pullRequest" in item:
                    return item["pullRequest"]
        elif isinstance(outputs, dict) and "pullRequest" in outputs:
            return outputs["pullRequest"]
        return None

    def check(self) -> List[Dict[str, Any]]:
        """Verifica todas as sessões e retorna alertas detectados."""
        if not self.client:
            return []

        alerts = []
        try:
            repo = get_repo_name()
            sessions = self.client.list_sessions(page_size=30, repo_filter=repo)
            feedback_sessions = []

            for s in sessions:
                session_id = s.get("name", "").split("/")[-1] or s.get("id")
                state = s.get("state", "UNKNOWN")
                if state in self.FEEDBACK_STATES:
                    event_key = f"state_feedback:{session_id}"
                    if event_key not in self.notified_events:
                        feedback_sessions.append(s)

            # Busca em paralelo de atividades para otimizar queries
            activities_cache = {}
            if feedback_sessions and hasattr(self.client, "list_activities_for_sessions"):
                session_ids = [
                    s.get("name", "").split("/")[-1] or s.get("id")
                    for s in feedback_sessions
                ]
                activities_cache = self.client.list_activities_for_sessions(
                    session_ids=session_ids, page_size=20
                )

            for s in sessions:
                session_id = s.get("name", "").split("/")[-1] or s.get("id")
                state = s.get("state", "UNKNOWN")
                title = s.get("title", "Sem título")

                # 1. Sessão que falhou ou foi cancelada
                if state in self.TERMINAL_FAILURE_STATES:
                    event_key = f"failed:{session_id}"
                    if event_key not in self.notified_events:
                        self.notified_events.add(event_key)
                        notify_attention(
                            source="Google Jules",
                            title=f"Sessão falhou ou foi cancelada ({session_id})",
                            details=f"Título: {title}\nEstado: {state}\nPainel: https://jules.google.com/session/{session_id}",
                            action_command=f"amb jules session {session_id}",
                        )
                        alerts.append({"type": "failed", "session_id": session_id})
                    continue

                # 2. Sessão com estado explícito de feedback ou aprovação de plano
                if state in self.FEEDBACK_STATES:
                    acts = activities_cache.get(session_id)
                    if acts is None:
                        try:
                            act_res = self.client.list_activities(
                                session_id=session_id, page_size=20
                            )
                            acts = (
                                act_res
                                if isinstance(act_res, list)
                                else act_res.get("activities", [])
                            )
                        except Exception:
                            acts = []

                    from auto_reply import get_last_conversation_turn

                    turn_info = get_last_conversation_turn(acts)

                    # Se a última mensagem já foi do usuário, não alertar
                    if not turn_info.get("is_awaiting_user_action", True):
                        continue

                    event_key = f"state_feedback:{session_id}:{turn_info.get('last_agent_msg_id')}"
                    if event_key not in self.notified_events:
                        self.notified_events.add(event_key)

                        last_msg = turn_info.get("last_agent_msg", "")
                        msg_detail = (
                            f'❓ Pergunta/Proposta do Agente:\n"{last_msg.strip()}"\n'
                            if last_msg
                            else "O agente finalizou o turno/mudança e aguarda sua instrução para prosseguir.\n"
                        )

                        notify_attention(
                            source="Google Jules",
                            title=f"Sessão aguardando sua resposta: '{title}' ({session_id})",
                            details=f"{msg_detail}Estado: {state}\nPainel: https://jules.google.com/session/{session_id}",
                            action_command=f"amb jules reply -s {session_id}",
                        )
                        alerts.append(
                            {
                                "type": "awaiting_feedback",
                                "session_id": session_id,
                                "text": last_msg,
                            }
                        )

                # 3. Notifica sessões concluídas para conferência e merge de PR
                if state in self.SUCCESS_STATES:
                    pr_info = self.extract_pull_request(s)
                    if pr_info:
                        event_key = f"completed:{session_id}"
                        if event_key not in self.notified_events:
                            self.notified_events.add(event_key)
                            notify_attention(
                                source="Google Jules",
                                title=f"Sessão concluída com PR pendente: '{title}' ({session_id})",
                                details=f"O Jules finalizou o trabalho. Verifique se o PR foi criado e execute o merge.\nPainel: https://jules.google.com/session/{session_id}",
                                action_command=f"amb jules merge -s {session_id}",
                            )
                            alerts.append(
                                {
                                    "type": "completed_needs_merge",
                                    "session_id": session_id,
                                    "pr": pr_info,
                                }
                            )
                    continue

        except Exception as e:
            log_error("JULES-WATCHER", f"Falha na checagem de sessões: {e}")

        return alerts


if __name__ == "__main__":
    w = JulesWatcher()
    al = w.check()
    print(f"Alertas Jules detectados: {len(al)}")
