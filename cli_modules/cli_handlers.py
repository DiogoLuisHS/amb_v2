import os
import sys
import json
from config import Colors, log, log_error

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


def cmd_gui(args):
    """Inicia o Assistente Gráfico (Tkinter UI)."""
    from gui.wizard_app import start_wizard
    start_wizard()


def cmd_config(args):
    """Gerencia preferências e controles do AMB_V2."""
    from config import set_gemini_confirmation, is_gemini_confirmation_required, Colors
    if getattr(args, "gemini_confirm", None) is not None:
        enable = args.gemini_confirm.lower() in ["on", "true", "1", "yes", "sim", "ativar"]
        set_gemini_confirmation(enable)
        status_msg = f"{Colors.GREEN}ATIVADA (Exige confirmação interativa antes de cada requisição ao Gemini){Colors.RESET}" if enable else f"{Colors.YELLOW}DESATIVADA (Chamadas ao Gemini automáticas){Colors.RESET}"
        print(f"\n🛡️ Autorização prévia do Gemini: {status_msg}\n")
    else:
        status = is_gemini_confirmation_required()
        status_msg = f"{Colors.GREEN}ATIVADA (Exige confirmação manual){Colors.RESET}" if status else f"{Colors.DIM}DESATIVADA (Chamadas automáticas){Colors.RESET}"
        print(f"\n🛡️ Status da Autorização do Gemini: {status_msg}")
        print(f"👉 Para alterar: amb config --gemini-confirm on (ou off)\n")



# -------------------------------------------------------------
# 3. AGENT & PERSONAS
# -------------------------------------------------------------
def cmd_agent(args):
    """Executa personas dinâmicas localmente, em loop contínuo ou na nuvem."""
    if getattr(args, "loop", False):
        from autonomous_loop import run_autonomous_loop
        run_autonomous_loop(
            role=args.role,
            all_personas=getattr(args, "all", False),
            prompt_file=args.task if (args.task and os.path.exists(args.task)) else None,
            max_cycles=getattr(args, "max_cycles", None),
            branch=getattr(args, "branch", None)
        )
        return


    import local_agent_runner as runner
    personas_dir = runner.get_personas_directory(args.personas_dir)
    personas = runner.discover_personas(personas_dir)

    if args.list or (not args.role and not args.all):
        runner.list_personas(personas, personas_dir)
        return

    # Padrão: Despacha para o Google Jules. Só roda local com agy se --agy / --local for especificado.
    dispatch_jules = not getattr(args, "agy", False)

    if args.all:
        for idx, (k, p_data) in enumerate(personas.items(), 1):
            print(f"\n📦 [{idx}/{len(personas)}] Processando Persona: {p_data['title']}")
            runner.execute_single_persona(p_data, task=args.task, dispatch_jules=dispatch_jules)
        return

    clean_role = args.role.lower().replace(".md", "").strip()
    if clean_role not in personas:
        log_error("AGENT", f"Persona '{args.role}' não encontrada em {personas_dir}.", hint=f"Disponíveis: {', '.join(personas.keys())}")
        sys.exit(1)

    runner.execute_single_persona(personas[clean_role], task=args.task, dispatch_jules=dispatch_jules)


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
        res = client.create_session(prompt=args.prompt, title=args.title)
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
        clean_args = ["cleanup_sessions.py"]
        if getattr(args, "failed", False):
            clean_args.append("--delete-failed")
        else:
            clean_args.append("--delete-merged")
            
        if not getattr(args, "force", False):
            clean_args.append("--dry-run")
            
        sys.argv = clean_args
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
    PipelineOrchestrator.run(
        stitch_prompt_file=getattr(args, "stitch_prompt", None),
        jules_prompt_file=getattr(args, "jules_prompt", None),
        auto_approve=getattr(args, "auto_approve", False),
        skip_stitch=getattr(args, "skip_stitch", False),
        no_qa=getattr(args, "no_qa", False),
        resume_session=getattr(args, "resume_session", None),
        device_type=getattr(args, "device", "DESKTOP"),
        edit_screen_id=getattr(args, "edit_screen_id", None),
        screen_id=getattr(args, "screen_id", None),
        sync_ds=getattr(args, "sync_ds", False),
        starting_branch=getattr(args, "branch", None)
    )


def cmd_schema(args):
    """Exibe o catálogo de schemas e tabelas do banco de dados (Read-Only)."""
    from db_schema_reader import show_schema
    show_schema(filter_term=args.target)


def cmd_context(args):
    """Gera o roteiro de arquivos ordenados por camadas de dependência para a IA."""
    from ai_context_builder import generate_context
    generate_context(target=args.module, output_json=args.json)
