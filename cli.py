#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🚀 AMB_V2 - CLI Global e Unificada de Automação de Engenharia
Comando: `amb`
Responsabilidade Única: Ponto de entrada CLI que detecta o repositório onde o terminal
está aberto e roteia todos os subcomandos (setup, monitor, advisor, agent, jules, stitch, render, pipeline, validate, dashboard, schema, context).
"""

import os
import sys
import argparse
import json

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


# -------------------------------------------------------------
# 1. SETUP & CHECK
# -------------------------------------------------------------
def cmd_setup(args):
    """Executa o assistente de setup no repositório atual."""
    from setup_project import run_setup, print_setup_prompt
    if getattr(args, "prompt", False):
        print_setup_prompt()
    else:
        run_setup(interactive=not args.auto)


def cmd_prompt(args):
    """Exibe o Prompt Mestre ou sintetiza um prompt com IA a partir de uma ideia informal."""
    if getattr(args, "synthesize", None):
        from antigravity_client import synthesize_prompt
        prompt_res = synthesize_prompt(raw_idea=args.synthesize, role=getattr(args, "role", "general") or "general")
        print("\n" + "=" * 75)
        print(f"{Colors.BOLD}🧠 PROMPT ESTRUTURADO GERADO COM IA:{Colors.RESET}")
        print("=" * 75)
        print(prompt_res)
        print("=" * 75 + "\n")
    else:
        from setup_project import print_setup_prompt
        print_setup_prompt()


def cmd_check(args):
    """Verifica e valida as chaves de API e configurações do projeto ativo."""
    import config as cfg
    cfg.main()


# -------------------------------------------------------------
# 2. MONITOR & ADVISOR & DASHBOARD
# -------------------------------------------------------------
def cmd_monitor(args):
    """Inicia o sentinela unificado em tempo real (ou menu interativo se --interactive)."""
    if getattr(args, "interactive", False):
        from auto_reply import run_auto_advisor
        run_auto_advisor(auto_approve=args.auto_approve)
        return

    from unified_monitor import UnifiedMonitor
    monitor = UnifiedMonitor(interval=args.interval, auto_approve=args.auto_approve)
    monitor.run(check_once=args.check_once)


def cmd_advisor(args):
    """Menu cognitivo para tirar dúvidas pendentes do Jules com IA."""
    from auto_reply import run_auto_advisor
    run_auto_advisor(auto_approve=args.auto_approve)


def cmd_dashboard(args):
    """Inicia a UI/SPA do Dashboard Web em tempo real."""
    from dashboard_server import start_dashboard
    start_dashboard(port=args.port)


# -------------------------------------------------------------
# 3. AGENT & PERSONAS
# -------------------------------------------------------------
def cmd_agent(args):
    """Executa personas dinâmicas localmente, em loop contínuo ou na nuvem."""
    if getattr(args, "loop", False):
        from autonomous_loop import run_autonomous_loop
        run_autonomous_loop(
            role=args.role or "relay",
            prompt_file=args.task if (args.task and os.path.exists(args.task)) else None,
            max_cycles=getattr(args, "max_cycles", None)
        )
        return

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


# -------------------------------------------------------------
# 4. GOOGLE JULES
# -------------------------------------------------------------
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
        from jules_client import JulesClient
        client = JulesClient()
        data = client.get_session(args.session_id)
        if getattr(args, "json", False):
            print(json.dumps(data, indent=2))
        else:
            sid = data.get("name", "").split("/")[-1] or data.get("id")
            state = data.get("state", "UNKNOWN")
            log("JULES-STATUS", f"Sessão {sid}:", Colors.CYAN)
            print(f"  • Título:     {data.get('title') or 'Sem título'}")
            print(f"  • Estado:     {Colors.BOLD}{state}{Colors.RESET}")
            outputs = data.get("outputs", {})
            pr_url = None
            if isinstance(outputs, list):
                for item in outputs:
                    if isinstance(item, dict) and item.get("pullRequest", {}).get("url"):
                        pr_url = item["pullRequest"]["url"]
            elif isinstance(outputs, dict):
                pr_url = outputs.get("pullRequest", {}).get("url")
            if pr_url:
                print(f"  • Pull Request: {Colors.GREEN}{pr_url}{Colors.RESET}")
            print(f"  • Painel Web:   https://jules.google.com/session/{sid}")

    elif sub == "create":
        from jules_client import JulesClient
        client = JulesClient()
        sources = client.list_sources()
        source_name = sources[0]["name"] if sources else None
        res = client.create_session(prompt=args.prompt, title=args.title, source_name=source_name)
        sid = res.get("name", "").split("/")[-1] or res.get("id")
        log("JULES", f"Sessão criada com sucesso: {sid}", Colors.GREEN)
        print(f"Painel: https://jules.google.com/session/{sid}")

    elif sub in ["reply", "advisor", "ask"]:
        if getattr(args, "message", None):
            from jules_client import JulesClient
            client = JulesClient()
            if not getattr(args, "session_id", None):
                log_error("JULES", "Informe --session-id ao usar --message direta.")
                return
            client.send_message(session_id=args.session_id, message=args.message)
            log("JULES", f"✅ Mensagem direta enviada para a sessão {args.session_id}!", Colors.GREEN)
        elif getattr(args, "session_id", None):
            from auto_reply import advise_and_reply
            advise_and_reply(session_id=args.session_id, auto_approve=args.auto_approve)
        else:
            from auto_reply import run_auto_advisor
            run_auto_advisor(auto_approve=args.auto_approve)

    elif sub == "approve":
        from jules_client import JulesClient
        client = JulesClient()
        client.approve_plan(session_id=args.session_id)
        log("JULES", f"✅ Plano da sessão {args.session_id} aprovado com sucesso!", Colors.GREEN)

    elif sub == "merge":
        from merge_session_pr import main as merge_main
        sys.argv = ["merge_session_pr.py"] + (["--session-id", args.session_id] if getattr(args, "session_id", None) else []) + (["--auto-latest"] if getattr(args, "auto_latest", False) else [])
        merge_main()

    elif sub in ["clean", "cleanup"]:
        from cleanup_sessions import main as clean_main
        sys.argv = ["cleanup_sessions.py"] + (["--force"] if getattr(args, "force", False) else [])
        clean_main()

    else:
        print("Subcomando do Jules inválido. Use 'amb jules --help'.")


# -------------------------------------------------------------
# 5. GOOGLE STITCH
# -------------------------------------------------------------
def cmd_stitch(args):
    """Roteia comandos da integração com o Google Stitch SDK."""
    sub = args.stitch_cmd
    from stitch_client import StitchClient

    client = StitchClient()

    if sub == "generate":
        res = client.generate_screen(prompt=args.prompt)
        sid = res.get("screenId") or "N/A"
        log("STITCH", f"Tela gerada com sucesso! ID: {sid}", Colors.GREEN)
        if res.get("screenshotUrl"):
            print(f"  • Screenshot: {res['screenshotUrl']}")

    elif sub == "refine":
        res = client.edit_screen(screen_id=args.screen_id, prompt=args.prompt)
        log("STITCH", f"Tela {args.screen_id} refinada com sucesso!", Colors.GREEN)
        if res.get("screenshotUrl"):
            print(f"  • Nova Screenshot: {res['screenshotUrl']}")

    elif sub == "get":
        res = client.get_screen(screen_id=args.screen_id)
        log("STITCH", f"Detalhes da tela {args.screen_id} obtidos com sucesso.", Colors.GREEN)

    elif sub == "variants":
        res = client.generate_variants(screen_id=args.screen_id, prompt=args.prompt, variant_count=args.count)
        log("STITCH", f"Variantes geradas com sucesso! ID: {res.get('screenId')}", Colors.GREEN)

    elif sub == "sync":
        res = client.sync_design_system(design_md_path=getattr(args, "file", None))
        log("STITCH", "✅ Design System sincronizado com sucesso!", Colors.GREEN)

    else:
        print("Subcomando do Stitch inválido. Use 'amb stitch --help'.")


# -------------------------------------------------------------
# 6. RENDER CLOUD
# -------------------------------------------------------------
def cmd_render(args):
    """Roteia comandos do Render Cloud."""
    sub = args.render_cmd
    from render_client import RenderClient
    from config import require_env

    client = RenderClient()

    if sub == "status":
        sid = getattr(args, "service_id", None) or require_env("RENDER_SERVICE_ID")
        deploys = client.list_deploys(service_id=sid, limit=1)
        if not deploys:
            print(f"Nenhum deploy encontrado para o serviço {sid}.")
            return
        dep = deploys[0].get("deploy", deploys[0])
        status = dep.get("status", "UNKNOWN")
        status_color = Colors.GREEN if status == "live" else (Colors.RED if "fail" in status.lower() else Colors.YELLOW)
        log("RENDER", f"Status do serviço {sid}: {status_color}{status}{Colors.RESET}", Colors.CYAN)
        print(f"  • Deploy ID:   {dep.get('id')}")
        print(f"  • Commit:      {dep.get('commit', {}).get('message', 'N/A')}")
        print(f"  • Criado em:   {dep.get('createdAt')}")

    elif sub == "logs":
        sid = getattr(args, "service_id", None) or require_env("RENDER_SERVICE_ID")
        deploys = client.list_deploys(service_id=sid, limit=1)
        if deploys:
            dep = deploys[0].get("deploy", deploys[0])
            dep_id = dep.get("id")
            log("RENDER-LOGS", f"Logs do Deploy {dep_id} (Serviço: {sid}):", Colors.CYAN)
            print(f"Painel Live Logs: https://dashboard.render.com/web/{sid}/deploys/{dep_id}")
        else:
            print(f"Nenhum deploy recente encontrado para {sid}.")

    elif sub == "deploy":
        sid = getattr(args, "service_id", None) or require_env("RENDER_SERVICE_ID")
        log("RENDER", f"Disparando deploy para serviço {sid}...", Colors.CYAN)
        res = client.trigger_deploy(service_id=sid)
        dep_id = res.get("id") or res.get("deploy", {}).get("id")
        log("RENDER", f"✅ Deploy disparado com sucesso! ID: {dep_id}", Colors.GREEN)

    elif sub == "services":
        services = client.list_services()
        log("RENDER", f"Serviços encontrados na conta ({len(services)}):", Colors.CYAN)
        for item in services:
            srv = item.get("service", item)
            print(f"  • ID: {Colors.BOLD}{srv.get('id')}{Colors.RESET} | {Colors.GREEN}{srv.get('name')}{Colors.RESET} ({srv.get('type')})")

    else:
        print("Subcomando do Render inválido. Use 'amb render --help'.")


# -------------------------------------------------------------
# 7. VALIDATE, PIPELINE, SCHEMA & CONTEXT
# -------------------------------------------------------------
def cmd_validate(args):
    """Audita um arquivo de código contra as regras arquiteturais do repositório."""
    from validate_architecture import validate_code
    log("VALIDATE", f"Auditando arquivo {args.file}...", Colors.CYAN)
    res = validate_code(args.file)
    print("\n" + "=" * 75)
    print(f"{Colors.BOLD}RELATÓRIO DE AUDITORIA ARQUITETURAL:{Colors.RESET}")
    print("=" * 75)
    print(res)
    print("=" * 75 + "\n")


def cmd_pipeline(args):
    """Executa o pipeline completo Design-to-Deploy."""
    from pipeline import PipelineOrchestrator
    PipelineOrchestrator.run(prompt_file=args.template)


def cmd_schema(args):
    """Exibe o catálogo de schemas e tabelas do banco de dados (Read-Only)."""
    from db_schema_reader import show_schema
    show_schema(filter_term=args.target)


def cmd_context(args):
    """Gera o roteiro de arquivos ordenados por camadas de dependência para a IA."""
    from ai_context_builder import generate_context
    generate_context(target=args.module, output_json=args.json)


# -------------------------------------------------------------
# MAIN CLI PARSER
# -------------------------------------------------------------
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
    p_prompt = subparsers.add_parser("prompt", help="Exibe ou sintetiza com IA o Prompt de Desenvolvimento.")
    p_prompt.add_argument("--synthesize", "-s", help="Ideia informal a ser sintetizada em prompt estruturado com IA.")
    p_prompt.add_argument("--role", "-r", default="general", help="Especialidade para sintetização do prompt.")
    p_prompt.set_defaults(func=cmd_prompt)

    # 2. amb check
    p_check = subparsers.add_parser("check", aliases=["status"], help="Valida chaves e configurações do projeto ativo.")
    p_check.set_defaults(func=cmd_check)

    # 3. amb monitor
    p_mon = subparsers.add_parser("monitor", aliases=["watch", "sentinel"], help="Sentinela em tempo real (Jules + Render) com suporte a auto-resposta Gemini.")
    p_mon.add_argument("--interactive", "-i", action="store_true", help="Abre o menu interativo cognitivo (Advisor) para inspecionar e responder pendências.")
    p_mon.add_argument("--auto-approve", "-y", action="store_true", help="Aprova e responde chats automaticamente via Gemini.")
    p_mon.add_argument("--check-once", "-1", action="store_true", help="Executa apenas uma rodada de checagem e encerra.")
    p_mon.add_argument("--interval", type=int, default=15, help="Intervalo de polling em segundos (padrão: 15s).")
    p_mon.set_defaults(func=cmd_monitor)

    # 4. amb advisor
    p_adv = subparsers.add_parser("advisor", aliases=["ask"], help="Menu cognitivo para tirar dúvidas pendentes do Jules com IA.")
    p_adv.add_argument("--auto-approve", "-y", action="store_true", help="Responde todas as sessões pendentes em lote.")
    p_adv.set_defaults(func=cmd_advisor)

    # 5. amb dashboard (web SPA)
    p_dash = subparsers.add_parser("dashboard", aliases=["web", "ui"], help="Inicia o servidor e SPA do Dashboard Web em tempo real.")
    p_dash.add_argument("--port", "-p", type=int, default=3333, help="Porta HTTP do servidor (padrão: 3333).")
    p_dash.set_defaults(func=cmd_dashboard)

    # 6. amb agent
    p_agent = subparsers.add_parser("agent", aliases=["persona"], help="Executor de personas autônomas de manutenção.")
    p_agent.add_argument("--role", "-r", help="Nome da persona (ex: deadwood, beacon, bolt, align, etc.).")
    p_agent.add_argument("--all", "-a", action="store_true", help="Executa todas as personas em lote.")
    p_agent.add_argument("--task", "-t", help="Instruções ou escopo adicional.")
    p_agent.add_argument("--list", "-l", action="store_true", help="Lista todas as personas disponíveis.")
    p_agent.add_argument("--dispatch-jules", "-j", action="store_true", help="Despacha para o Google Jules na nuvem.")
    p_agent.add_argument("--loop", "-c", "--continuous", action="store_true", help="Executa o ciclo contínuo e autônomo de personas.")
    p_agent.add_argument("--max-cycles", type=int, help="Limite de ciclos no modo loop (se omitido, roda continuamente).")
    p_agent.add_argument("--personas-dir", help="Pasta customizada de personas.")
    p_agent.set_defaults(func=cmd_agent)

    # 7. amb jules
    p_jules = subparsers.add_parser("jules", help="Comandos de integração com o Google Jules.")
    j_subs = p_jules.add_subparsers(dest="jules_cmd", help="Subcomandos do Jules")
    
    j_list = j_subs.add_parser("list", help="Lista sessões recentes.")
    j_list.add_argument("--limit", "-n", type=int, default=10, help="Limite de sessões.")

    j_get = j_subs.add_parser("get", help="Exibe detalhes, PR ou faz streaming ao vivo da sessão.")
    j_get.add_argument("session_id", help="ID da sessão.")
    j_get.add_argument("--watch", "-w", action="store_true", help="Acompanha em tempo real as atividades e saídas da sessão.")
    j_get.add_argument("--json", action="store_true", help="Saída em JSON puro.")

    j_create = j_subs.add_parser("create", help="Cria uma nova sessão no Jules.")
    j_create.add_argument("--prompt", "-p", required=True, help="Prompt da tarefa.")
    j_create.add_argument("--title", "-t", help="Título da sessão.")

    j_reply = j_subs.add_parser("reply", aliases=["advisor", "ask"], help="Responde uma dúvida com IA (ou envia mensagem direta se --message).")
    j_reply.add_argument("--session-id", "-s", required=False, help="ID da sessão (opcional; se omitido, lista todas as sessões pendentes).")
    j_reply.add_argument("--message", "-m", help="Mensagem direta manual a ser enviada ao chat.")
    j_reply.add_argument("--auto-approve", "-y", action="store_true", help="Envia resposta gerada pelo Gemini sem pedir confirmação.")

    j_app = j_subs.add_parser("approve", help="Aprova o plano de uma sessão.")
    j_app.add_argument("--session-id", "-s", required=True, help="ID da sessão.")

    j_merge = j_subs.add_parser("merge", help="Detecta o PR da sessão, aprova, faz merge no GitHub e valida localmente.")
    j_merge.add_argument("--session-id", "-s", help="ID da sessão para detectar o PR.")
    j_merge.add_argument("--auto-latest", action="store_true", help="Detecta automaticamente o PR aberto mais recente.")

    j_clean = j_subs.add_parser("clean", aliases=["cleanup"], help="Audita e remove na nuvem sessões do Jules já integradas.")
    j_clean.add_argument("--force", "-f", action="store_true", help="Remove sem pedir confirmação.")
    p_jules.set_defaults(func=cmd_jules)

    # 8. amb stitch
    p_stitch = subparsers.add_parser("stitch", help="Comandos de integração com o Google Stitch SDK.")
    s_subs = p_stitch.add_subparsers(dest="stitch_cmd", help="Subcomandos do Stitch")

    s_gen = s_subs.add_parser("generate", help="Gera uma nova tela via Stitch.")
    s_gen.add_argument("--prompt", "-p", required=True, help="Descrição visual da tela.")
    s_gen.add_argument("--title", "-t", help="Título da tela.")

    s_ref = s_subs.add_parser("refine", help="Refina uma tela existente no Stitch com novas instruções.")
    s_ref.add_argument("--screen-id", "-s", required=True, help="ID da tela.")
    s_ref.add_argument("--prompt", "-p", required=True, help="Instruções de edição e refinamento visual.")

    s_get = s_subs.add_parser("get", help="Obtém o código HTML/CSS e assets de uma tela.")
    s_get.add_argument("--screen-id", "-s", required=True, help="ID da tela.")

    s_vars = s_subs.add_parser("variants", help="Gera variantes visuais exploratórias de uma tela.")
    s_vars.add_argument("--screen-id", "-s", required=True, help="ID da tela base.")
    s_vars.add_argument("--prompt", "-p", required=True, help="Instruções de variação.")
    s_vars.add_argument("--count", "-c", type=int, default=3, help="Número de variantes (padrão: 3).")

    s_sync = s_subs.add_parser("sync", help="Sincroniza design tokens do design.md com o Design System do Stitch.")
    s_sync.add_argument("--file", "-f", help="Caminho do arquivo design.md.")
    p_stitch.set_defaults(func=cmd_stitch)

    # 9. amb render
    p_render = subparsers.add_parser("render", help="Comandos de integração com o Render Cloud.")
    r_subs = p_render.add_subparsers(dest="render_cmd", help="Subcomandos do Render")
    r_subs.add_parser("status", help="Status do deploy mais recente.")
    r_subs.add_parser("logs", help="Últimos logs de build/execução.")
    r_subs.add_parser("deploy", help="Dispara um novo deploy.")
    r_subs.add_parser("services", help="Lista todos os serviços configurados na conta Render.")
    p_render.set_defaults(func=cmd_render)

    # 10. amb validate
    p_val = subparsers.add_parser("validate", aliases=["lint", "audit"], help="Audita um arquivo contra as regras arquiteturais do repositório.")
    p_val.add_argument("file", help="Caminho do arquivo de código a ser auditado.")
    p_val.set_defaults(func=cmd_validate)

    # 11. amb pipeline
    p_pipe = subparsers.add_parser("pipeline", help="Executa o pipeline orquestrado Design-to-Deploy.")
    p_pipe.add_argument("template", help="Caminho do arquivo markdown de especificação da tarefa.")
    p_pipe.set_defaults(func=cmd_pipeline)

    # 12. amb schema (alias: amb db)
    p_schema = subparsers.add_parser("schema", aliases=["db"], help="Inspeciona tabelas e colunas de schemas do banco de dados (Read-Only).")
    p_schema.add_argument("target", nargs="?", default=None, help="Nome da tabela ou módulo a filtrar (ex: kanban, agenda, projects).")
    p_schema.set_defaults(func=cmd_schema)

    # 13. amb context (alias: amb ctx)
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
