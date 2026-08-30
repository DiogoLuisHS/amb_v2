#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🚀 AMB_V2 - CLI Global e Unificada de Automação de Engenharia
Comando: `amb`
Responsabilidade Única: Ponto de entrada CLI que detecta o repositório onde o terminal
está aberto e roteia subcomandos (setup, monitor, advisor, agent, jules, stitch, render, pipeline).
"""

import os
import sys
import argparse
import subprocess

# Injeta todos os submódulos de amb_v2 no sys.path
_AMB_ROOT = os.path.abspath(os.path.dirname(__file__))
for _sub in [
    "config", "agents", "architecture", "pipeline", "dashboard", "dashboard/watchers",
    "integrations/jules", "integrations/jules/tools",
    "integrations/stitch", "integrations/stitch/tools",
    "integrations/antigravity", "integrations/antigravity/tools",
    "integrations/render", "integrations/render/tools",
]:
    _p = os.path.normpath(os.path.join(_AMB_ROOT, *_sub.split("/")))
    if os.path.exists(_p) and _p not in sys.path:
        sys.path.insert(0, _p)

from config import Colors, log, log_error, find_repo_root, load_env_file, get_repo_name, AmbError


def banner():
    print(f"\n{Colors.BOLD}{Colors.CYAN}==========================================================================={Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.CYAN}🚀 AMB_V2 CLI — SISTEMA UNIFICADO DE AUTOMAÇÃO E AGENTES{Colors.RESET}")
    print(f"📁 Repositório Ativo: {Colors.GREEN}{get_repo_name()}{Colors.RESET} ({find_repo_root()})")
    print(f"{Colors.BOLD}{Colors.CYAN}==========================================================================={Colors.RESET}\n")


def cmd_schema(args):
    """Exibe o catálogo de schemas e tabelas do banco de dados (Read-Only)."""
    from db_schema_reader import show_schema
    show_schema(filter_term=args.target)


def cmd_context(args):
    """Gera o roteiro de arquivos ordenados por camadas de dependência para a IA."""
    from ai_context_builder import generate_context
    generate_context(target=args.module, output_json=args.json)


def cmd_setup(args):
    """Executa o assistente de setup no repositório atual."""
    from setup_project import run_setup, print_setup_prompt
    if getattr(args, "prompt", False):
        print_setup_prompt()
    else:
        run_setup(interactive=not args.auto)


def cmd_prompt(args):
    """Exibe o Prompt Mestre de Auto-Configuração de IA para novos projetos."""
    from setup_project import print_setup_prompt
    print_setup_prompt()


def cmd_check(args):
    """Verifica e valida as chaves de API e configurações do projeto ativo."""
    import config as cfg
    cfg.main()


def cmd_monitor(args):
    """Inicia o sentinela unificado em tempo real."""
    from unified_monitor import UnifiedMonitor
    monitor = UnifiedMonitor(interval=args.interval, auto_approve=args.auto_approve)
    monitor.run(check_once=args.check_once)


def cmd_advisor(args):
    """Executa o conselheiro cognitivo para responder chats pendentes."""
    import auto_advisor
    if args.auto_approve:
        auto_advisor.auto_reply_all_pending(auto_approve=True)
    else:
        auto_advisor.interactive_advisor_menu()


def cmd_agent(args):
    """Executa o runner dinâmico de personas."""
    import local_agent_runner as runner
    personas_dir = runner.get_personas_directory(args.personas_dir)
    personas = runner.discover_personas(personas_dir)

    if args.list or (not args.role and not args.all):
        runner.list_personas(personas, personas_dir)
        return

    if args.all:
        for idx, (k, p_data) in enumerate(personas.items(), 1):
            print(f"\n📦 [{idx}/{len(personas)}] Processando Persona: {p_data['title']}")
            runner.execute_single_persona(p_data, task=args.task, dispatch_jules=args.dispatch_jules)
        return

    clean_role = args.role.lower().replace(".md", "").strip()
    if clean_role not in personas:
        log_error("AGENT", f"Persona '{args.role}' não encontrada em {personas_dir}.", hint=f"Disponíveis: {', '.join(personas.keys())}")
        sys.exit(1)

    runner.execute_single_persona(personas[clean_role], task=args.task, dispatch_jules=args.dispatch_jules)


def cmd_jules(args):
    """Roteia comandos específicos da integração com o Google Jules."""
    sub = args.jules_cmd

    if sub == "list":
        from jules_client import JulesClient
        client = JulesClient()
        sessions = client.list_sessions(page_size=args.limit)
        log("JULES", f"Sessões recentes ({len(sessions)}):", Colors.CYAN)
        for s in sessions:
            sid = s.get("name", "").split("/")[-1] or s.get("id")
            title = s.get("title") or "Sem título"
            state = s.get("state", "UNKNOWN")
            print(f"  • [{Colors.BOLD}{sid}{Colors.RESET}] {title} ({state})")
            print(f"    https://jules.google.com/session/{sid}")

    elif sub == "get":
        from get_session import main as get_session_main
        sys.argv = ["get_session.py", "--session-id", args.session_id] + (["--json"] if args.json else [])
        get_session_main()

    elif sub == "create":
        from create_session import create_session
        res = create_session(prompt=args.prompt, title=args.title)
        sid = res.get("name", "").split("/")[-1] or res.get("id")
        log("JULES", f"Sessão criada com sucesso: {sid}", Colors.GREEN)
        print(f"Painel: https://jules.google.com/session/{sid}")

    elif sub == "reply":
        from auto_reply import auto_reply_session
        auto_reply_session(session_id=args.session_id, auto_approve=args.auto_approve)

    elif sub == "approve":
        from approve_plan import approve_plan
        approve_plan(session_id=args.session_id)

    else:
        print("Subcomando do Jules inválido. Use 'amb jules --help'.")


def cmd_stitch(args):
    """Roteia comandos da integração com o Google Stitch SDK."""
    sub = args.stitch_cmd

    if sub == "generate":
        import generate_screen
        sys.argv = ["generate_screen.py", "--prompt", args.prompt] + (["--title", args.title] if args.title else [])
        generate_screen.main()

    elif sub == "refine":
        import edit_screen
        sys.argv = ["edit_screen.py", "--screen-id", args.screen_id, "--prompt", args.prompt]
        edit_screen.main()

    elif sub == "get":
        import get_screen
        sys.argv = ["get_screen.py", "--screen-id", args.screen_id]
        get_screen.main()

    else:
        print("Subcomando do Stitch inválido. Use 'amb stitch --help'.")


def cmd_render(args):
    """Roteia comandos do Render Cloud."""
    sub = args.render_cmd
    if sub == "status":
        import get_deploy_status
        get_deploy_status.main()
    elif sub == "logs":
        import fetch_logs
        fetch_logs.main()
    elif sub == "deploy":
        import trigger_deploy
        trigger_deploy.main()
    else:
        print("Subcomando do Render inválido. Use 'amb render --help'.")


def cmd_pipeline(args):
    """Executa o pipeline completo Design-to-Deploy."""
    from pipeline import PipelineOrchestrator
    PipelineOrchestrator.run(prompt_file=args.template)


def main():
    load_env_file()

    parser = argparse.ArgumentParser(
        prog="amb",
        description="CLI Unificada do AMB_V2 — Automação, Agentes e Integrações para Monorepos e Projetos."
    )
    subparsers = parser.add_subparsers(dest="command", help="Comandos disponíveis")

    # 1. amb setup
    p_setup = subparsers.add_parser("setup", aliases=["init"], help="Analisa e configura o projeto atual.")
    p_setup.add_argument("--auto", action="store_true", help="Executa o setup de forma automática/não-interativa.")
    p_setup.add_argument("--prompt", "-p", action="store_true", help="Exibe o Prompt Mestre de Auto-Configuração para colar em IAs.")
    p_setup.set_defaults(func=cmd_setup)

    # 1.1 amb prompt
    p_prompt = subparsers.add_parser("prompt", help="Exibe o Prompt Mestre de Auto-Configuração para colar em IAs.")
    p_prompt.set_defaults(func=cmd_prompt)

    # 2. amb check
    p_check = subparsers.add_parser("check", aliases=["status"], help="Valida chaves e configurações do projeto ativo.")
    p_check.set_defaults(func=cmd_check)

    # 3. amb monitor
    p_mon = subparsers.add_parser("monitor", help="Sentinela em tempo real (Jules + Render).")
    p_mon.add_argument("--auto-approve", "-y", action="store_true", help="Aprova/responde chats automaticamente.")
    p_mon.add_argument("--check-once", action="store_true", help="Executa apenas uma rodada de checagem.")
    p_mon.add_argument("--interval", "-i", type=int, default=15, help="Intervalo de polling em segundos.")
    p_mon.set_defaults(func=cmd_monitor)

    # 4. amb advisor
    p_adv = subparsers.add_parser("advisor", help="Menu cognitivo para tirar dúvidas pendentes do Jules.")
    p_adv.add_argument("--auto-approve", "-y", action="store_true", help="Responde todas as sessões pendentes em lote.")
    p_adv.set_defaults(func=cmd_advisor)

    # 5. amb agent
    p_agent = subparsers.add_parser("agent", aliases=["persona"], help="Executor de personas autônomas de manutenção.")
    p_agent.add_argument("--role", "-r", help="Nome da persona (ex: deadwood, beacon, bolt, align, etc.).")
    p_agent.add_argument("--all", "-a", action="store_true", help="Executa todas as personas em lote.")
    p_agent.add_argument("--task", "-t", help="Instruções ou escopo adicional.")
    p_agent.add_argument("--list", "-l", action="store_true", help="Lista todas as personas disponíveis.")
    p_agent.add_argument("--dispatch-jules", "-j", action="store_true", help="Despacha para o Google Jules na nuvem.")
    p_agent.add_argument("--personas-dir", help="Pasta customizada de personas.")
    p_agent.set_defaults(func=cmd_agent)

    # 6. amb jules
    p_jules = subparsers.add_parser("jules", help="Comandos de integração com o Google Jules.")
    j_subs = p_jules.add_subparsers(dest="jules_cmd", help="Subcomandos do Jules")
    
    j_list = j_subs.add_parser("list", help="Lista sessões recentes.")
    j_list.add_argument("--limit", "-n", type=int, default=10, help="Limite de sessões.")

    j_get = j_subs.add_parser("get", help="Exibe detalhes e PR de uma sessão.")
    j_get.add_argument("session_id", help="ID da sessão.")
    j_get.add_argument("--json", action="store_true", help="Saída em JSON puro.")

    j_create = j_subs.add_parser("create", help="Cria uma nova sessão no Jules.")
    j_create.add_argument("--prompt", "-p", required=True, help="Prompt da tarefa.")
    j_create.add_argument("--title", "-t", help="Título da sessão.")

    j_reply = j_subs.add_parser("reply", help="Responde uma dúvida pendente com histórico integral.")
    j_reply.add_argument("--session-id", "-s", required=True, help="ID da sessão.")
    j_reply.add_argument("--auto-approve", "-y", action="store_true", help="Envia resposta gerada sem confirmação.")

    j_app = j_subs.add_parser("approve", help="Aprova o plano de uma sessão.")
    j_app.add_argument("--session-id", "-s", required=True, help="ID da sessão.")
    p_jules.set_defaults(func=cmd_jules)

    # 7. amb stitch
    p_stitch = subparsers.add_parser("stitch", help="Comandos de integração com o Google Stitch SDK.")
    s_subs = p_stitch.add_subparsers(dest="stitch_cmd", help="Subcomandos do Stitch")

    s_gen = s_subs.add_parser("generate", help="Gera uma nova tela via Stitch.")
    s_gen.add_argument("--prompt", "-p", required=True, help="Descrição visual da tela.")
    s_gen.add_argument("--title", "-t", help="Título da tela.")

    s_ref = s_subs.add_parser("refine", help="Refina uma tela existente no Stitch com novas instruções.")
    s_ref.add_argument("--screen-id", "-s", required=True, help="ID da tela.")
    s_ref.add_argument("--prompt", "-p", required=True, help="Instruções de edição e refinamento visual.")

    s_get = s_subs.add_parser("get", help="Obtém o código HTML/CSS de uma tela.")
    s_get.add_argument("--screen-id", "-s", required=True, help="ID da tela.")
    p_stitch.set_defaults(func=cmd_stitch)

    # 8. amb render
    p_render = subparsers.add_parser("render", help="Comandos de integração com o Render Cloud.")
    r_subs = p_render.add_subparsers(dest="render_cmd", help="Subcomandos do Render")
    r_subs.add_parser("status", help="Status do deploy.")
    r_subs.add_parser("logs", help="Últimos logs.")
    r_subs.add_parser("deploy", help="Dispara um novo deploy.")
    p_render.set_defaults(func=cmd_render)

    # 9. amb pipeline
    p_pipe = subparsers.add_parser("pipeline", help="Executa o pipeline orquestrado Design-to-Deploy.")
    p_pipe.add_argument("template", help="Caminho do arquivo markdown de especificação da tarefa.")
    p_pipe.set_defaults(func=cmd_pipeline)

    # 10. amb schema (alias: amb db)
    p_schema = subparsers.add_parser("schema", aliases=["db"], help="Inspeciona tabelas e colunas de schemas do banco de dados (Read-Only).")
    p_schema.add_argument("target", nargs="?", default=None, help="Nome da tabela ou módulo a filtrar (ex: kanban, agenda, projects).")
    p_schema.set_defaults(func=cmd_schema)

    # 11. amb context (alias: amb ctx)
    p_ctx = subparsers.add_parser("context", aliases=["ctx", "ai-context"], help="Gera o roteiro de leitura de arquivos por camadas para a IA.")
    p_ctx.add_argument("module", nargs="?", default="agenda", help="Nome do módulo ou pasta para rastrear (ex: agenda, kanban, projects).")
    p_ctx.add_argument("--json", action="store_true", help="Retorna o resultado em JSON estruturado.")
    p_ctx.set_defaults(func=cmd_context)

    args = parser.parse_args()

    if not args.command:
        banner()
        parser.print_help()
        sys.exit(0)

    try:
        args.func(args)
    except AmbError as ae:
        log_error("AMB", str(ae), getattr(ae, "hint", None))
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n👋 Operação cancelada pelo usuário.")
        sys.exit(0)
    except Exception as e:
        log_error("AMB", f"Erro inesperado: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
