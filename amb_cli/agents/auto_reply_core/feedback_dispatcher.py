#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🤖 AMB_V2 - Despachador de Respostas e Gestor de Sessões do Jules (SRP)
Localização: amb_cli/agents/auto_reply_core/feedback_dispatcher.py
Responsabilidade Única: Interagir com a API do Jules para enviar mensagens,
aprovar planos, listar sessões aguardando feedback e coordenar fluxos interativos/em lote.
"""

import sys
from typing import Any, Dict, List, Optional

from core.bootstrap import ensure_amb_env
ensure_amb_env()

from core import Colors, log, log_error
from workspace import get_repo_name
from integrations.jules.jules_client import JulesClient
from .turn_extractor import TurnHistoryExtractor
from .cognitive_advisor import CognitiveAdvisor


class JulesFeedbackDispatcher:
    """Orquestrador de despacho e interação com o Google Jules."""

    def __init__(
        self,
        jules_client: Optional[JulesClient] = None,
        advisor: Optional[CognitiveAdvisor] = None,
        extractor: Optional[TurnHistoryExtractor] = None,
    ):
        self.jules_client = jules_client or JulesClient()
        self.advisor = advisor or CognitiveAdvisor()
        self.extractor = extractor or TurnHistoryExtractor()

    def send_reply(self, session_id: str, message: str) -> None:
        """Envia mensagem ao chat da sessão no Jules."""
        log("JULES-ADVISOR", f"Enviando resposta para a sessão {session_id}...", Colors.CYAN)
        self.jules_client.send_message(session_id=session_id, message=message)
        log("JULES-ADVISOR", "🎉 Resposta enviada com sucesso ao Google Jules!", Colors.GREEN)

    def approve_plan(self, session_id: str) -> None:
        """Aprova formalmente o plano proposto pelo agente na sessão."""
        log("JULES-ADVISOR", f"Aprovando plano da sessão {session_id}...", Colors.CYAN)
        self.jules_client.approve_plan(session_id)
        log("JULES-ADVISOR", "✅ Plano aprovado com sucesso!", Colors.GREEN)

    def get_pending_sessions(self) -> List[Dict[str, Any]]:
        """Varre as sessões do repositório atual e retorna apenas as que demandam ação humana."""
        current_repo = get_repo_name()
        sessions = self.jules_client.list_sessions(page_size=50, repo_filter=current_repo)
        pending = []

        for s in sessions:
            sid = s.get("name", "").split("/")[-1] or s.get("id")
            state = s.get("state", "UNKNOWN")
            title = s.get("title") or "Sem título"

            if (
                state in [
                    "AWAITING_USER_FEEDBACK",
                    "AWAITING_USER_ACTION",
                    "AWAITING_INPUT",
                    "AWAITING_PLAN_APPROVAL",
                ]
                or "AWAITING" in (state or "").upper()
            ):
                try:
                    _, _, _, context_txt, turn_info = self.extractor.get_full_session_history(
                        self.jules_client, sid
                    )
                    # Se a última mensagem já foi do usuário, a sessão NÃO está pendente de resposta
                    if not turn_info.get("is_awaiting_user_action", True):
                        continue

                    pending.append(
                        {
                            "session_id": sid,
                            "state": state,
                            "title": title,
                            "question": context_txt,
                            "has_unapproved_plan": turn_info.get(
                                "has_unapproved_plan", False
                            ),
                            "plan_title": turn_info.get("unapproved_plan_title", ""),
                        }
                    )
                except Exception:
                    pending.append(
                        {
                            "session_id": sid,
                            "state": state,
                            "title": title,
                            "question": "Aguardando feedback humano.",
                            "has_unapproved_plan": False,
                        }
                    )
        return pending

    def advise_and_reply(
        self,
        session_id: str,
        auto_approve: bool = False,
        force: bool = False,
    ) -> Optional[str]:
        """Fluxo com exibição de histórico, pergunta e resposta assistida por IA."""
        clean_sid = str(session_id).strip().rstrip("/").split("/")[-1]
        log(
            "JULES-ADVISOR",
            f"Carregando histórico completo da sessão {clean_sid}...",
            Colors.CYAN,
        )

        session, initial_prompt, chat_history, current_question, turn_info = (
            self.extractor.get_full_session_history(self.jules_client, clean_sid)
        )
        title = session.get("title", "Sem título")

        # Proteção: se a última mensagem da sessão já foi do usuário, não responder novamente
        if not force and not turn_info.get("is_awaiting_user_action", True):
            last_u = turn_info.get("last_user_msg", "")
            preview = (last_u[:80] + "...") if len(last_u) > 80 else last_u
            if auto_approve:
                log(
                    "JULES-ADVISOR",
                    f"ℹ️ Sessão {clean_sid} já foi respondida recentemente (última msg: '{preview}'). Aguardando agente processar.",
                    Colors.YELLOW,
                )
                return None
            else:
                print(f"\n⚠️  {Colors.YELLOW}{Colors.BOLD}AVISO: Última mensagem já enviada!{Colors.RESET} {Colors.DIM}'{preview}'{Colors.RESET}")
                c_force = input("👉 Forçar envio? [s/N]: ").strip().lower()
                if c_force not in ["s", "sim", "y", "yes"]:
                    return None

        print(f"\n🤖 {Colors.BOLD}SESSÃO:{Colors.RESET} {title} ({clean_sid}) | 📊 {Colors.BOLD}ESTADO:{Colors.RESET} {session.get('state')}")
        print(f"🎯 {Colors.BOLD}ÚLTIMA DÚVIDA:{Colors.RESET} {Colors.YELLOW}{current_question.strip() or 'Aguardando...'}{Colors.RESET}\n")

        log(
            "ANTIGRAVITY",
            "🧠 Enviando histórico completo + última dúvida para o Gemini formular a resposta...",
            Colors.CYAN,
        )
        suggested_reply = self.advisor.generate_suggestion(
            session_title=title,
            initial_prompt=initial_prompt,
            full_chat_history=chat_history,
            current_question=current_question,
        )

        print(f"\n💡 {Colors.BOLD}{Colors.GREEN}SUGESTÃO GERADA PELO GEMINI:{Colors.RESET}\n" + "-" * 75)
        print(suggested_reply.strip() + "\n" + "-" * 75 + "\n")

        if auto_approve:
            final_reply = suggested_reply
        else:
            print(f"{Colors.BOLD}🎯 OPÇÕES:{Colors.RESET} [ENTER/s] Aprovar, [h] Histórico, [e] Editar, [d] Digitar, [p] Aprovar plano, [n] Cancelar")
            opt = input("👉 Escolha: ").strip().lower()

            if opt in ["n", "cancelar", "sair"]:
                log("JULES-ADVISOR", "Operação cancelada pelo usuário.", Colors.YELLOW)
                return None
            elif opt == "h":
                print("\n" + "=" * 75)
                print(f"{Colors.BOLD}HISTÓRICO COMPLETO DO CHAT:{Colors.RESET}")
                print("=" * 75)
                print(chat_history)
                print("=" * 75 + "\n")
                return self.advise_and_reply(
                    session_id=clean_sid, auto_approve=auto_approve, force=True
                )
            elif opt == "p":
                self.approve_plan(clean_sid)
                return None
            elif opt == "e":
                extra = input("\n✏️ Digite suas instruções adicionais ou ajustes: ").strip()
                final_reply = (
                    f"{suggested_reply}\n\nInstruções Adicionais:\n{extra}"
                    if extra
                    else suggested_reply
                )
            elif opt == "d":
                final_reply = input("\n✏️ Digite sua mensagem para o Jules: ").strip()
                if not final_reply:
                    log(
                        "JULES-ADVISOR",
                        "Mensagem vazia. Operação cancelada.",
                        Colors.YELLOW,
                    )
                    return None
            else:
                final_reply = suggested_reply

        self.send_reply(session_id=clean_sid, message=final_reply)
        return final_reply

    def process_auto_approve_batch(self, pending: List[Dict[str, Any]]) -> None:
        """Processa em lote e responde automaticamente todas as sessões pendentes."""
        log(
            "AUTO-ADVISOR",
            f"Iniciando resolução automática de todos os {len(pending)} chats pendentes...",
            Colors.CYAN,
        )
        for idx, item in enumerate(pending, 1):
            sid = item["session_id"]
            print(f"\n{'=' * 75}")
            print(f"⚡ [{idx}/{len(pending)}] Processando Sessão: {item['title']} ({sid})")
            print(f"{'=' * 75}")
            try:
                self.advise_and_reply(session_id=sid, auto_approve=True)
            except Exception as e:
                log_error("AUTO-ADVISOR", f"Falha ao responder sessão {sid}: {e}")

        print(
            f"\n{Colors.BOLD}{Colors.GREEN}🎉 Todos os {len(pending)} chats foram processados com sucesso!{Colors.RESET}\n"
        )

    def process_interactive_menu(self, pending: List[Dict[str, Any]]) -> None:
        """Menu interativo para escolha manual de qual sessão responder."""
        while True:
            try:
                choice = input(
                    "👉 Digite o número da sessão (ou 'A' para auto-responder todas, '0' para sair): "
                ).strip()
                if choice in ["0", "s", "sair", "exit"]:
                    break

                if choice.lower() in ["a", "all", "todos"]:
                    self.process_auto_approve_batch(pending)
                    break

                idx = int(choice) - 1
                if 0 <= idx < len(pending):
                    target_sid = pending[idx]["session_id"]
                    self.advise_and_reply(session_id=target_sid, auto_approve=False)
                    break
                else:
                    print(
                        f"{Colors.YELLOW}Opção inválida. Digite um número de 1 a {len(pending)}.{Colors.RESET}"
                    )
            except ValueError:
                print(f"{Colors.YELLOW}Digite um número válido.{Colors.RESET}")
            except KeyboardInterrupt:
                break

    def run_auto_advisor(self, auto_approve: bool = False) -> None:
        """Ponto de entrada do advisor: detecta sessões pendentes e direciona para lote ou menu."""
        print("\n" + "=" * 75)
        mode_label = (
            f"{Colors.GREEN}[MODO AUTO-APPROVE 100% AUTÔNOMO]{Colors.RESET}"
            if auto_approve
            else "[MODO INTERATIVO COM APROVAÇÃO]"
        )
        print(
            f"{Colors.BOLD}{Colors.CYAN}🤖 AMB_V2 — ASSISTENTE COGNITIVO DE RESPOSTAS (ANTIGRAVITY + JULES) {mode_label}{Colors.RESET}"
        )
        print("=" * 75)

        pending = self.get_pending_sessions()

        if not pending:
            print(
                f"\n{Colors.GREEN}✔ Nenhum chat aguardando resposta ou pendência no momento!{Colors.RESET}\n"
            )
            return

        print(
            f"\n{Colors.BOLD}📋 Chats do Jules aguardando resposta ({len(pending)} encontrados):{Colors.RESET}\n"
        )
        for idx, item in enumerate(pending, 1):
            print(
                f"  [{Colors.BOLD}{idx}{Colors.RESET}] {Colors.CYAN}{item['title']}{Colors.RESET} (ID: {item['session_id']})"
            )
            print(f"      Estado: {Colors.YELLOW}{item['state']}{Colors.RESET}")
            first_line = item["question"].split("\n")[0][:100]
            print(f"      Contexto/Dúvida: {Colors.DIM}{first_line}...{Colors.RESET}\n")

        if auto_approve:
            self.process_auto_approve_batch(pending)
        else:
            self.process_interactive_menu(pending)
