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

from core.bootstrap import ensure_amb_env
ensure_amb_env()

from core import get_env, log_error
from workspace import get_repo_name  # noqa: E402
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
    def extract_pull_request(session_dict: Dict[str, Any], activities: Optional[List[Dict[str, Any]]] = None) -> Optional[Dict[str, Any]]:
        """Extrai metadados do Pull Request dos outputs da sessão ou das atividades via JulesClient."""
        return JulesClient.extract_pull_request(session_dict, activities=activities)

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


def stream_session_activities(session_id: str, poll_interval: int = 4, client: Optional[JulesClient] = None) -> None:
    """Faz streaming ao vivo das atividades e saídas da sessão do Jules no terminal."""
    import time
    from core import Colors, log
    from auto_reply_core.turn_extractor import TurnHistoryExtractor

    c = client or JulesClient()
    clean_id = session_id.split("/")[-1]

    try:
        sess = c.get_session(clean_id)
        title = sess.get("title", "Sem título")
        state = sess.get("state", "UNKNOWN")
    except Exception as e:
        log_error("JULES-STREAM", f"Falha ao carregar sessão {clean_id}: {e}")
        return

    print("\n" + "=" * 75)
    print(f"📡 {Colors.BOLD}{Colors.CYAN}STREAMING AO VIVO DA SESSÃO JULES{Colors.RESET}")
    print(f"  • ID:     {Colors.BOLD}{clean_id}{Colors.RESET}")
    print(f"  • Título: {title}")
    print(f"  • Estado: {Colors.BOLD}{state}{Colors.RESET}")
    print(f"  • Painel: https://jules.google.com/session/{clean_id}")
    print("=" * 75)
    print(f"{Colors.DIM}Pressione Ctrl+C para encerrar o acompanhamento.{Colors.RESET}\n")

    seen_ids = set()

    try:
        while True:
            try:
                # Atualiza dados da sessão
                sess = c.get_session(clean_id)
                current_state = sess.get("state", "UNKNOWN")

                # Obtém atividades
                act_res = c.list_activities(clean_id, page_size=25)
                acts = act_res.get("activities", []) if isinstance(act_res, dict) else (act_res if isinstance(act_res, list) else [])

                # Processa da mais antiga para a mais recente
                for act in reversed(acts):
                    aid = act.get("id") or act.get("name")
                    if aid and aid not in seen_ids:
                        seen_ids.add(aid)
                        ctime = act.get("createTime", "")[:19].replace("T", " ")
                        originator = (act.get("originator") or "agent").lower()

                        # 1. Mensagem do Usuário
                        user_txt = TurnHistoryExtractor.extract_activity_text(act, role="user")
                        if user_txt:
                            print(f"{Colors.BOLD}{Colors.BLUE}[{ctime}] 👤 USUÁRIO:{Colors.RESET} {user_txt}")
                            continue

                        # 2. Mensagem ou Pergunta do Agente
                        agent_txt = TurnHistoryExtractor.extract_activity_text(act, role="agent")
                        if agent_txt:
                            print(f"{Colors.BOLD}{Colors.GREEN}[{ctime}] 🤖 JULES:{Colors.RESET} {agent_txt}")
                            continue

                        # 3. Plano de Ação Gerado
                        if "planGenerated" in act:
                            plan = act["planGenerated"]
                            steps = plan.get("steps", []) if isinstance(plan, dict) else []
                            print(f"{Colors.BOLD}{Colors.YELLOW}[{ctime}] 📋 PLANO GERADO PELO AGENTE ({len(steps)} passos):{Colors.RESET}")
                            for idx, step in enumerate(steps, 1):
                                desc = step.get("description") or str(step)
                                print(f"    {idx}. {desc}")
                            continue

                        # 4. Ação genérica ou bash command
                        desc = act.get("description") or act.get("type") or "Atividade"
                        print(f"{Colors.DIM}[{ctime}] ⚙️  {desc}{Colors.RESET}")

                # Checa se entrou em estado de parada ou ação necessária
                if current_state in JulesWatcher.FEEDBACK_STATES:
                    print(f"\n{Colors.BOLD}{Colors.YELLOW}🔔 Sessão aguardando interação ({current_state})!{Colors.RESET}")
                    print(f"👉 Para aprovar o plano: amb jules approve -s {clean_id}")
                    print(f"👉 Para responder dúvida: amb jules reply -s {clean_id}\n")
                    break

                if current_state in JulesWatcher.TERMINAL_FAILURE_STATES:
                    print(f"\n{Colors.BOLD}{Colors.RED}❌ Sessão encerrada com falha ({current_state}).{Colors.RESET}\n")
                    break

                if current_state in JulesWatcher.SUCCESS_STATES:
                    pr_info = JulesClient.extract_pull_request(sess, activities=acts)
                    pr_url = pr_info.get("url") if pr_info else "Não detectado"
                    print(f"\n{Colors.BOLD}{Colors.GREEN}🎉 Sessão concluída com sucesso!{Colors.RESET}")
                    print(f"  • Pull Request: {Colors.GREEN}{pr_url}{Colors.RESET}")
                    print(f"👉 Para integrar ao Git: amb jules merge -s {clean_id}\n")
                    break

            except Exception as e:
                log_error("JULES-STREAM", f"Erro transitório na leitura: {e}")

            time.sleep(poll_interval)

    except KeyboardInterrupt:
        print(f"\n{Colors.DIM}Streaming encerrado pelo usuário.{Colors.RESET}\n")


if __name__ == "__main__":
    w = JulesWatcher()
    al = w.check()
    print(f"Alertas Jules detectados: {len(al)}")
