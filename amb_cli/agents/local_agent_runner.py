#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Descobre e executa personas de agentes estáticos (remoto ou local).
"""

import os
import sys
import argparse
import subprocess
import re
from typing import Dict, Optional

from core.bootstrap import ensure_amb_env
ensure_amb_env()

from core import Colors, log, log_error
from workspace import find_repo_root
from amb_cli.agents.persona_engine import PersonaEngine


class ApiExecutionError(Exception):
    """Exceção levantada quando há falha na execução de um agente local ou na nuvem."""
    def __init__(self, message: str, hint: Optional[str] = None):
        super().__init__(message)
        self.hint = hint


def execute_single_persona(
    persona_data: Dict[str, str],
    task: Optional[str] = None,
    dispatch_jules: bool = True
) -> None:
    """Executa ou despacha uma persona específica."""
    title = persona_data["title"]
    root = find_repo_root()
    engine = PersonaEngine(repo_root=root)
    base_content = engine.render_persona_template(persona_data["content"])

    full_prompt = base_content

    key = persona_data.get("key", "")
    diario_candidates = [
        os.path.join(root, ".amb", "diarios", f"{key}.md"),
        os.path.join(root, ".jules", "diarios", f"{key}.md"),
    ]
    for dpath in diario_candidates:
        if os.path.exists(dpath):
            try:
                with open(dpath, "r", encoding="utf-8", errors="replace") as df:
                    diario_content = df.read().strip()
                    if diario_content:
                        rel_path = os.path.relpath(dpath, root).replace("\\", "/")
                        full_prompt = f"{full_prompt}\n\n---\n\n## 🧠 Histórico do Repositório ({rel_path})\n{diario_content}"
                        break
            except (OSError, IOError) as e:
                log_error("AGENT", f"Erro ao ler diário '{dpath}': {e}")

    if task:
        full_prompt = f"{full_prompt}\n\n---\n\n## 🎯 Instrução Específica Adicional\n{task}"

    print("\n" + "=" * 75)
    print(f"🤖 {Colors.BOLD}EXECUTANDO PERSONA:{Colors.RESET} {title}")
    print(f"📄 {Colors.BOLD}ARQUIVO:{Colors.RESET} {persona_data['filename']}")
    print(f"📁 {Colors.BOLD}LOCAL:{Colors.RESET} {persona_data['path']}")
    print(f"🎯 {Colors.BOLD}MODO:{Colors.RESET} {'Google Jules Cloud VM' if dispatch_jules else 'Antigravity Local (agy CLI)'}")
    print("=" * 75 + "\n")

    if dispatch_jules:
        from integrations.jules.tools.create_session import create_session
        log("AGENT", f"Despachando '{title}' para o Google Jules...", Colors.CYAN)
        res = create_session(
            prompt=full_prompt,
            title=title
        )
        sid = res.get("name", "").split("/")[-1] or res.get("id")
        log("AGENT", f"🎉 Sessão do Jules criada com sucesso! ID: {sid}", Colors.GREEN)
        print(f"🔗 Painel Web: https://jules.google.com/session/{sid}")
        print(f"👉 Para monitorar: amb jules get {sid}\n")
        return

    run_local_agent(full_prompt, root, title)


def run_local_agent(full_prompt: str, root: str, title: str) -> int:
    """Executa o agente localmente usando o Google Antigravity SDK (agy CLI)."""
    log("AGENT", f"Iniciando agente local no repositório...", Colors.CYAN)
    try:
        proc = subprocess.run(
            ["agy", "-p", full_prompt],
            cwd=root,
            text=True,
            encoding="utf-8",
            errors="replace"
        )
        if proc.returncode != 0:
            raise ApiExecutionError(f"Agente local encerrou com código {proc.returncode}")
        log("AGENT", f"✅ Execução de '{title}' finalizada com sucesso!", Colors.GREEN)
        return proc.returncode
    except FileNotFoundError:
        raise ApiExecutionError(
            "CLI 'agy' não encontrada no PATH do sistema.",
            hint="Certifique-se de que o Google Antigravity SDK / agy CLI está instalado e acessível no terminal."
        )


def main() -> None:
    parser = argparse.ArgumentParser(description="Executor dinâmico de personas do repositório ativo (lê dinamicamente da pasta .amb/ ou .jules/).")
    parser.add_argument("--role", "-r", help="Nome da persona a ser executada (ex: engineer, etc.).")
    parser.add_argument("--all", "-a", action="store_true", help="Executa TODAS as personas encontradas na pasta sequencialmente.")
    parser.add_argument("--task", "-t", help="Instrução ou escopo específico adicional para anexar ao prompt da persona.")
    parser.add_argument("--list", "-l", action="store_true", help="Lista todas as personas disponíveis na pasta e encerra.")
    parser.add_argument("--agy", "--local", action="store_true", default=False, help="Executa o agente localmente via agy CLI em vez de despachar para o Google Jules.")
    parser.add_argument("--dispatch-jules", "-j", action="store_true", help="(Legado) Força o despacho para o Google Jules na nuvem (comportamento padrão).")
    parser.add_argument("--personas-dir", help="Caminho customizado da pasta de personas.")

    args = parser.parse_args()

    dispatch_jules = not args.agy

    engine = PersonaEngine()
    personas_dir = engine.get_personas_directory(args.personas_dir)
    personas = engine.discover_personas(args.personas_dir)

    if args.list or (not args.role and not args.all):
        engine.list_personas(personas, personas_dir)
        return

    if args.all:
        if not personas:
            log_error("AGENT", f"Nenhuma persona encontrada em {personas_dir}")
            sys.exit(1)

        print("\n" + "=" * 75)
        print(f"{Colors.BOLD}{Colors.CYAN}🚀 INICIANDO EXECUÇÃO EM LOTE DE TODAS AS {len(personas)} PERSONAS{Colors.RESET}")
        print("=" * 75)

        for idx, (key, p_data) in enumerate(personas.items(), 1):
            print(f"\n{'#' * 75}")
            print(f"📦 [{idx}/{len(personas)}] Processando Persona: {p_data['title']}")
            print(f"{'#' * 75}")
            try:
                execute_single_persona(
                    persona_data=p_data,
                    task=args.task,
                    dispatch_jules=dispatch_jules
                )
            except Exception as e:
                log_error("AGENT", f"Falha na persona '{key}': {e}")

        print(f"\n{Colors.BOLD}{Colors.GREEN}🎉 Execução em lote de todas as personas concluída!{Colors.RESET}\n")
        return

    clean_role = args.role.lower().replace(".md", "").strip()
    if clean_role not in personas:
        log_error(
            "AGENT",
            f"Persona '{args.role}' não encontrada em {personas_dir}.",
            hint=f"Personas disponíveis: {', '.join(personas.keys())}. Ou use --list para ver todas."
        )
        sys.exit(1)

    try:
        execute_single_persona(
            persona_data=personas[clean_role],
            task=args.task,
            dispatch_jules=dispatch_jules
        )
    except Exception as e:
        log_error("AGENT", str(e))
        sys.exit(1)


if __name__ == "__main__":
    main()
