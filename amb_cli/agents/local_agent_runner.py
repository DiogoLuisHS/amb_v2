#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🤖 AMB_V2 - Local Agent (Antigravity & Jules) Runner
Localização: amb_cli/agents/local_agent_runner.py
Responsabilidade Única: Descobrir e executar personas de agentes estáticos definidos
no projeto, despachando para a API do Jules na nuvem ou executando localmente via Antigravity CLI.
"""

import os
import sys
import argparse
import subprocess
import re
from typing import Dict, Optional

from config.bootstrap import ensure_amb_env
ensure_amb_env()

from config import Colors, log, log_error, find_repo_root


class ApiExecutionError(Exception):
    """Exceção levantada quando há falha na execução de um agente local ou na nuvem."""
    def __init__(self, message: str, hint: Optional[str] = None):
        super().__init__(message)
        self.hint = hint


def get_personas_directory(custom_dir: Optional[str] = None) -> str:
    """Resolve e retorna o diretório de personas com prioridade para o .amb do projeto."""
    root = find_repo_root()
    if custom_dir:
        abs_custom = os.path.abspath(custom_dir)
        if not os.path.exists(abs_custom):
            os.makedirs(abs_custom, exist_ok=True)
        return abs_custom

    amb_personas = os.path.join(root, ".amb", "personas")
    if os.path.exists(amb_personas) and os.path.isdir(amb_personas):
        md_files = [f for f in os.listdir(amb_personas) if f.endswith(".md") and not f.startswith("_") and f.lower() != "readme.md"]
        if md_files:
            return os.path.abspath(amb_personas)

    jules_personas = os.path.join(root, ".jules", "personas")
    if os.path.exists(jules_personas) and os.path.isdir(jules_personas):
        return os.path.abspath(jules_personas)

    jules_dir = os.path.join(root, ".jules")
    if os.path.exists(jules_dir) and os.path.isdir(jules_dir):
        md_files = [f for f in os.listdir(jules_dir) if f.endswith(".md") and not f.startswith("_") and f.lower() != "readme.md"]
        if md_files:
            return os.path.abspath(jules_dir)

    candidates = [
        os.path.join(root, "amb_cli", "agents", "personas"),
        os.path.join(os.path.dirname(__file__), "personas"),
        os.path.join(root, "amb_cli", "integrations", "antigravity", "personas"),
    ]
    for p in candidates:
        if os.path.exists(p):
            return os.path.abspath(p)

    default_dir = os.path.join(root, ".amb", "personas")
    os.makedirs(default_dir, exist_ok=True)
    return default_dir


def discover_personas(personas_dir: str) -> Dict[str, Dict[str, str]]:
    """Varre dinamicamente a pasta de personas e extrai metadados dos arquivos markdown."""
    personas = {}
    if not os.path.exists(personas_dir):
        return personas

    for fname in sorted(os.listdir(personas_dir)):
        if not fname.endswith(".md"):
            continue
        if fname.lower() in ["readme.md"] or fname.startswith("_"):
            continue

        key = os.path.splitext(fname)[0].lower()
        fpath = os.path.join(personas_dir, fname)

        title = key.capitalize()
        summary = "Agente de manutenção especializado."
        content = ""

        try:
            with open(fpath, "r", encoding="utf-8", errors="replace") as f:
                content = f.read().strip()

            m_title = re.search(r"^#\s+(.+)$", content, re.MULTILINE)
            if m_title:
                title = m_title.group(1).strip()

            lines = [l.strip() for l in content.split("\n") if l.strip() and not l.startswith("#")]
            if lines:
                summary = lines[0][:120] + ("..." if len(lines[0]) > 120 else "")
        except Exception:
            pass

        personas[key] = {
            "key": key,
            "filename": fname,
            "path": fpath,
            "title": title,
            "summary": summary,
            "content": content
        }

    return personas


def list_personas(personas: Dict[str, Dict[str, str]], personas_dir: str) -> None:
    """Exibe no terminal a listagem dinâmica de todas as personas encontradas na pasta."""
    print("\n" + "=" * 75)
    print(f"{Colors.BOLD}{Colors.CYAN}🤖 PERSONAS DISPONÍVEIS NA PASTA ({len(personas)} encontradas){Colors.RESET}")
    print(f"📁 Diretório: {Colors.DIM}{personas_dir}{Colors.RESET}")
    print("=" * 75 + "\n")

    if not personas:
        print(f"{Colors.YELLOW}Nenhuma persona (.md) encontrada em: {personas_dir}{Colors.RESET}")
        print(f"Basta adicionar arquivos como '{personas_dir}/minha_persona.md' para ativá-las.\n")
        return

    for key, p in personas.items():
        print(f"  • {Colors.BOLD}{key:<12}{Colors.RESET} {Colors.GREEN}{p['title']}{Colors.RESET} (Arquivo: {p['filename']})")
        print(f"    Missão: {Colors.DIM}{p['summary']}{Colors.RESET}\n")

    print(f"{Colors.YELLOW}Como Executar:{Colors.RESET}")
    print(f"  • Despachar Jules (Padrão): amb agent --role <nome>  (ou python amb_cli/agents/local_agent_runner.py --role <nome>)")
    print(f"  • TODAS as Personas (Jules):  amb agent --all")
    print(f"  • Executar Local (agy CLI):   amb agent --role <nome> --agy (ou --local)\n")


def execute_single_persona(
    persona_data: Dict[str, str],
    task: Optional[str] = None,
    dispatch_jules: bool = True
) -> None:
    """Executa ou despacha uma persona específica."""
    title = persona_data["title"]
    base_content = persona_data["content"]
    root = find_repo_root()

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
                        full_prompt = f"{full_prompt}\n\n---\n\n🧠 HISTÓRICO & APRENDIZADOS PRÉVIOS DO REPOSITÓRIO ({rel_path}):\n{diario_content}"
                        break
            except Exception:
                pass

    if task:
        full_prompt = f"{full_prompt}\n\n---\n\n🎯 ESCOPO ESPECÍFICO ADICIONAL SOLICITADO:\n{task}"

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

    personas_dir = get_personas_directory(args.personas_dir)
    personas = discover_personas(personas_dir)

    if args.list or (not args.role and not args.all):
        list_personas(personas, personas_dir)
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
