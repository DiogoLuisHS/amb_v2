#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
================================================================================
🔁 AMB_V2 - LOOP AUTÔNOMO CONTÍNUO (JULES + ANTIGRAVITY)
================================================================================
Localização: amb_v2/agents/autonomous_loop.py
Responsabilidade Única: Executar ciclos contínuos de desenvolvimento autônomo,
enviando prompts estruturados (ou personas) ao Google Jules, monitorando
atividades em tempo real, respondendo dúvidas via Antigravity e aprovando PRs.

Exemplos de Uso:
  python amb_v2/agents/autonomous_loop.py --role relay
  python amb_v2/agents/autonomous_loop.py --role sentry --modules kanban,mindmap,meudia
  python amb_v2/agents/autonomous_loop.py --role relay --max-cycles 5
================================================================================
"""

import os
import sys
import time
import json
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
    "integrations/stitch", "integrations/stitch/tools",
    "integrations/antigravity", "integrations/antigravity/tools",
    "integrations/render", "integrations/render/tools",
]:
    _p = os.path.normpath(os.path.join(_AMB, *_sub.split("/")))
    if os.path.exists(_p) and _p not in sys.path:
        sys.path.insert(0, _p)

from config import Colors, log, log_error, find_repo_root, get_repo_name, require_env, AmbError
from jules_client import JulesClient
from antigravity_client import AntigravityClient
from auto_reply import advise_and_reply
from merge_session_pr import approve_and_merge_pr


PERSONAS = {
    "relay": {
        "title": "Autonomous Relay Engineer",
        "description": "Engenheiro de continuidade e refatoração incremental de código.",
        "prompt": (
            "Você é o Autonomous Relay Engineer.\n"
            "Sua missão é dar continuidade ao desenvolvimento, auditoria e aperfeiçoamento do projeto.\n"
            "1. Analise os arquivos recentes e identifique débitos técnicos, componentes incompletos ou oportunidades de melhoria.\n"
            "2. Implemente melhorias sólidas seguindo o Design System e padrões do repositório.\n"
            "3. Garanta 0 erros de TypeScript/compilação e integridade total nos testes.\n"
            "4. Crie commits atômicos e descritivos."
        )
    },
    "sentry": {
        "title": "Architecture & Type Safety Sentry",
        "description": "Auditoria de integridade de tipos, contratos de API e arquitetura.",
        "prompt": (
            "Você é o Architecture Sentry.\n"
            "Sua missão é auditar a integridade estrutural do repositório:\n"
            "1. Execute verificações rigorosas de tipos no projeto.\n"
            "2. Corrija any implícitos, tipos genéricos ausentes e inconsistências de schema.\n"
            "3. Verifique contratos de API entre frontend e backend.\n"
            "4. Garanta conformidade com as regras arquiteturais do projeto."
        )
    },
    "pixel": {
        "title": "Design System Artisan",
        "description": "Refinamento de UI/UX, tokens de design, layout e estética visual.",
        "prompt": (
            "Você é o Design System Artisan.\n"
            "Sua missão é elevar a experiência visual e consistência de UI/UX do projeto:\n"
            "1. Audite telas e componentes garantindo o uso rigoroso dos tokens do Design System.\n"
            "2. Implemente micro-interações, estados de hover e transições suaves.\n"
            "3. Assegure responsividade e suporte harmônico a Light e Dark Mode."
        )
    }
}


def load_persona_content(role: str) -> tuple[str, str]:
    """Carrega o conteúdo da persona a partir da pasta .amb/personas/ do projeto ativo."""
    root = find_repo_root()
    search_paths = [
        os.path.join(root, ".amb", "personas", f"{role}.md"),
        os.path.join(root, ".amb", f"{role}.md"),
        os.path.join(root, ".jules", "personas", f"{role}.md"),
        os.path.join(root, ".jules", f"{role}.md"),
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "personas", f"{role}.md")
    ]
    
    for persona_file in search_paths:
        if os.path.exists(persona_file):
            with open(persona_file, "r", encoding="utf-8", errors="replace") as pf:
                content = pf.read().strip()
            title = f"{role.title()} Persona"
            for line in content.splitlines():
                if line.startswith("# "):
                    title = line.replace("# ", "").strip()
                    break
            return title, content

    if role in PERSONAS:
        p = PERSONAS[role]
        return p["title"], p["prompt"]
    return f"{role.title()} Agent", f"Você é o agente especialista {role} do projeto."


def monitor_and_assist_session(client: JulesClient, session_id: str, auto_reply_ai: bool = True) -> str:
    """Monitora a sessão no Jules, respondendo planos e perguntas até a conclusão."""
    log("JULES-MONITOR", f"Iniciando acompanhamento da sessão {session_id}...", Colors.CYAN)
    last_act_id = None
    feedback_answered_for_turn = False

    while True:
        try:
            sess = client.get_session(session_id)
            state = sess.get("state", "UNKNOWN")

            acts_resp = client.list_activities(session_id=session_id, page_size=20)
            acts = acts_resp if isinstance(acts_resp, list) else acts_resp.get("activities", [])

            has_unapproved_plan = False
            if acts:
                latest = acts[0]
                aid = latest.get("id") or latest.get("name")
                if aid != last_act_id:
                    last_act_id = aid
                    feedback_answered_for_turn = False
                    
                    desc = latest.get("description") or latest.get("agentMessage", {}).get("text") or "Atividade"
                    print(f"[{Colors.BOLD}{state}{Colors.RESET}] {desc[:100]}...")

                for a in acts[:3]:
                    plan = a.get("plan") or a.get("agentMessage", {}).get("plan")
                    if plan and plan.get("state") == "PENDING_USER_APPROVAL":
                        has_unapproved_plan = True
                        break

            if state == "AWAITING_USER_FEEDBACK":
                if has_unapproved_plan:
                    if not feedback_answered_for_turn:
                        log("JULES", "Detectado plano pendente. Aprovando via :approvePlan...", Colors.GREEN)
                        try:
                            client.approve_plan(session_id)
                            feedback_answered_for_turn = True
                        except Exception as ep:
                            log_error("JULES", f"Falha ao aprovar plano pendente: {ep}")
                elif auto_reply_ai and not feedback_answered_for_turn:
                    log("ANTIGRAVITY", "Sessão aguardando feedback. Formulando resposta técnica...", Colors.HEADER)
                    try:
                        advise_and_reply(session_id=session_id, auto_approve=True)
                        feedback_answered_for_turn = True
                        print(f"[{Colors.GREEN}✔ Resposta enviada com sucesso para destravar o agente.{Colors.RESET}]\n")
                    except Exception as er:
                        log_error("ANTIGRAVITY", f"Falha ao auto-responder com IA: {er}")

            if state in ["COMPLETED", "SUCCEEDED"]:
                log("LOOP", f"🎉 Sessão {session_id} CONCLUÍDA com sucesso!", Colors.GREEN)
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
    role: Optional[str] = "relay",
    prompt_file: Optional[str] = None,
    modules: Optional[List[str]] = None,
    max_cycles: Optional[int] = None,
    delay_between_cycles: int = 8,
    branch: str = "develop",
    no_auto_merge: bool = False
):
    """Executa o loop contínuo de envio, monitoramento, auto-resposta e re-disparo."""
    repo_name = get_repo_name()
    client = JulesClient()
    source_name = f"sources/github/{repo_name}"

    cycle_count = 0
    modules_list = modules or [""]

    print("\n" + "=" * 75)
    print(f"{Colors.BOLD}{Colors.CYAN}🔁 INICIANDO LOOP AUTÔNOMO JULES + ANTIGRAVITY{Colors.RESET}")
    print(f"📁 Repositório: {Colors.BOLD}{repo_name}{Colors.RESET} (Branch: {branch})")
    print(f"🤖 Persona Base: {Colors.BOLD}{role or 'Prompt Customizado'}{Colors.RESET}")
    if modules and modules != [""]:
        print(f"🎯 Módulos em Rotação: {', '.join(modules)}")
    print(f"⏱️ Limite de Ciclos: {max_cycles if max_cycles else 'Infinito (Contínuo)'}")
    print("=" * 75 + "\n")

    while True:
        cycle_count += 1
        current_module = modules_list[(cycle_count - 1) % len(modules_list)]

        print("\n" + "#" * 75)
        print(f"🔄 {Colors.BOLD}CICLO #{cycle_count}{Colors.RESET}" + (f" - Foco no Módulo: [{current_module}]" if current_module else ""))
        print("#" * 75 + "\n")

        # 1. Carrega o Prompt
        if prompt_file and os.path.exists(prompt_file):
            with open(prompt_file, "r", encoding="utf-8", errors="replace") as pf:
                base_prompt = pf.read()
            title = f"Task: {Path(prompt_file).stem.replace('_', ' ').title()}"
        else:
            title, base_prompt = load_persona_content(role or "relay")

        if current_module:
            full_prompt = f"{base_prompt}\n\n---\n\n🎯 ESCOPO DESTA ITERAÇÃO:\nConcentre a auditoria e alinhamento estritamente no módulo: `{current_module}`."
            session_title = f"{title} [{current_module}] - Ciclo #{cycle_count}"
        else:
            full_prompt = base_prompt
            session_title = f"{title} - Ciclo #{cycle_count}"

        # 2. Despacho no Jules
        log("LOOP", f"Criando nova sessão no Google Jules...", Colors.CYAN)
        session_resp = client.create_session(
            prompt=full_prompt,
            source_name=source_name,
            title=session_title,
            base_branch=branch
        )

        session_id = session_resp.get("name", "").split("/")[-1] or session_resp.get("id", "")
        if not session_id:
            raise AmbError(f"Falha ao obter ID da sessão: {session_resp}")

        print(f"🎉 Sessão #{cycle_count} Criada: {Colors.GREEN}{session_id}{Colors.RESET}")
        print(f"🔗 Acompanhe: {Colors.BLUE}https://jules.google.com/sessions/{session_id}{Colors.RESET}\n")

        log("LOOP", "Aguardando provisionamento da VM no Jules (5s)...", Colors.DIM)
        time.sleep(5)

        # 3. Monitoramento + Auto-Resposta
        try:
            state = monitor_and_assist_session(client=client, session_id=session_id, auto_reply_ai=True)
            
            # 4. Aprovação e Integração do PR no Git (Se a sessão concluiu com sucesso)
            if state in ["COMPLETED", "SUCCEEDED"] and not no_auto_merge:
                log("GIT-MERGE", f"Iniciando aprovação e merge do Pull Request da sessão {session_id}...", Colors.HEADER)
                try:
                    approve_and_merge_pr(session_id=session_id, target_branch=branch)
                except Exception as em:
                    log_error("GIT-MERGE", f"Aviso na integração do PR: {em}")
        except KeyboardInterrupt:
            print(f"\n{Colors.YELLOW}Loop interrompido pelo usuário após o ciclo #{cycle_count}.{Colors.RESET}")
            break

        # 5. Checagem de Limite
        if max_cycles and cycle_count >= max_cycles:
            log("LOOP", f"Limite de {max_cycles} ciclos atingido. Encerrando loop com sucesso!", Colors.GREEN)
            break

        # 6. Pausa antes do próximo ciclo
        log("LOOP", f"Aguardando {delay_between_cycles}s para iniciar o próximo ciclo...", Colors.DIM)
        time.sleep(delay_between_cycles)


def main():
    parser = argparse.ArgumentParser(description="Loop Autônomo Contínuo Jules + Antigravity (AMB_V2)")
    parser.add_argument("--role", "-r", default="relay", help="Persona a ser executada em loop (ex: relay, sentry, pixel). Padrão: relay")
    parser.add_argument("--prompt", "-p", help="Caminho de um arquivo .md com prompt customizado.")
    parser.add_argument("--modules", "-m", help="Lista de módulos separados por vírgula para alternar por ciclo (ex: kanban,mindmap,meudia,agenda,projects).")
    parser.add_argument("--max-cycles", "-c", type=int, help="Número máximo de ciclos antes de parar (se omitido, roda continuamente).")
    parser.add_argument("--delay", "-d", type=int, default=8, help="Intervalo em segundos entre ciclos (Padrão: 8s).")
    parser.add_argument("--branch", "-b", default="develop", help="Branch alvo no GitHub (Padrão: develop).")
    parser.add_argument("--no-auto-merge", action="store_true", help="Não faz o merge automático do PR ao finalizar o ciclo.")

    args = parser.parse_args()

    modules_list = [m.strip() for m in args.modules.split(",") if m.strip()] if args.modules else None

    try:
        run_autonomous_loop(
            role=args.role,
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
