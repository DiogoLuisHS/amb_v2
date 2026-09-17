#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔁 AMB_V2 - Loop Autônomo Contínuo de Engenharia (Jules + Antigravity)
Localização: amb_cli/agents/autonomous_loop.py
Responsabilidade Única: Orquestrar ciclos contínuos de desenvolvimento autônomo,
delegando monitoramento a loop_core.session_assistant e despacho a loop_core.cycle_dispatcher.

Exemplos de Uso:
  amb agent --role engineer --loop --max-cycles 3
  amb agent --all --loop --max-cycles 2
  python amb_cli/agents/autonomous_loop.py --all --max-cycles 2
"""

import os
import sys
import time
import argparse
from pathlib import Path
from typing import List, Optional

from config.bootstrap import ensure_amb_env
ensure_amb_env()

from config import Colors, log, log_error, find_repo_root, get_repo_name, AmbError
from integrations.git.git_service import GitService
from integrations.jules.jules_client import JulesClient
from agents.local_agent_runner import get_personas_directory, discover_personas
from agents.loop_core.session_assistant import monitor_and_assist_session
from agents.loop_core.cycle_dispatcher import (
    build_ai_context,
    dispatch_jules_session,
    handle_pr_merge,
)


def load_persona_content(role: str) -> tuple[str, str]:
    """Carrega dinamicamente o conteúdo da persona."""
    personas_dir = get_personas_directory()
    personas = discover_personas(personas_dir)
    clean_role = role.lower().replace(".md", "").strip()

    if clean_role in personas:
        p = personas[clean_role]
        return p["title"], p["content"]

    default_personas = {
        "engineer": (
            "Autonomous Software Engineer",
            "Você é o Autonomous Software Engineer. Sua missão é dar continuidade ao desenvolvimento, auditoria e aperfeiçoamento do projeto.\n"
            "1. Analise arquivos recentes e identifique débitos técnicos, bugs ou novas funcionalidades.\n"
            "2. Implemente melhorias sólidas seguindo o Design System e padrões arquiteturais do repositório.\n"
            "3. Garanta integridade total passando na suíte de testes e validação de QA configurada.\n"
            "4. Crie commits descritivos e abra o Pull Request quando concluído.",
        ),
    }

    if clean_role in default_personas:
        return default_personas[clean_role]

    return f"{role.title()} Agent", f"Você é o agente especialista {role} do projeto."


def run_autonomous_loop(
    role: Optional[str] = None,
    all_personas: bool = False,
    prompt_file: Optional[str] = None,
    modules: Optional[List[str]] = None,
    max_cycles: Optional[int] = None,
    delay_between_cycles: int = 8,
    branch: Optional[str] = None,
    no_auto_merge: bool = False,
) -> None:
    """Executa o loop contínuo de envio, monitoramento, auto-resposta e re-disparo para uma ou todas as personas."""
    repo_name = get_repo_name()
    repo_root = find_repo_root()
    client = JulesClient()
    source_name = f"sources/github/{repo_name}"

    if not branch or branch in ["develop", "main"]:
        branch = GitService(repo_root=repo_root).get_current_branch(cwd=repo_root)
    branch = branch or "main"

    personas_dir = get_personas_directory()
    discovered = discover_personas(personas_dir)

    # Resolução de Prompts (arquivo único ou diretório) vs Personas
    prompts_to_run: List[Path] = []
    if prompt_file:
        p_target = Path(prompt_file)
        if p_target.is_dir():
            prompts_to_run = sorted(
                [
                    p
                    for p in p_target.glob("*.md")
                    if p.name.lower() != "readme.md" and not p.name.startswith(("_", "."))
                ]
            )
        elif p_target.is_file():
            prompts_to_run = [p_target]

    if prompts_to_run:
        items_to_run = [{"type": "prompt", "path": p, "name": p.stem} for p in prompts_to_run]
    elif all_personas:
        items_to_run = [{"type": "persona", "name": k} for k in discovered.keys()] if discovered else [{"type": "persona", "name": "engineer"}]
    elif role:
        items_to_run = [{"type": "persona", "name": role}]
    else:
        items_to_run = [{"type": "persona", "name": k} for k in discovered.keys()] if discovered else [{"type": "persona", "name": "engineer"}]

    modules_list = modules or [""]

    print("\n" + "=" * 75)
    print(
        f"{Colors.BOLD}{Colors.CYAN}🔁 INICIANDO LOOP AUTÔNOMO JULES + ANTIGRAVITY{Colors.RESET}"
    )
    print(f"📁 Repositório: {Colors.BOLD}{repo_name}{Colors.RESET} (Branch: {branch})")
    if prompts_to_run:
        print(
            f"📄 Prompts no Lote ({len(prompts_to_run)}): {Colors.BOLD}{', '.join([p.name for p in prompts_to_run])}{Colors.RESET}"
        )
    else:
        print(
            f"🤖 Personas no Ciclo ({len(items_to_run)}): {Colors.BOLD}{', '.join([it['name'] for it in items_to_run])}{Colors.RESET}"
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

        for item_idx, item in enumerate(items_to_run, 1):
            current_module = modules_list[(completed_cycles - 1) % len(modules_list)]
            item_name = item["name"]

            if item["type"] == "prompt":
                p_path: Path = item["path"]
                print(
                    f"\n📦 [{item_idx}/{len(items_to_run)}] Executando Prompt: {Colors.BOLD}{item_name}{Colors.RESET}"
                )
                base_prompt = p_path.read_text(encoding="utf-8", errors="replace")
                title = f"Task: {p_path.stem.replace('_', ' ').title()}"
                session_title = f"{title} - Ciclo #{completed_cycles}"
                full_prompt = build_ai_context(base_prompt, None, p_path.stem)
            else:
                print(
                    f"\n📦 [{item_idx}/{len(items_to_run)}] Executando Persona: {Colors.BOLD}{item_name.upper()}{Colors.RESET}"
                    + (f" - Módulo: [{current_module}]" if current_module else "")
                )
                title, base_prompt = load_persona_content(item_name)
                if current_module:
                    full_prompt = (
                        f"{base_prompt}\n\n---\n\n🎯 ESCOPO DESTA ITERAÇÃO:\n"
                        f"Concentre a auditoria e alinhamento estritamente no módulo: `{current_module}`."
                    )
                    session_title = f"{title} [{current_module}] - Ciclo #{completed_cycles}"
                else:
                    session_title = f"{title} - Ciclo #{completed_cycles}"
                    full_prompt = base_prompt
                full_prompt = build_ai_context(full_prompt, current_module, item_name)

            # Despacho no Jules
            try:
                session_id = dispatch_jules_session(
                    client, full_prompt, source_name, session_title, branch
                )

                # Monitoramento + Auto-Resposta
                state = monitor_and_assist_session(
                    client=client, session_id=session_id, auto_reply_ai=True
                )

                # Aprovação e Integração do PR no Git
                if state in ["COMPLETED", "SUCCEEDED"] and not no_auto_merge:
                    handle_pr_merge(session_id, branch, repo_root, completed_cycles)

            except KeyboardInterrupt:
                print(f"\n{Colors.YELLOW}Loop interrompido pelo usuário.{Colors.RESET}")
                return
            except Exception as e:
                log_error("LOOP", f"Erro no processamento de '{item_name}': {e}")

            if len(items_to_run) > 1:
                log(
                    "LOOP",
                    f"Pausa de {delay_between_cycles}s antes do próximo item...",
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
    parser = argparse.ArgumentParser(description="Loop Autônomo Contínuo Jules + Antigravity (AMB_V2)")
    parser.add_argument("--role", "-r", help="Persona a ser executada em loop (ex: engineer).")
    parser.add_argument("--all", "-a", action="store_true", help="Executa todas as personas em cada ciclo.")
    parser.add_argument("--prompt", "-p", help="Arquivo markdown (.md) ou diretório de prompts em lote.")
    parser.add_argument("--modules", "-m", help="Módulos separados por vírgula para alternar por ciclo.")
    parser.add_argument("--max-cycles", "-c", type=int, help="Número máximo de ciclos antes de parar.")
    parser.add_argument("--delay", "-d", type=int, default=8, help="Intervalo em segundos entre ciclos (Padrão: 8s).")
    parser.add_argument("--branch", "-b", default="develop", help="Branch alvo no GitHub (Padrão: develop).")
    parser.add_argument("--no-auto-merge", action="store_true", help="Não faz o merge automático do PR.")

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
