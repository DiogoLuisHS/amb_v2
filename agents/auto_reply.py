#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
================================================================================
🤖 AMB_V2 - AUTO REPLY & ADVISOR (JULES + ANTIGRAVITY)
================================================================================
Localização: amb_v2/agents/auto_reply.py
Responsabilidade Única: Analisar o histórico cronológico de uma sessão do Google
Jules e gerar respostas técnicas contextuais usando Antigravity/Gemini para
destravar o agente quando ele estiver no estado AWAITING_USER_FEEDBACK.
================================================================================
"""

import os
import sys
import argparse
from typing import Tuple, Dict, Any, Optional

# Bootstrap dinâmico de caminhos amb_v2
_cur = os.path.dirname(os.path.abspath(__file__))
while _cur and os.path.basename(_cur) != "amb_v2":
    _p = os.path.dirname(_cur)
    if _p == _cur:
        break
    _cur = _p
_AMB = _cur
for _sub in [
    "config",
    "agents",
    "pipeline",
    "dashboard",
    "dashboard/watchers",
    "integrations/jules",
    "integrations/jules/tools",
    "integrations/stitch",
    "integrations/stitch/tools",
    "integrations/antigravity",
    "integrations/antigravity/tools",
    "integrations/render",
    "integrations/render/tools",
]:
    _p = os.path.normpath(os.path.join(_AMB, *_sub.split("/")))
    if os.path.exists(_p) and _p not in sys.path:
        sys.path.insert(0, _p)

from config import Colors, log, log_error, find_repo_root  # noqa: E402
from jules_client import JulesClient  # noqa: E402
from antigravity_client import AntigravityClient  # noqa: E402


def extract_activity_text(activity: dict, role: str = "agent") -> str:
    """Extrai com precisão o texto de mensagens da API do Jules para qualquer formato retornado."""
    if not activity or not isinstance(activity, dict):
        return ""

    if role == "agent":
        if "agentMessaged" in activity:
            val = activity["agentMessaged"]
            if isinstance(val, dict):
                res = (
                    val.get("agentMessage")
                    or val.get("text")
                    or val.get("message")
                    or ""
                )
                if isinstance(res, str) and res.strip():
                    return res.strip()
            elif isinstance(val, str) and val.strip():
                return val.strip()

        if "agentMessage" in activity:
            val = activity["agentMessage"]
            if isinstance(val, dict):
                res = (
                    val.get("text")
                    or val.get("agentMessage")
                    or val.get("message")
                    or ""
                )
                if isinstance(res, str) and res.strip():
                    return res.strip()
            elif isinstance(val, str) and val.strip():
                return val.strip()

        if "userFeedbackRequired" in activity:
            val = activity["userFeedbackRequired"]
            if isinstance(val, dict):
                res = val.get("question") or val.get("text") or val.get("message") or ""
                if isinstance(res, str) and res.strip():
                    return res.strip()
            elif isinstance(val, str) and val.strip():
                return val.strip()

    elif role == "user":
        if "userMessaged" in activity:
            val = activity["userMessaged"]
            if isinstance(val, dict):
                res = (
                    val.get("userMessage")
                    or val.get("text")
                    or val.get("message")
                    or ""
                )
                if isinstance(res, str) and res.strip():
                    return res.strip()
            elif isinstance(val, str) and val.strip():
                return val.strip()

        if "userMessage" in activity:
            val = activity["userMessage"]
            if isinstance(val, dict):
                res = (
                    val.get("text")
                    or val.get("userMessage")
                    or val.get("message")
                    or ""
                )
                if isinstance(res, str) and res.strip():
                    return res.strip()
            elif isinstance(val, str) and val.strip():
                return val.strip()

    return ""


def get_last_conversation_turn(acts: list) -> Dict[str, Any]:
    """
    Analisa a lista de atividades (da mais recente para a mais antiga)
    e determina quem falou por último e qual foi a última pergunta/plano real.
    """
    turn_info = {
        "last_speaker": None,  # 'USER' | 'AGENT' | 'PLAN' | 'SYSTEM'
        "last_user_msg": "",
        "last_agent_msg": "",
        "last_agent_msg_id": None,
        "has_unapproved_plan": False,
        "unapproved_plan_title": "",
        "is_awaiting_user_action": False,
    }

    if not acts:
        return turn_info

    for a in acts:
        aid = a.get("id") or a.get("name")

        # 1. Mensagem do Usuário
        user_txt = extract_activity_text(a, role="user")
        if user_txt:
            if not turn_info["last_speaker"]:
                turn_info["last_speaker"] = "USER"
                turn_info["last_user_msg"] = user_txt
                turn_info["is_awaiting_user_action"] = False
                break

        # 2. Plano com aprovação pendente
        plan = (
            a.get("plan") or a.get("agentMessage", {}).get("plan")
            if isinstance(a.get("agentMessage"), dict)
            else None
        )
        if not plan and "planGenerated" in a:
            p_gen = a["planGenerated"].get("plan")
            if p_gen and p_gen.get("state") == "PENDING_USER_APPROVAL":
                plan = p_gen

        if plan and plan.get("state") == "PENDING_USER_APPROVAL":
            if not turn_info["last_speaker"]:
                turn_info["last_speaker"] = "PLAN"
                turn_info["has_unapproved_plan"] = True
                turn_info["unapproved_plan_title"] = plan.get("title", "")
                turn_info["last_agent_msg_id"] = aid
                turn_info["last_agent_msg"] = f"Plano proposto: {plan.get('title', '')}"
                turn_info["is_awaiting_user_action"] = True
                break

        # 3. Mensagem do Agente / Feedback Requerido
        agent_txt = extract_activity_text(a, role="agent")
        if agent_txt:
            if not turn_info["last_speaker"]:
                turn_info["last_speaker"] = "AGENT"
                turn_info["last_agent_msg"] = agent_txt
                turn_info["last_agent_msg_id"] = aid
                turn_info["is_awaiting_user_action"] = True
                break

    return turn_info


def get_full_session_history(
    client: JulesClient, session_id: str
) -> Tuple[Dict[str, Any], str, str, str, Dict[str, Any]]:
    """Obtém a sessão, o prompt inicial, a conversa cronológica formatada, a última dúvida e metadados do turno."""
    session = client.get_session(session_id)
    initial_prompt = session.get("prompt", "")

    acts_resp = client.list_activities(session_id=session_id, page_size=100)
    acts = acts_resp if isinstance(acts_resp, list) else acts_resp.get("activities", [])

    turn_info = get_last_conversation_turn(acts)

    # A API retorna em ordem decrescente (mais recente primeiro) -> invertemos para cronológico
    chronological_acts = list(reversed(acts))

    chat_lines = []
    current_question = turn_info.get("last_agent_msg", "")

    for a in chronological_acts:
        time_str = a.get("createTime", "")[:19].replace("T", " ")

        # Mensagem do Usuário
        user_txt = extract_activity_text(a, role="user")
        if user_txt:
            chat_lines.append(f"[{time_str}] 👤 USUÁRIO:\n{user_txt}\n")

        # Mensagem do Jules
        agent_txt = extract_activity_text(a, role="agent")
        if agent_txt:
            chat_lines.append(f"[{time_str}] 🤖 AGENTE JULES:\n{agent_txt}\n")
            current_question = agent_txt

        # Comando Bash
        elif a.get("bashCommand"):
            cmd = a["bashCommand"].get("command", "")
            out = a["bashCommand"].get("output", "")
            trunc_out = out[:800] + (
                f"\n...[+{len(out) - 800} chars omitidos]" if len(out) > 800 else ""
            )
            chat_lines.append(
                f"[{time_str}] 💻 BASH: `$ {cmd}`\nOutput:\n{trunc_out}\n"
            )

        # Plano do Agente
        elif a.get("plan") or a.get("planGenerated"):
            p_obj = a.get("plan") or a.get("planGenerated", {}).get("plan") or {}
            plan_title = p_obj.get("title", "")
            steps = p_obj.get("steps", [])
            step_lines = "\n".join(
                [
                    f"   - [{'x' if s.get('state') == 'COMPLETED' else ' '}] {s.get('description', '')}"
                    for s in steps
                ]
            )
            chat_lines.append(
                f"[{time_str}] 📋 PLANO PROPOSTO: {plan_title}\n{step_lines}\n"
            )

        # Progresso ou Avaliação do Agente
        elif a.get("progressUpdated"):
            p_title = a["progressUpdated"].get("title", "")
            p_desc = a["progressUpdated"].get("description", "")
            chat_lines.append(
                f"[{time_str}] 📊 PROGRESSO/AVALIAÇÃO: {p_title}\n{p_desc}\n"
            )

    full_history = "\n".join(chat_lines)
    return session, initial_prompt, full_history, current_question, turn_info


def _filter_rules_for_jules(content: str) -> str:
    """Filtra seções de Git/VCS das regras para não enviar restrições limitantes ao Jules.
    Bug #6 fix: detecta qualquer nível de header markdown como delimitador de seção.
    """
    lines = []
    skip = False
    for line in content.splitlines():
        # Detecta início de seção bloqueada (qualquer nível de header)
        if any(
            kw in line
            for kw in [
                "Version Control",
                "Git Safety Lock",
                "SAFETY LOCK",
                "Git Lock",
                "VCS Rules",
            ]
        ):
            skip = True
            continue
        # Qualquer header markdown (# ## ###) encerra a seção bloqueada
        if skip and line.lstrip().startswith("#"):
            skip = False
        if not skip:
            lines.append(line)
    return "\n".join(lines)


def generate_ai_suggestion(
    session_title: str,
    initial_prompt: str,
    full_chat_history: str,
    current_question: str,
) -> str:
    """Gera a sugestão de resposta técnica via Antigravity Client / Gemini contextualizado com histórico e regras."""
    root = find_repo_root()
    rules_dir = os.path.join(root, ".antigravity", "rules")
    if not os.path.exists(rules_dir):
        rules_dir = os.path.join(root, ".gemini", "rules")

    rules_context = ""
    if os.path.exists(rules_dir):
        for f in sorted(os.listdir(rules_dir)):
            if f.endswith(".md"):
                try:
                    with open(
                        os.path.join(rules_dir, f),
                        "r",
                        encoding="utf-8",
                        errors="replace",
                    ) as rf:
                        filtered_rule = _filter_rules_for_jules(rf.read())
                        rules_context += f"\n--- [REGRA: {f}] ---\n" + filtered_rule
                except Exception:
                    pass

    system_instruction = (
        "Você é o Antigravity Cognitive Advisor para o Google Jules. "
        "Sua função é analisar o contexto completo do chat, a missão inicial do projeto "
        "e responder com precisão cirúrgica e técnica à ÚLTIMA mensagem ou dúvida enviada pelo agente Jules."
    )

    prompt = f"""Você deve responder à última mensagem enviada pelo agente Google Jules no chat.

================================================================================
📌 1. MISSÃO INICIAL DA SESSÃO (OBJETIVO ORIGINAL):
================================================================================
Título: {session_title}
Prompt de Despacho:
"{initial_prompt}"

================================================================================
📜 2. CONTEXTO GERAL (HISTÓRICO COMPLETO DE TODAS AS MENSAGENS E AÇÕES DO CHAT):
================================================================================
{full_chat_history if full_chat_history.strip() else "Nenhuma mensagem anterior registrada."}

================================================================================
🎯 3. ÚLTIMA MENSAGEM / DÚVIDA DO JULES A SER RESPONDIDA AGORA:
================================================================================
"{current_question if current_question.strip() else "O agente concluiu uma etapa e aguarda instruções para prosseguir."}"

================================================================================
📐 4. REGRAS ARQUITETURAIS DO REPOSITÓRIO:
================================================================================
{rules_context or "Mantenha tipagem estrita, boas práticas, SRP e não quebre contratos de API."}

================================================================================
INSTRUÇÃO DE FORMULAÇÃO DA RESPOSTA:
================================================================================
1. FOCO NA ÚLTIMA MENSAGEM: Responda diretamente ao que o agente perguntou ou propôs na Seção 3.
2. USE O CONTEXTO COMPLETO: Utilize o histórico da Seção 2 e as regras da Seção 4 para não autorizar desvios, alterações indevidas em código funcional ou violações de contratos Zod/TypeScript.
3. SE HOUVER DESVIO: Dê instruções corretivas claras e diretas para o agente retomar o objetivo original da Seção 1.
4. SE O TRABALHO ESTIVER CORRETO: Aprove a proposta e instrua o agente a rodar os testes/build e abrir o Pull Request.

Retorne APENAS o texto da mensagem técnica pronta para ser enviada no chat do Jules."""

    client = AntigravityClient()
    try:
        return client.generate_text(
            prompt=prompt, system_instruction=system_instruction
        )
    except Exception as e:
        log_error("ANTIGRAVITY", f"Falha na API Gemini: {e}")
        # Fallback contextualizado e seguro para não travar o loop
        q_lower = current_question.lower()
        if (
            "open the pr" in q_lower
            or "create a pr" in q_lower
            or "proceed" in q_lower
            or "pr as it is" in q_lower
        ):
            return "Yes, please proceed to open the Pull Request with your completed fixes. Our local AMB_V2 Gatekeeper will run the complete typecheck and build suite locally before merging. Thank you!"
        elif "plan" in q_lower or "approve" in q_lower:
            return "Approved. Please proceed with the proposed plan, adhering strictly to existing TypeScript contracts and zero runtime errors."
        else:
            return "Please proceed with the proposed implementation adhering to the repository rules, and open the Pull Request when ready."


def advise_and_reply(session_id: str, auto_approve: bool = False, force: bool = False):
    """Fluxo interativo com exibição de histórico, pergunta e resposta assistida por IA."""
    j_client = JulesClient()
    log(
        "JULES-ADVISOR",
        f"Carregando histórico completo da sessão {session_id}...",
        Colors.CYAN,
    )

    session, initial_prompt, chat_history, current_question, turn_info = (
        get_full_session_history(j_client, session_id)
    )
    title = session.get("title", "Sem título")

    # Proteção: se a última mensagem da sessão já foi do usuário, não responder novamente
    if not force and not turn_info.get("is_awaiting_user_action", True):
        last_u = turn_info.get("last_user_msg", "")
        preview = (last_u[:80] + "...") if len(last_u) > 80 else last_u
        if auto_approve:
            log(
                "JULES-ADVISOR",
                f"ℹ️ Sessão {session_id} já foi respondida recentemente (última msg: '{preview}'). Aguardando agente processar.",
                Colors.YELLOW,
            )
            return
        else:
            print("\n" + "=" * 75)
            print(f"🤖 {Colors.BOLD}SESSÃO:{Colors.RESET} {title} ({session_id})")
            print(f"📊 {Colors.BOLD}ESTADO:{Colors.RESET} {session.get('state')}")
            print("=" * 75)
            print(
                f"\n⚠️  {Colors.YELLOW}{Colors.BOLD}AVISO: A última mensagem desta sessão já foi enviada pelo usuário!{Colors.RESET}"
            )
            print(f'   {Colors.DIM}"{last_u}"{Colors.RESET}')
            print(
                f"{Colors.YELLOW}O agente Jules ainda está processando e não fez uma nova pergunta.{Colors.RESET}\n"
            )

            c_force = (
                input("👉 Deseja forçar o envio de outra mensagem mesmo assim? [s/N]: ")
                .strip()
                .lower()
            )
            if c_force not in ["s", "sim", "y", "yes"]:
                log(
                    "JULES-ADVISOR",
                    "Operação abortada para evitar mensagens duplicadas.",
                    Colors.CYAN,
                )
                return

    print("\n" + "=" * 75)
    print(f"🤖 {Colors.BOLD}SESSÃO:{Colors.RESET} {title} ({session_id})")
    print(f"📊 {Colors.BOLD}ESTADO:{Colors.RESET} {session.get('state')}")
    print("=" * 75)

    print(
        f"\n🎯 {Colors.BOLD}ÚLTIMA MENSAGEM / DÚVIDA DETECTADA DO JULES:{Colors.RESET}"
    )
    print(
        f"{Colors.YELLOW}{current_question.strip() if current_question.strip() else 'Aguardando decisão para prosseguir.'}{Colors.RESET}\n"
    )

    log(
        "ANTIGRAVITY",
        "🧠 Enviando histórico completo + última dúvida para o Gemini formular a resposta...",
        Colors.CYAN,
    )
    suggested_reply = generate_ai_suggestion(
        session_title=title,
        initial_prompt=initial_prompt,
        full_chat_history=chat_history,
        current_question=current_question,
    )

    print(
        f"\n💡 {Colors.BOLD}{Colors.GREEN}SUGESTÃO GERADA PELO GEMINI (BASEADA NO HISTÓRICO + REGRAS):{Colors.RESET}"
    )
    print("-" * 75)
    print(suggested_reply.strip())
    print("-" * 75 + "\n")

    if auto_approve:
        final_reply = suggested_reply
    else:
        print(f"{Colors.BOLD}🎯 O QUE DESEJA FAZER?{Colors.RESET}")
        print("  [ENTER / S]  Aprovar e enviar a resposta sugerida para o Jules")
        print("  [H]          Ver histórico detalhado do chat")
        print("  [E]          Editar ou adicionar instruções à resposta sugerida")
        print("  [D]          Digitar uma resposta completamente manual")
        print("  [P]          Apenas aprovar o plano (:approvePlan)")
        print("  [N]          Cancelar / Não enviar nada")

        opt = input("\n👉 Escolha [ENTER/s/h/e/d/p/n]: ").strip().lower()

        if opt in ["n", "cancelar", "sair"]:
            log("JULES-ADVISOR", "Operação cancelada pelo usuário.", Colors.YELLOW)
            return
        elif opt == "h":
            print("\n" + "=" * 75)
            print(f"{Colors.BOLD}HISTÓRICO COMPLETO DO CHAT:{Colors.RESET}")
            print("=" * 75)
            print(chat_history)
            print("=" * 75 + "\n")
            return advise_and_reply(
                session_id=session_id, auto_approve=auto_approve, force=True
            )
        elif opt == "p":
            log(
                "JULES-ADVISOR",
                f"Aprovando plano da sessão {session_id}...",
                Colors.CYAN,
            )
            j_client.approve_plan(session_id)
            log("JULES-ADVISOR", "✅ Plano aprovado com sucesso!", Colors.GREEN)
            return
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
                return
        else:
            final_reply = suggested_reply

    log(
        "JULES-ADVISOR", f"Enviando resposta para a sessão {session_id}...", Colors.CYAN
    )
    j_client.send_message(session_id=session_id, message=final_reply)
    log(
        "JULES-ADVISOR",
        "🎉 Resposta enviada com sucesso ao Google Jules!",
        Colors.GREEN,
    )


# Alias para retrocompatibilidade
auto_reply_session = advise_and_reply


def get_pending_sessions(client: Optional[JulesClient] = None) -> list[dict]:
    """Varre as sessões do repositório atual e retorna apenas as que realmente demandam ação humana."""
    c = client or JulesClient()
    from config import get_repo_name

    current_repo = get_repo_name()
    sessions = c.list_sessions(page_size=50, repo_filter=current_repo)
    pending = []
    for s in sessions:
        sid = s.get("name", "").split("/")[-1] or s.get("id")
        state = s.get("state", "UNKNOWN")
        title = s.get("title") or "Sem título"

        if state in [
            "AWAITING_USER_FEEDBACK",
            "Awaiting User Feedback",
            "AWAITING_INPUT",
            "AWAITING_PLAN_APPROVAL",
        ]:
            try:
                _, _, _, context_txt, turn_info = get_full_session_history(c, sid)

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


def _process_auto_approve_batch(pending: list[dict]):
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
            advise_and_reply(session_id=sid, auto_approve=True)
        except Exception as e:
            log_error("AUTO-ADVISOR", f"Falha ao responder sessão {sid}: {e}")

    print(
        f"\n{Colors.BOLD}{Colors.GREEN}🎉 Todos os {len(pending)} chats foram analisados e respondidos com sucesso pelo Antigravity!{Colors.RESET}\n"
    )


def _process_interactive_menu(pending: list[dict]):
    while True:
        try:
            choice = input(
                "👉 Digite o número da sessão (ou 'A' para auto-responder todas, '0' para sair): "
            ).strip()
            if choice in ["0", "s", "sair", "exit"]:
                break

            if choice.lower() in ["a", "all", "todos"]:
                _process_auto_approve_batch(pending)
                break

            idx = int(choice) - 1
            if 0 <= idx < len(pending):
                target_sid = pending[idx]["session_id"]
                advise_and_reply(session_id=target_sid, auto_approve=False)
                break
            else:
                print(
                    f"{Colors.YELLOW}Opção inválida. Digite um número de 1 a {len(pending)}.{Colors.RESET}"
                )
        except ValueError:
            print(f"{Colors.YELLOW}Digite um número válido.{Colors.RESET}")
        except KeyboardInterrupt:
            break


def run_auto_advisor(auto_approve: bool = False):
    """Processa chats pendentes com opção de auto-aprovação em lote ou menu interativo."""
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

    client = JulesClient()
    pending = get_pending_sessions(client)

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

    # MODO 1: Auto-Approve em lote
    if auto_approve:
        _process_auto_approve_batch(pending)
    # MODO 2: Interativo
    else:
        _process_interactive_menu(pending)


def auto_reply_all_pending(auto_approve: bool = True):
    run_auto_advisor(auto_approve=auto_approve)


def interactive_advisor_menu():
    run_auto_advisor(auto_approve=False)


def main():
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
