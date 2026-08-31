#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔁 AMB_V2 - Loop Autônomo Contínuo de Engenharia (Jules + Antigravity)
Localização: amb_v2/agents/autonomous_loop.py
Responsabilidade Única: Executar ciclos contínuos de desenvolvimento autônomo,
enviando prompts estruturados (ou personas) ao Google Jules, monitorando
atividades em tempo real, respondendo dúvidas via Antigravity e integrando PRs no Git.

Exemplos de Uso:
  amb agent --role pixel --loop --max-cycles 3
  amb agent --all --loop --max-cycles 2
  python amb_v2/agents/autonomous_loop.py --all --max-cycles 2
"""

import os
import sys
import time
import argparse
from pathlib import Path
from typing import List, Optional

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
    "integrations/stitch", "integrations/antigravity", "integrations/render",
]:
    _p = os.path.normpath(os.path.join(_AMB, *_sub.split("/")))
    if os.path.exists(_p) and _p not in sys.path:
        sys.path.insert(0, _p)

from config import Colors, log, log_error, find_repo_root, get_repo_name, AmbError
from jules_client import JulesClient
from auto_reply import advise_and_reply
from local_agent_runner import get_personas_directory, discover_personas
from merge_session_pr import approve_and_merge_pr


def load_persona_content(role: str) -> tuple[str, str]:
    """Carrega dinamicamente o conteúdo da persona."""
    personas_dir = get_personas_directory()
    personas = discover_personas(personas_dir)
    clean_role = role.lower().replace(".md", "").strip()

    if clean_role in personas:
        p = personas[clean_role]
        return p["title"], p["content"]

    # Fallbacks padrão
    default_personas = {
        "relay": (
            "Autonomous Relay Engineer",
            "Você é o Autonomous Relay Engineer. Sua missão é dar continuidade ao desenvolvimento, auditoria e aperfeiçoamento do projeto. "
            "1. Analise arquivos recentes e identifique débitos técnicos.\n"
            "2. Implemente melhorias sólidas seguindo o Design System e padrões do repositório.\n"
            "3. Garanta 0 erros de TypeScript e build verde.\n"
            "4. Crie commits descritivos e abra o Pull Request."
        ),
        "sentry": (
            "Architecture & Type Safety Sentry",
            "Você é o Architecture Sentry. Sua missão é auditar a integridade estrutural do repositório, contratos de API e tipagem estrita."
        ),
        "pixel": (
            "Design System Artisan",
            "Você é o Design System Artisan. Sua missão é elevar a experiência visual e consistência de UI/UX do projeto."
        )
    }

    if clean_role in default_personas:
        return default_personas[clean_role]

    return f"{role.title()} Agent", f"Você é o agente especialista {role} do projeto."


def monitor_and_assist_session(client: JulesClient, session_id: str, auto_reply_ai: bool = True) -> str:
    """Monitora a sessão no Jules, respondendo planos e perguntas até a conclusão.
    
    Rastreia a última MENSAGEM DO AGENTE (não qualquer activity) para detectar
    novas perguntas mesmo quando o Jules faz uma segunda pergunta após receber resposta.
    """
    log("JULES-MONITOR", f"Iniciando acompanhamento da sessão {session_id}...", Colors.CYAN)

    # Rastreia o ID da última mensagem do AGENTE que já foi respondida
    last_answered_agent_msg_id = None
    last_state_was_feedback = False

    while True:
        try:
            sess = client.get_session(session_id)
            state = sess.get("state", "UNKNOWN")

            acts_resp = client.list_activities(session_id=session_id, page_size=30)
            acts = acts_resp if isinstance(acts_resp, list) else acts_resp.get("activities", [])

            # Identifica a mensagem mais recente DO AGENTE (ignora respostas do usuário)
            latest_agent_msg_id = None
            has_unapproved_plan = False
            for a in acts[:15]:
                # Plano pendente tem prioridade
                plan = a.get("plan") or a.get("agentMessage", {}).get("plan")
                if plan and plan.get("state") == "PENDING_USER_APPROVAL":
                    has_unapproved_plan = True
                    latest_agent_msg_id = a.get("id") or a.get("name")
                    break
                # Mensagem ou progresso do agente
                if a.get("agentMessage") or a.get("progressUpdated"):
                    if not latest_agent_msg_id:  # Pega só o mais recente
                        latest_agent_msg_id = a.get("id") or a.get("name")

            # Decisão de responder:
            # 1. Há uma mensagem nova do agente que não foi respondida ainda, OU
            # 2. Estado voltou para AWAITING após ter saído (Jules fez 2ª pergunta)
            is_feedback_state = state in ["AWAITING_USER_FEEDBACK", "Awaiting User Feedback", "AWAITING_INPUT", "AWAITING_PLAN_APPROVAL"]
            has_new_agent_msg = latest_agent_msg_id and latest_agent_msg_id != last_answered_agent_msg_id
            state_returned_to_feedback = is_feedback_state and not last_state_was_feedback

            should_reply = has_new_agent_msg or state_returned_to_feedback

            if is_feedback_state and should_reply:
                if has_unapproved_plan:
                    log("JULES", "Detectado plano pendente. Aprovando via :approvePlan...", Colors.GREEN)
                    try:
                        client.approve_plan(session_id)
                        last_answered_agent_msg_id = latest_agent_msg_id
                    except Exception as ep:
                        log_error("JULES", f"Falha ao aprovar plano pendente: {ep}")

                elif auto_reply_ai:
                    reason = "nova pergunta detectada" if has_new_agent_msg else "estado voltou para AWAITING (2ª dúvida)"
                    log("ANTIGRAVITY", f"Sessão aguardando feedback ({reason}). Formulando resposta...", Colors.HEADER)
                    try:
                        advise_and_reply(session_id=session_id, auto_approve=True)
                        last_answered_agent_msg_id = latest_agent_msg_id
                        print(f"[{Colors.GREEN}✔ Resposta enviada com sucesso para destravar o agente.{Colors.RESET}]\n")
                    except Exception as er:
                        log_error("ANTIGRAVITY", f"Falha ao auto-responder com IA: {er}")

            last_state_was_feedback = is_feedback_state

            if state in ["COMPLETED", "SUCCEEDED"]:
                log("LOOP", f"🎉 Sessão {session_id} CONCLUÍDA com sucesso!", Colors.GREEN)
                # Aguarda Jules popular o PR nos outputs antes de tentar detectar
                log("LOOP", "Aguardando Jules registrar o PR nos outputs (12s)...", Colors.DIM)
                time.sleep(12)
                return state
            elif state in ["FAILED", "CANCELLED", "CLOSED"]:
                log_error("LOOP", f"Sessão finalizada com estado: {state}")
                return state

            time.sleep(6)
        except KeyboardInterrupt:
            print(f"\n{Colors.YELLOW}Monitoramento interrompido pelo usuário.{Colors.RESET}")
            raise
        except Exception as e:
            err_str = str(e)
            if "404" in err_str or "Not Found" in err_str:
                log("LOOP", "Aguardando inicialização da sessão na nuvem...", Colors.DIM)
            else:
                log_error("LOOP", f"Aviso de polling: {e}")
            time.sleep(6)


def run_autonomous_loop(
    role: Optional[str] = None,
    all_personas: bool = False,
    prompt_file: Optional[str] = None,
    modules: Optional[List[str]] = None,
    max_cycles: Optional[int] = None,
    delay_between_cycles: int = 8,
    branch: str = "develop",
    no_auto_merge: bool = False
):
    """Executa o loop contínuo de envio, monitoramento, auto-resposta e re-disparo para uma ou todas as personas."""
    repo_name = get_repo_name()
    client = JulesClient()
    source_name = f"sources/github/{repo_name}"

    personas_dir = get_personas_directory()
    discovered = discover_personas(personas_dir)

    if all_personas:
        roles_to_run = list(discovered.keys()) if discovered else ["relay", "sentry", "pixel"]
    elif role:
        roles_to_run = [role]
    else:
        roles_to_run = ["relay"]

    modules_list = modules or [""]

    print("\n" + "=" * 75)
    print(f"{Colors.BOLD}{Colors.CYAN}🔁 INICIANDO LOOP AUTÔNOMO JULES + ANTIGRAVITY{Colors.RESET}")
    print(f"📁 Repositório: {Colors.BOLD}{repo_name}{Colors.RESET} (Branch: {branch})")
    print(f"🤖 Personas no Ciclo ({len(roles_to_run)}): {Colors.BOLD}{', '.join(roles_to_run)}{Colors.RESET}")
    if modules and modules != [""]:
        print(f"🎯 Módulos em Rotação: {', '.join(modules)}")
    print(f"⏱️ Limite de Ciclos: {f'{max_cycles} rodadas completas' if max_cycles else 'Infinito (Contínuo)'}")
    print("=" * 75 + "\n")

    completed_cycles = 0

    while True:
        completed_cycles += 1

        print("\n" + "#" * 75)
        print(f"🔄 {Colors.BOLD}CICLO #{completed_cycles} DE {max_cycles if max_cycles else '∞'}{Colors.RESET}")
        print("#" * 75 + "\n")

        for persona_idx, cur_role in enumerate(roles_to_run, 1):
            current_module = modules_list[(completed_cycles - 1) % len(modules_list)]

            print(f"\n📦 [{persona_idx}/{len(roles_to_run)}] Executando Persona: {Colors.BOLD}{cur_role.upper()}{Colors.RESET}" + (f" - Módulo: [{current_module}]" if current_module else ""))

            # 1. Carrega o Prompt
            if prompt_file and os.path.exists(prompt_file):
                with open(prompt_file, "r", encoding="utf-8", errors="replace") as pf:
                    base_prompt = pf.read()
                title = f"Task: {Path(prompt_file).stem.replace('_', ' ').title()}"
            else:
                title, base_prompt = load_persona_content(cur_role)

            if current_module:
                full_prompt = f"{base_prompt}\n\n---\n\n🎯 ESCOPO DESTA ITERAÇÃO:\nConcentre a auditoria e alinhamento estritamente no módulo: `{current_module}`."
                session_title = f"{title} [{current_module}] - Ciclo #{completed_cycles}"
            else:
                session_title = f"{title} - Ciclo #{completed_cycles}"
                full_prompt = base_prompt

            # C5: Enriquecer o prompt com o roteiro arquitetural do amb context
            # Reduz 20-30min de exploração inicial do Jules ao já fornecer o mapa de arquivos
            try:
                from ai_context_builder import AIContextBuilder
                from pathlib import Path as _Path
                _repo_root = find_repo_root()
                _ctx_builder = AIContextBuilder(_Path(_repo_root))
                _ctx_builder.analyze()
                _ctx_query = current_module if current_module else cur_role
                _ctx_chain = _ctx_builder.trace_module_chain(_ctx_query)
                _ctx_layers = _ctx_builder.classify_and_order_files(_ctx_chain, _ctx_query)
                _ctx_md = _ctx_builder.generate_markdown(_ctx_query, _ctx_layers)
                total_ctx_files = sum(len(l["files"]) for l in _ctx_layers.values())
                if total_ctx_files > 0:
                    full_prompt = (
                        f"{full_prompt}\n\n"
                        f"---\n\n"
                        f"## 📂 ROTEIRO DE LEITURA ARQUITETURAL (gerado por `amb context {_ctx_query}`)\n\n"
                        f"**Use este roteiro para iniciar sua análise sem precisar explorar o repositório do zero.**\n"
                        f"Leia os arquivos na ordem apresentada (DB → Repositórios → Services → Controllers → UI):\n\n"
                        f"{_ctx_md}"
                    )
                    log("LOOP", f"Roteiro arquitetural '{_ctx_query}' ({total_ctx_files} arquivos) anexado ao prompt.", Colors.GREEN)
            except Exception as ctx_err:
                log("LOOP", f"Aviso: amb context não disponível — {ctx_err}", Colors.DIM)

            # 2. Despacho no Jules
            log("LOOP", f"Criando sessão para persona '{cur_role}' no Google Jules...", Colors.CYAN)
            try:
                session_resp = client.create_session(
                    prompt=full_prompt,
                    source_name=source_name,
                    title=session_title,
                    base_branch=branch
                )

                session_id = session_resp.get("name", "").split("/")[-1] or session_resp.get("id", "")
                if not session_id:
                    raise AmbError(f"Falha ao obter ID da sessão: {session_resp}")

                print(f"🎉 Sessão Criada: {Colors.GREEN}{session_id}{Colors.RESET}")
                print(f"🔗 Acompanhe: {Colors.BLUE}https://jules.google.com/session/{session_id}{Colors.RESET}\n")

                log("LOOP", "Aguardando provisionamento da VM no Jules (5s)...", Colors.DIM)
                time.sleep(5)

                # 3. Monitoramento + Auto-Resposta
                state = monitor_and_assist_session(client=client, session_id=session_id, auto_reply_ai=True)
                
                # 4. Aprovação e Integração do PR no Git
                if state in ["COMPLETED", "SUCCEEDED"] and not no_auto_merge:
                    log("GIT-MERGE", f"Verificando Pull Request da sessão {session_id}...", Colors.HEADER)
                    try:
                        approve_and_merge_pr(session_id=session_id, target_branch=branch)
                    except Exception as em:
                        log_error("GIT-MERGE", f"Aviso na integração do PR: {em}")

            except KeyboardInterrupt:
                print(f"\n{Colors.YELLOW}Loop interrompido pelo usuário.{Colors.RESET}")
                return
            except Exception as e:
                log_error("LOOP", f"Erro no processamento da persona '{cur_role}': {e}")

            if len(roles_to_run) > 1:
                log("LOOP", f"Pausa de {delay_between_cycles}s antes da próxima persona...", Colors.DIM)
                time.sleep(delay_between_cycles)

        # Checagem de Limite de Ciclos Globais
        if max_cycles and completed_cycles >= max_cycles:
            log("LOOP", f"Limite de {max_cycles} ciclos atingido. Todas as personas foram executadas com sucesso!", Colors.GREEN)
            break

        log("LOOP", f"Ciclo #{completed_cycles} concluído. Aguardando {delay_between_cycles}s para a próxima rodada...", Colors.DIM)
        time.sleep(delay_between_cycles)


def main():
    parser = argparse.ArgumentParser(description="Loop Autônomo Contínuo Jules + Antigravity (AMB_V2)")
    parser.add_argument("--role", "-r", help="Persona a ser executada em loop (ex: relay, sentry, pixel).")
    parser.add_argument("--all", "-a", action="store_true", help="Executa todas as personas disponíveis da pasta em cada ciclo.")
    parser.add_argument("--prompt", "-p", help="Caminho de um arquivo .md com prompt customizado.")
    parser.add_argument("--modules", "-m", help="Lista de módulos separados por vírgula para alternar por ciclo (ex: kanban,agenda,projects).")
    parser.add_argument("--max-cycles", "-c", type=int, help="Número máximo de ciclos antes de parar (se omitido, roda continuamente).")
    parser.add_argument("--delay", "-d", type=int, default=8, help="Intervalo em segundos entre ciclos (Padrão: 8s).")
    parser.add_argument("--branch", "-b", default="develop", help="Branch alvo no GitHub (Padrão: develop).")
    parser.add_argument("--no-auto-merge", action="store_true", help="Não faz o merge automático do PR ao finalizar o ciclo.")

    args = parser.parse_args()

    modules_list = [m.strip() for m in args.modules.split(",") if m.strip()] if args.modules else None

    try:
        run_autonomous_loop(
            role=args.role,
            all_personas=args.all,
            prompt_file=args.prompt,
            modules=modules_list,
            max_cycles=args.max_cycles,
            delay_between_cycles=args.delay,
            branch=args.branch,
            no_auto_merge=args.no_auto_merge
        )
    except AmbError as e:
        log_error("LOOP", e.message, hint=e.hint)
        sys.exit(1)
    except Exception as e:
        log_error("LOOP", str(e))
        sys.exit(1)


if __name__ == "__main__":
    main()
