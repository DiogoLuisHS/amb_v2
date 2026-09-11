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
import subprocess
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
    "config",
    "agents",
    "pipeline",
    "dashboard",
    "dashboard/watchers",
    "integrations/jules",
    "integrations/jules/tools",
    "integrations/stitch",
    "integrations/antigravity",
    "integrations/render",
]:
    _p = os.path.normpath(os.path.join(_AMB, *_sub.split("/")))
    if os.path.exists(_p) and _p not in sys.path:
        sys.path.insert(0, _p)

from config import Colors, log, log_error, find_repo_root, get_repo_name, AmbError  # noqa: E402
from jules_client import JulesClient  # noqa: E402
from auto_reply import advise_and_reply  # noqa: E402
from local_agent_runner import get_personas_directory, discover_personas  # noqa: E402
from merge_session_pr import approve_and_merge_pr  # noqa: E402


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
            "4. Crie commits descritivos e abra o Pull Request.",
        ),
        "sentry": (
            "Architecture & Type Safety Sentry",
            "Você é o Architecture Sentry. Sua missão é auditar a integridade estrutural do repositório, contratos de API e tipagem estrita.",
        ),
        "pixel": (
            "Design System Artisan",
            "Você é o Design System Artisan. Sua missão é elevar a experiência visual e consistência de UI/UX do projeto.",
        ),
    }

    if clean_role in default_personas:
        return default_personas[clean_role]

    return f"{role.title()} Agent", f"Você é o agente especialista {role} do projeto."


def monitor_and_assist_session(
    client: JulesClient, session_id: str, auto_reply_ai: bool = True
) -> str:
    """Monitora a sessão no Jules, respondendo planos e perguntas até a conclusão.

    Usa análise estrita de turnos de conversa (get_last_conversation_turn) para:
    1. Nunca responder se a última mensagem da conversa já foi do usuário
    2. Detectar novas perguntas ou planos pendentes do agente mesmo em múltiplos turnos
    """
    log(
        "JULES-MONITOR",
        f"Iniciando acompanhamento da sessão {session_id}...",
        Colors.CYAN,
    )

    # Rastreia o ID da última mensagem/plano do AGENTE que já foi respondida
    last_answered_agent_msg_id = None

    while True:
        try:
            sess = client.get_session(session_id)
            state = sess.get("state", "UNKNOWN")

            acts_resp = client.list_activities(session_id=session_id, page_size=30)
            acts = (
                acts_resp
                if isinstance(acts_resp, list)
                else acts_resp.get("activities", [])
            )

            # Analisa o turno da conversa
            from auto_reply import get_last_conversation_turn

            turn_info = get_last_conversation_turn(acts)
            is_feedback_state = state in [
                "AWAITING_USER_FEEDBACK",
                "Awaiting User Feedback",
                "AWAITING_INPUT",
                "AWAITING_PLAN_APPROVAL",
            ]

            # Só atua se:
            # 1. O estado indicar espera de feedback/aprovação
            # 2. A última atividade de conversa for do AGENTE (não do USER)
            # 3. O ID da mensagem do agente for novo (não respondido ainda neste ciclo)
            if is_feedback_state and turn_info.get("is_awaiting_user_action", False):
                latest_agent_msg_id = turn_info.get("last_agent_msg_id")
                is_new_agent_msg = (
                    latest_agent_msg_id
                    and latest_agent_msg_id != last_answered_agent_msg_id
                )

                if is_new_agent_msg:
                    if turn_info.get("has_unapproved_plan", False):
                        p_title = turn_info.get(
                            "unapproved_plan_title", "Plano Proposto"
                        )
                        log(
                            "JULES",
                            f"Detectado plano pendente ('{p_title}'). Aprovando via :approvePlan...",
                            Colors.GREEN,
                        )
                        try:
                            client.approve_plan(session_id)
                            last_answered_agent_msg_id = latest_agent_msg_id
                        except Exception as ep:
                            log_error("JULES", f"Falha ao aprovar plano pendente: {ep}")

                    elif auto_reply_ai:
                        log(
                            "ANTIGRAVITY",
                            "Sessão aguardando feedback (nova pergunta detectada). Formulando resposta...",
                            Colors.HEADER,
                        )
                        try:
                            advise_and_reply(session_id=session_id, auto_approve=True)
                            last_answered_agent_msg_id = latest_agent_msg_id
                            print(
                                f"[{Colors.GREEN}✔ Resposta enviada com sucesso para destravar o agente.{Colors.RESET}]\n"
                            )
                        except Exception as er:
                            log_error(
                                "ANTIGRAVITY", f"Falha ao auto-responder com IA: {er}"
                            )

            if state in ["COMPLETED", "SUCCEEDED"]:
                log(
                    "LOOP",
                    f"🎉 Sessão {session_id} CONCLUÍDA com sucesso!",
                    Colors.GREEN,
                )
                # Aguarda Jules popular o PR nos outputs antes de tentar detectar
                log(
                    "LOOP",
                    "Aguardando Jules registrar o PR nos outputs (12s)...",
                    Colors.DIM,
                )
                time.sleep(12)
                return state
            elif state in ["FAILED", "CANCELLED", "CLOSED"]:
                log_error("LOOP", f"Sessão finalizada com estado: {state}")
                return state

            time.sleep(6)
        except KeyboardInterrupt:
            print(
                f"\n{Colors.YELLOW}Monitoramento interrompido pelo usuário.{Colors.RESET}"
            )
            raise
        except Exception as e:
            err_str = str(e)
            if "404" in err_str or "Not Found" in err_str:
                log(
                    "LOOP", "Aguardando inicialização da sessão na nuvem...", Colors.DIM
                )
            else:
                log_error("LOOP", f"Aviso de polling: {e}")
            time.sleep(6)


def _build_ai_context(
    full_prompt: str, current_module: Optional[str], cur_role: str
) -> str:
    """Enriquece o prompt com o roteiro arquitetural."""
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
        total_ctx_files = sum(len(layer["files"]) for layer in _ctx_layers.values())
        if total_ctx_files > 0:
            full_prompt = (
                f"{full_prompt}\n\n"
                f"---\n\n"
                f"## 📂 ROTEIRO DE LEITURA ARQUITETURAL (gerado por `amb context {_ctx_query}`)\n\n"
                f"**Use este roteiro para iniciar sua análise sem precisar explorar o repositório do zero.**\n"
                f"Leia os arquivos na ordem apresentada (DB → Repositórios → Services → Controllers → UI):\n\n"
                f"{_ctx_md}"
            )
            log(
                "LOOP",
                f"Roteiro arquitetural '{_ctx_query}' ({total_ctx_files} arquivos) anexado ao prompt.",
                Colors.GREEN,
            )
    except Exception as ctx_err:
        log("LOOP", f"Aviso: amb context não disponível — {ctx_err}", Colors.DIM)

    return full_prompt


def _dispatch_jules_session(
    client: JulesClient,
    full_prompt: str,
    source_name: str,
    session_title: str,
    branch: str,
) -> str:
    """Cria a sessão no Jules e retorna o ID."""
    log("LOOP", "Criando sessão para persona no Google Jules...", Colors.CYAN)

    session_resp = client.create_session(
        prompt=full_prompt,
        source_name=source_name,
        title=session_title,
        base_branch=branch,
    )

    session_id = session_resp.get("name", "").split("/")[-1] or session_resp.get(
        "id", ""
    )
    if not session_id:
        raise AmbError(f"Falha ao obter ID da sessão: {session_resp}")

    print(f"🎉 Sessão Criada: {Colors.GREEN}{session_id}{Colors.RESET}")
    print(
        f"🔗 Acompanhe: {Colors.BLUE}https://jules.google.com/session/{session_id}{Colors.RESET}\n"
    )

    log("LOOP", "Aguardando provisionamento da VM no Jules (5s)...", Colors.DIM)
    time.sleep(5)

    return session_id


def _handle_pr_merge(
    session_id: str, branch: str, repo_root: str, completed_cycles: int
) -> None:
    """Aprova e integra o Pull Request no Git local."""
    log(
        "GIT-MERGE",
        f"Verificando Pull Request da sessão {session_id}...",
        Colors.HEADER,
    )
    try:
        merged = approve_and_merge_pr(session_id=session_id, target_branch=branch)
        if merged:
            log(
                "GIT-SYNC",
                f"✔ Sincronização concluída com sucesso! origin/{branch} atualizado com as mudanças do Ciclo #{completed_cycles}.",
                Colors.GREEN,
            )
            # Garante que o git local puxa e valida origin
            subprocess.run(
                ["git", "pull", "origin", branch],
                cwd=repo_root,
                capture_output=True,
                shell=True,
            )
    except Exception as em:
        log_error("GIT-MERGE", f"Aviso na integração do PR: {em}")


def run_autonomous_loop(
    role: Optional[str] = None,
    all_personas: bool = False,
    prompt_file: Optional[str] = None,
    modules: Optional[List[str]] = None,
    max_cycles: Optional[int] = None,
    delay_between_cycles: int = 8,
    branch: Optional[str] = None,
    no_auto_merge: bool = False,
):
    """Executa o loop contínuo de envio, monitoramento, auto-resposta e re-disparo para uma ou todas as personas."""
    repo_name = get_repo_name()
    repo_root = find_repo_root()
    client = JulesClient()
    source_name = f"sources/github/{repo_name}"

    # Auto-detecta branch atual do Git local se não fornecida explicitamente
    if not branch or branch in ["develop", "main"]:
        try:
            b_proc = subprocess.run(
                ["git", "branch", "--show-current"],
                cwd=repo_root,
                capture_output=True,
                text=True,
                check=False,
            )
            cur_b = b_proc.stdout.strip()
            if cur_b:
                branch = cur_b
        except Exception:
            pass
    branch = branch or "main"

    personas_dir = get_personas_directory()
    discovered = discover_personas(personas_dir)

    if all_personas:
        roles_to_run = (
            list(discovered.keys()) if discovered else ["relay", "sentry", "pixel"]
        )
    elif role:
        roles_to_run = [role]
    else:
        roles_to_run = ["relay"]

    modules_list = modules or [""]

    print("\n" + "=" * 75)
    print(
        f"{Colors.BOLD}{Colors.CYAN}🔁 INICIANDO LOOP AUTÔNOMO JULES + ANTIGRAVITY{Colors.RESET}"
    )
    print(f"📁 Repositório: {Colors.BOLD}{repo_name}{Colors.RESET} (Branch: {branch})")
    print(
        f"🤖 Personas no Ciclo ({len(roles_to_run)}): {Colors.BOLD}{', '.join(roles_to_run)}{Colors.RESET}"
    )
    if modules and modules != [""]:
        print(f"🎯 Módulos em Rotação: {', '.join(modules)}")
    print(
        f"⏱️ Limite de Ciclos: {f'{max_cycles} rodadas completas' if max_cycles else 'Infinito (Contínuo)'}"
    )
    print("=" * 75 + "\n")

    completed_cycles = 0

    while True:
        completed_cycles += 1

        print("\n" + "#" * 75)
        print(
            f"🔄 {Colors.BOLD}CICLO #{completed_cycles} DE {max_cycles if max_cycles else '∞'}{Colors.RESET}"
        )
        print("#" * 75 + "\n")

        for persona_idx, cur_role in enumerate(roles_to_run, 1):
            current_module = modules_list[(completed_cycles - 1) % len(modules_list)]

            print(
                f"\n📦 [{persona_idx}/{len(roles_to_run)}] Executando Persona: {Colors.BOLD}{cur_role.upper()}{Colors.RESET}"
                + (f" - Módulo: [{current_module}]" if current_module else "")
            )

            # 1. Carrega o Prompt
            if prompt_file and os.path.exists(prompt_file):
                with open(prompt_file, "r", encoding="utf-8", errors="replace") as pf:
                    base_prompt = pf.read()
                title = f"Task: {Path(prompt_file).stem.replace('_', ' ').title()}"
            else:
                title, base_prompt = load_persona_content(cur_role)

            if current_module:
                full_prompt = f"{base_prompt}\n\n---\n\n🎯 ESCOPO DESTA ITERAÇÃO:\nConcentre a auditoria e alinhamento estritamente no módulo: `{current_module}`."
                session_title = (
                    f"{title} [{current_module}] - Ciclo #{completed_cycles}"
                )
            else:
                session_title = f"{title} - Ciclo #{completed_cycles}"
                full_prompt = base_prompt

            # C5: Enriquecer o prompt com o roteiro arquitetural do amb context
            full_prompt = _build_ai_context(full_prompt, current_module, cur_role)

            # 2. Despacho no Jules
            try:
                session_id = _dispatch_jules_session(
                    client, full_prompt, source_name, session_title, branch
                )

                # 3. Monitoramento + Auto-Resposta
                state = monitor_and_assist_session(
                    client=client, session_id=session_id, auto_reply_ai=True
                )

                # 4. Aprovação e Integração do PR no Git
                if state in ["COMPLETED", "SUCCEEDED"] and not no_auto_merge:
                    _handle_pr_merge(session_id, branch, repo_root, completed_cycles)

            except KeyboardInterrupt:
                print(f"\n{Colors.YELLOW}Loop interrompido pelo usuário.{Colors.RESET}")
                return
            except Exception as e:
                log_error("LOOP", f"Erro no processamento da persona '{cur_role}': {e}")

            if len(roles_to_run) > 1:
                log(
                    "LOOP",
                    f"Pausa de {delay_between_cycles}s antes da próxima persona...",
                    Colors.DIM,
                )
                time.sleep(delay_between_cycles)

        # Checagem de Limite de Ciclos Globais
        if max_cycles and completed_cycles >= max_cycles:
            log(
                "LOOP",
                f"Limite de {max_cycles} ciclos atingido. Todas as personas foram executadas com sucesso!",
                Colors.GREEN,
            )
            break

        wait_seconds = max(delay_between_cycles, 10)
        log(
            "LOOP",
            f"Ciclo #{completed_cycles} concluído. Aguardando {wait_seconds}s para propagação do Git antes do Ciclo #{completed_cycles + 1}...",
            Colors.CYAN,
        )
        time.sleep(wait_seconds)


def main():
    parser = argparse.ArgumentParser(
        description="Loop Autônomo Contínuo Jules + Antigravity (AMB_V2)"
    )
    parser.add_argument(
        "--role",
        "-r",
        help="Persona a ser executada em loop (ex: relay, sentry, pixel).",
    )
    parser.add_argument(
        "--all",
        "-a",
        action="store_true",
        help="Executa todas as personas disponíveis da pasta em cada ciclo.",
    )
    parser.add_argument(
        "--prompt", "-p", help="Caminho de um arquivo .md com prompt customizado."
    )
    parser.add_argument(
        "--modules",
        "-m",
        help="Lista de módulos separados por vírgula para alternar por ciclo (ex: kanban,agenda,projects).",
    )
    parser.add_argument(
        "--max-cycles",
        "-c",
        type=int,
        help="Número máximo de ciclos antes de parar (se omitido, roda continuamente).",
    )
    parser.add_argument(
        "--delay",
        "-d",
        type=int,
        default=8,
        help="Intervalo em segundos entre ciclos (Padrão: 8s).",
    )
    parser.add_argument(
        "--branch",
        "-b",
        default="develop",
        help="Branch alvo no GitHub (Padrão: develop).",
    )
    parser.add_argument(
        "--no-auto-merge",
        action="store_true",
        help="Não faz o merge automático do PR ao finalizar o ciclo.",
    )

    args = parser.parse_args()

    modules_list = (
        [m.strip() for m in args.modules.split(",") if m.strip()]
        if args.modules
        else None
    )

    try:
        run_autonomous_loop(
            role=args.role,
            all_personas=args.all,
            prompt_file=args.prompt,
            modules=modules_list,
            max_cycles=args.max_cycles,
            delay_between_cycles=args.delay,
            branch=args.branch,
            no_auto_merge=args.no_auto_merge,
        )
    except AmbError as e:
        log_error("LOOP", e.message, hint=e.hint)
        sys.exit(1)
    except Exception as e:
        log_error("LOOP", str(e))
        sys.exit(1)


if __name__ == "__main__":
    main()
