#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
📡 AMB_V2 - Monitoramento: Assistente Central de Resposta e Decisão com IA (SRP)
Localização: amb_v2/dashboard/auto_advisor.py
Responsabilidade Única: Listar todas as pendências detectadas (Jules/Stitch), exibir a pergunta/proposta
do agente, consultar o Antigravity SDK para sugerir a melhor resposta e despachar (com opção de auto-aprovação).
"""

import os
import sys
import argparse

# Bootstrap dinâmico de caminhos amb_v2
_cur = os.path.dirname(os.path.abspath(__file__))
while _cur and os.path.basename(_cur) != "amb_v2":
    _p = os.path.dirname(_cur)
    if _p == _cur:
        break
    _cur = _p
_AMB = _cur
for _sub in [
    "config", "agents", "pipeline", "dashboard", "dashboard/watchers",
    "integrations/jules", "integrations/jules/tools",
    "integrations/stitch", "integrations/stitch/tools",
    "integrations/antigravity", "integrations/antigravity/tools",
    "integrations/render", "integrations/render/tools",
]:
    _p = os.path.normpath(os.path.join(_AMB, *_sub.split("/")))
    if os.path.exists(_p) and _p not in sys.path:
        sys.path.insert(0, _p)

from config import Colors, log, log_error, get_repo_name
from jules_client import JulesClient
from auto_reply import advise_and_reply, get_full_session_history


def get_pending_sessions(client: JulesClient) -> list[dict]:
    """Varre as sessões do repositório atual e retorna as que demandam feedback humano."""
    current_repo = get_repo_name()
    sessions = client.list_sessions(page_size=50, repo_filter=current_repo)
    pending = []
    for s in sessions:
        sid = s.get("name", "").split("/")[-1] or s.get("id")
        state = s.get("state", "UNKNOWN")
        title = s.get("title") or "Sem título"

        if state in ["AWAITING_USER_FEEDBACK", "Awaiting User Feedback", "AWAITING_INPUT", "AWAITING_PLAN_APPROVAL"]:
            try:
                _, _, _, context_txt = get_full_session_history(client, sid)
                pending.append({
                    "session_id": sid,
                    "state": state,
                    "title": title,
                    "question": context_txt
                })
            except Exception:
                pending.append({
                    "session_id": sid,
                    "state": state,
                    "title": title,
                    "question": "Aguardando feedback humano."
                })
    return pending


def run_auto_advisor(auto_approve: bool = False):
    """Processa chats pendentes com opção de auto-aprovação em lote."""
    print("\n" + "=" * 75)
    mode_label = f"{Colors.GREEN}[MODO AUTO-APPROVE 100% AUTÔNOMO]{Colors.RESET}" if auto_approve else "[MODO INTERATIVO COM APROVAÇÃO]"
    print(f"{Colors.BOLD}{Colors.CYAN}🤖 AMB_V2 — ASSISTENTE COGNITIVO DE RESPOSTAS (ANTIGRAVITY + JULES) {mode_label}{Colors.RESET}")
    print("=" * 75)

    client = JulesClient()
    pending = get_pending_sessions(client)

    if not pending:
        print(f"\n{Colors.GREEN}✔ Nenhum chat aguardando resposta ou pendência no momento!{Colors.RESET}\n")
        return

    print(f"\n{Colors.BOLD}📋 Chats do Jules aguardando resposta ({len(pending)} encontrados):{Colors.RESET}\n")
    for idx, item in enumerate(pending, 1):
        print(f"  [{Colors.BOLD}{idx}{Colors.RESET}] {Colors.CYAN}{item['title']}{Colors.RESET} (ID: {item['session_id']})")
        print(f"      Estado: {Colors.YELLOW}{item['state']}{Colors.RESET}")
        first_line = item['question'].split("\n")[0][:100]
        print(f"      Contexto/Dúvida: {Colors.DIM}{first_line}...{Colors.RESET}\n")

    # MODO 1: Auto-Approve de todas as sessões pendentes
    if auto_approve:
        log("AUTO-ADVISOR", f"Iniciando resolução automática de todos os {len(pending)} chats pendentes...", Colors.CYAN)
        for idx, item in enumerate(pending, 1):
            sid = item["session_id"]
            print(f"\n{'=' * 75}")
            print(f"⚡ [{idx}/{len(pending)}] Processando Sessão: {item['title']} ({sid})")
            print(f"{'=' * 75}")
            try:
                advise_and_reply(session_id=sid, auto_approve=True)
            except Exception as e:
                log_error("AUTO-ADVISOR", f"Falha ao responder sessão {sid}: {e}")

        print(f"\n{Colors.BOLD}{Colors.GREEN}🎉 Todos os {len(pending)} chats foram analisados e respondidos com sucesso pelo Antigravity!{Colors.RESET}\n")
        return

    # MODO 2: Interativo
    while True:
        try:
            choice = input(f"👉 Digite o número da sessão (ou 'A' para auto-responder todas, '0' para sair): ").strip()
            if choice in ["0", "s", "sair", "exit"]:
                break

            if choice.lower() in ["a", "all", "todos"]:
                run_auto_advisor(auto_approve=True)
                break

            idx = int(choice) - 1
            if 0 <= idx < len(pending):
                target_sid = pending[idx]["session_id"]
                advise_and_reply(session_id=target_sid, auto_approve=False)
                break
            else:
                print(f"{Colors.YELLOW}Opção inválida. Digite um número de 1 a {len(pending)}.{Colors.RESET}")
        except ValueError:
            print(f"{Colors.YELLOW}Digite um número válido.{Colors.RESET}")
        except KeyboardInterrupt:
            break


def main():
    parser = argparse.ArgumentParser(description="Assistente cognitivo de resposta para pendências do Jules.")
    parser.add_argument("--session-id", "-s", help="ID direto de uma sessão a ser respondida com IA.")
    parser.add_argument("--auto-approve", "-y", "--all", action="store_true", help="Auto-aprova e envia respostas para todos os chats pendentes sem pedir confirmação.")

    args = parser.parse_args()

    try:
        if args.session_id:
            advise_and_reply(session_id=args.session_id, auto_approve=args.auto_approve)
        else:
            run_auto_advisor(auto_approve=args.auto_approve)
    except Exception as e:
        log_error("ADVISOR", str(e))
        sys.exit(1)


if __name__ == "__main__":
    main()
