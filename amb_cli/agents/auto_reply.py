#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🤖 AMB_V2 - AUTO REPLY & ADVISOR (JULES + ANTIGRAVITY) — FAÇADE SRP
Ponto de entrada que delega para classes especializadas em auto_reply_core.
"""

import argparse
import sys
from typing import Any, Dict, List, Optional, Tuple

from core.bootstrap import ensure_amb_env
ensure_amb_env()

from core import log_error
from integrations.jules.jules_client import JulesClient
from agents.auto_reply_core import (
    TurnHistoryExtractor,
    CognitiveAdvisor,
    JulesFeedbackDispatcher,
)


def extract_activity_text(activity: Dict[str, Any], role: str = "agent") -> str:
    """Extrai o texto de mensagens da API do Jules para qualquer formato retornado."""
    return TurnHistoryExtractor.extract_activity_text(activity, role=role)


def get_last_conversation_turn(acts: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Analisa a lista de atividades e determina quem falou por último e qual foi a última pergunta/plano."""
    return TurnHistoryExtractor.get_last_conversation_turn(acts)


def get_full_session_history(
    client: JulesClient, session_id: str
) -> Tuple[Dict[str, Any], str, str, str, Dict[str, Any]]:
    """Obtém a sessão, o prompt inicial, a conversa cronológica, a última dúvida e metadados."""
    return TurnHistoryExtractor.get_full_session_history(client, session_id)


def _filter_rules_for_jules(content: str) -> str:
    """Filtra seções de Git/VCS das regras para não enviar restrições limitantes ao Jules."""
    return CognitiveAdvisor.filter_rules_for_jules(content)


def load_rules(rules_dir: str) -> str:
    """Carrega e cacheia o conteúdo das regras para evitar I/O redundante."""
    return CognitiveAdvisor.load_rules(rules_dir)


def generate_ai_suggestion(
    session_title: str,
    initial_prompt: str,
    full_chat_history: str,
    current_question: str,
) -> str:
    """Gera sugestão de resposta técnica via CognitiveAdvisor com histórico e regras."""
    advisor = CognitiveAdvisor()
    return advisor.generate_suggestion(
        session_title=session_title,
        initial_prompt=initial_prompt,
        full_chat_history=full_chat_history,
        current_question=current_question,
    )


def advise_and_reply(
    session_id: str, auto_approve: bool = False, force: bool = False
) -> Optional[str]:
    """Fluxo interativo com exibição de histórico, pergunta e resposta assistida por IA."""
    dispatcher = JulesFeedbackDispatcher()
    return dispatcher.advise_and_reply(
        session_id=session_id, auto_approve=auto_approve, force=force
    )


# Alias para retrocompatibilidade
auto_reply_session = advise_and_reply


def get_pending_sessions(client: Optional[JulesClient] = None) -> List[Dict[str, Any]]:
    """Varre as sessões do repositório atual e retorna as que demandam ação humana."""
    dispatcher = JulesFeedbackDispatcher(jules_client=client)
    return dispatcher.get_pending_sessions()


def _process_auto_approve_batch(pending: List[Dict[str, Any]]) -> None:
    """Processa lote de sessões pendentes com auto-aprovação."""
    dispatcher = JulesFeedbackDispatcher()
    dispatcher.process_auto_approve_batch(pending)


def _process_interactive_menu(pending: List[Dict[str, Any]]) -> None:
    """Processa sessões pendentes através de menu interativo."""
    dispatcher = JulesFeedbackDispatcher()
    dispatcher.process_interactive_menu(pending)


def run_auto_advisor(auto_approve: bool = False) -> None:
    """Processa chats pendentes com opção de auto-aprovação em lote ou menu interativo."""
    dispatcher = JulesFeedbackDispatcher()
    dispatcher.run_auto_advisor(auto_approve=auto_approve)


def auto_reply_all_pending(auto_approve: bool = True) -> None:
    """Processa todas as sessões pendentes utilizando auto-aprovação."""
    run_auto_advisor(auto_approve=auto_approve)


def interactive_advisor_menu() -> None:
    """Abre o menu interativo para processar sessões pendentes."""
    run_auto_advisor(auto_approve=False)


def main() -> None:
    """Ponto de entrada do CLI para o Auto Reply."""
    parser = argparse.ArgumentParser(
        description="Gera sugestão de resposta via Antigravity com histórico completo do chat."
    )
    parser.add_argument(
        "--session-id",
        "-s",
        required=False,
        help="ID da sessão no Jules (opcional, se omitido lista todos os chats pendentes).",
    )
    parser.add_argument(
        "--auto-approve",
        "-y",
        action="store_true",
        help="Envia a resposta gerada automaticamente sem pedir confirmação.",
    )

    args = parser.parse_args()

    try:
        if args.session_id:
            advise_and_reply(session_id=args.session_id, auto_approve=args.auto_approve)
        else:
            run_auto_advisor(auto_approve=args.auto_approve)
    except Exception as e:
        log_error("JULES-ADVISOR", str(e))
        sys.exit(1)


if __name__ == "__main__":
    main()
