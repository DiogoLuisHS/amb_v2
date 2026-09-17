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
        run_setup(
            interactive=not args.auto,
            target_dir=getattr(args, "path", None),
            force=getattr(args, "force", False),
            dry_run=getattr(args, "dry_run", False)
        )


def cmd_prompt(args):
    """Exibe o Prompt Mestre ou sintetiza um prompt com IA a partir de uma ideia informal."""
    if getattr(args, "synthesize", None):
        from integrations.antigravity.tools.synthesize_prompt import run_synthesize_prompt
        prompt_res = run_synthesize_prompt(
            raw_idea=args.synthesize,
            role=getattr(args, "role", "general") or "general"
        )
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
    cfg.main(as_json=getattr(args, "json", False))


# -------------------------------------------------------------
# 2. MONITOR & ADVISOR & DASHBOARD
# -------------------------------------------------------------
def cmd_monitor(args):
    """Inicia o sentinela unificado em tempo real (ou menu interativo se --interactive)."""
    if getattr(args, "interactive", False):
        from auto_reply import run_auto_advisor
        run_auto_advisor(auto_approve=args.auto_approve)
        return

    from agents.monitor import UnifiedMonitor
    monitor = UnifiedMonitor(interval=args.interval, auto_approve=args.auto_approve)
    monitor.run(check_once=args.check_once)


def cmd_advisor(args):
    """Menu cognitivo para tirar dúvidas pendentes do Jules com IA."""
    sid = getattr(args, "session_id_flag", None) or getattr(args, "session_id", None)
    if sid:
        sid = str(sid).strip().rstrip("/").split("/")[-1]
        msg = getattr(args, "message", None)
        if msg:
            from jules_client import JulesClient
            client = JulesClient()
            client.send_message(session_id=sid, message=msg)
            from config import Colors, log
            log("JULES", f"✅ Mensagem direta enviada para a sessão {sid}!", Colors.GREEN)
        else:
            from auto_reply import advise_and_reply
            advise_and_reply(session_id=sid, auto_approve=args.auto_approve)
    else:
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
    if getattr(args, "loop", False) or getattr(args, "prompt", None):
        from agents.autonomous_loop import run_autonomous_loop
        prompt_file = getattr(args, "prompt", None) or (args.task if (getattr(args, "task", None) and os.path.exists(args.task)) else None)
        max_c = getattr(args, "max_cycles", None)
        if max_c is None and getattr(args, "prompt", None) and not getattr(args, "loop", False):
            max_c = 1
        run_autonomous_loop(
            role=args.role,
            all_personas=getattr(args, "all", False),
            prompt_file=prompt_file,
            max_cycles=max_c,
            branch=getattr(args, "branch", None)
        )
        return

    from agents import local_agent_runner as runner
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

    if sub in ["status", "check"]:
        from integrations.jules.jules_client import JulesClient
        client = JulesClient()
        res = client.get_status(repo_filter=getattr(args, "repo", None))
        if getattr(args, "json", False):
            print(json.dumps(res, indent=2, ensure_ascii=False))
        else:
            print(f"\n{Colors.BOLD}{Colors.CYAN}=== ☁️ DIAGNÓSTICO GOOGLE JULES ==={Colors.RESET}\n")
            key_st = f"{Colors.GREEN}Configurada{Colors.RESET}" if res["api_key_configured"] else f"{Colors.RED}Ausente{Colors.RESET}"
            print(f"  • API Key:           {key_st}")
            reach_st = f"{Colors.GREEN}Conectada{Colors.RESET}" if res["api_reachable"] else f"{Colors.RED}Inacessível ({res.get('error')}){Colors.RESET}"
            print(f"  • API REST:          {reach_st}")
            print(f"  • Fontes na Conta:   {Colors.BOLD}{res['sources_count']}{Colors.RESET}")
            print(f"  • Repositório Alvo:  {Colors.BOLD}{res['active_repo'] or 'Não detectado'}{Colors.RESET}")
            repo_st = f"{Colors.GREEN}Sim{Colors.RESET}" if res["repo_connected"] else f"{Colors.YELLOW}Não encontrado nas fontes conectadas{Colors.RESET}"
            print(f"  • Repo Conectado:    {repo_st}")
            print(f"\n  • Sessões do Repo:   Total: {Colors.BOLD}{res['sessions_total']}{Colors.RESET} | Aguardando: {Colors.YELLOW}{res['sessions_awaiting_feedback']}{Colors.RESET} | Em Progresso: {Colors.CYAN}{res['sessions_in_progress']}{Colors.RESET} | Concluídas: {Colors.GREEN}{res['sessions_completed']}{Colors.RESET} | Falhas: {Colors.RED}{res['sessions_failed']}{Colors.RESET}\n")

    elif sub in ["sources", "source"]:
        from integrations.jules.tools.list_sources import run_list_sources
        run_list_sources(as_json=getattr(args, "json", False))

    elif sub == "list":
        from integrations.jules.tools.list_sessions import run_list_sessions
        run_list_sessions(
            limit=getattr(args, "limit", 10),
            repo=getattr(args, "repo", None),
            all_repos=getattr(args, "all", False),
            state=getattr(args, "state", None),
            as_json=getattr(args, "json", False)
        )

    elif sub == "get":
        sid = getattr(args, "session_id", None) or getattr(args, "session_id_flag", None)
        if not sid:
            log_error("JULES", "Informe o ID da sessão.")
            return
        from integrations.jules.tools.get_session import run_get_session
        run_get_session(
            session_id=sid,
            watch=getattr(args, "watch", False),
            as_json=getattr(args, "json", False)
        )

    elif sub == "create":
        from integrations.jules.tools.create_session import run_create_session
        run_create_session(
            prompt=args.prompt,
            title=getattr(args, "title", None),
            base_branch=getattr(args, "branch", None),
            source_name=getattr(args, "source", None),
            as_json=getattr(args, "json", False)
        )

    elif sub in ["reply", "advisor", "ask"]:
        sid = getattr(args, "session_id_flag", None) or getattr(args, "session_id", None)
        if sid:
            from integrations.jules.jules_client import JulesClient
            sid = JulesClient.normalize_session_id(sid)

        if getattr(args, "message", None):
            if not sid:
                log_error("JULES", "Informe o ID da sessão ao usar --message direta.")
                return
            from integrations.jules.tools.send_message import run_send_message
            run_send_message(
                session_id=sid,
                message=args.message,
                force=getattr(args, "force", False)
            )
        elif sid:
            from auto_reply import advise_and_reply
            advise_and_reply(session_id=sid, auto_approve=getattr(args, "auto_approve", False))
        else:
            from auto_reply import run_auto_advisor
            run_auto_advisor(auto_approve=getattr(args, "auto_approve", False))

    elif sub == "approve":
        sid = getattr(args, "session_id", None) or getattr(args, "session_id_flag", None)
        if not sid:
            log_error("JULES", "Informe o ID da sessão para aprovação.")
            return
        from integrations.jules.tools.approve_plan import run_approve_plan
        run_approve_plan(
            session_id=sid,
            force=getattr(args, "force", False),
            as_json=getattr(args, "json", False)
        )

    elif sub == "merge":
        sid = getattr(args, "session_id", None) or getattr(args, "session_id_flag", None)
        from integrations.jules.tools.merge_session_pr import run_merge_session_pr
        run_merge_session_pr(
            session_id=sid,
            auto_latest=getattr(args, "auto_latest", False),
            target_branch=getattr(args, "branch", "main")
        )

    elif sub in ["clean", "cleanup"]:
        from integrations.jules.tools.cleanup_sessions import run_cleanup_sessions
        delete_mode = "failed" if getattr(args, "failed", False) else ("merged" if getattr(args, "merged", False) else "merged")
        delete_id = getattr(args, "id", None)
        run_cleanup_sessions(
            delete_mode=delete_mode,
            delete_id=delete_id,
            dry_run=not getattr(args, "force", False)
        )

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

    def _resolve_prompt(p: str) -> str:
        if p and os.path.exists(p) and os.path.isfile(p):
            with open(p, "r", encoding="utf-8", errors="replace") as f:
                return f.read().strip()
        return p

    as_json = getattr(args, "json", False)

    if sub == "list":
        screens = client.list_screens(project_id=getattr(args, "project_id", None))
        if as_json:
            print(json.dumps(screens, indent=2, ensure_ascii=False))
            return
        print(f"\n{Colors.BOLD}{Colors.CYAN}=== TELAS DO PROJETO STITCH ({len(screens)} encontrada(s)) ==={Colors.RESET}\n")
        if not screens:
            print("  Nenhuma tela encontrada no projeto ativo.")
            return
        for s in screens:
            sid = s.get("id") or s.get("screenId") or (s.get("name", "").split("/")[-1])
            title = s.get("title") or s.get("label") or "Sem título"
            dims = f" ({s.get('width')}x{s.get('height')})" if s.get("width") and s.get("height") else ""
            desc = f" - {s.get('description')}" if s.get("description") else ""
            print(f"  • {Colors.GREEN}{sid:<14}{Colors.RESET} {Colors.BOLD}{title}{Colors.RESET}{dims}{desc}")
        print()

    elif sub == "generate":
        prompt_text = _resolve_prompt(args.prompt)
        device = getattr(args, "device", None)
        output_file = getattr(args, "output", None)
        res = client.generate_screen(prompt=prompt_text, device_type=device, output_file=output_file)
        if as_json:
            print(json.dumps(res, indent=2, ensure_ascii=False))
            return
        sid = res.get("screenId") or "N/A"
        log("STITCH", f"Tela gerada com sucesso! ID: {sid}", Colors.GREEN)
        if res.get("screenshotUrl"):
            print(f"  • Screenshot: {res['screenshotUrl']}")
        if output_file:
            print(f"  • HTML salvo em: {output_file}")

    elif sub == "refine":
        prompt_text = _resolve_prompt(args.prompt)
        output_file = getattr(args, "output", None)
        device = getattr(args, "device", None)
        res = client.edit_screen(screen_id=args.screen_id, prompt=prompt_text, device_type=device, output_file=output_file)
        if as_json:
            print(json.dumps(res, indent=2, ensure_ascii=False))
            return
        log("STITCH", f"Tela {args.screen_id} refinada com sucesso!", Colors.GREEN)
        if res.get("screenshotUrl"):
            print(f"  • Nova Screenshot: {res['screenshotUrl']}")
        if output_file:
            print(f"  • HTML salvo em: {output_file}")

    elif sub == "get":
        output_file = getattr(args, "output", None)
        res = client.get_screen(screen_id=args.screen_id, output_file=output_file)
        if as_json:
            print(json.dumps(res, indent=2, ensure_ascii=False))
            return
        log("STITCH", f"Detalhes da tela {args.screen_id} obtidos com sucesso.", Colors.GREEN)
        if res.get("title"):
            print(f"  • Título: {res['title']}")
        if res.get("screenshotUrl"):
            print(f"  • Screenshot: {res['screenshotUrl']}")
        if res.get("htmlCode"):
            print(f"  • DOM HTML: {len(res['htmlCode'])} caracteres")
        if output_file:
            print(f"  • HTML salvo em: {output_file}")

    elif sub == "variants":
        device = getattr(args, "device", None)
        res = client.generate_variants(screen_id=args.screen_id, prompt=args.prompt, variant_count=args.count, device_type=device)
        if as_json:
            print(json.dumps(res, indent=2, ensure_ascii=False))
            return
        log("STITCH", f"Variantes geradas com sucesso! ID: {res.get('screenId')}", Colors.GREEN)
        if res.get("screenshotUrl"):
            print(f"  • Screenshot: {res['screenshotUrl']}")

    elif sub == "download":
        out_dir = getattr(args, "output", "./stitch_assets")
        pid = getattr(args, "project_id", None)
        res = client.download_assets(output_dir=out_dir, project_id=pid)
        if as_json:
            print(json.dumps(res, indent=2, ensure_ascii=False))
            return
        log("STITCH", f"Assets baixados com sucesso para: {out_dir}", Colors.GREEN)

    elif sub == "project":
        pid = getattr(args, "project_id", None)
        res = client.get_project(project_id=pid)
        if as_json:
            print(json.dumps(res, indent=2, ensure_ascii=False))
            return
        print(f"\n{Colors.BOLD}{Colors.CYAN}=== PROJETO STITCH ==={Colors.RESET}\n")
        print(json.dumps(res, indent=2, ensure_ascii=False))

    elif sub == "sync":
        res = client.sync_design_system(design_md_path=getattr(args, "file", None))
        if as_json:
            print(json.dumps(res, indent=2, ensure_ascii=False))
            return
        log("STITCH", "✅ Design System sincronizado com sucesso!", Colors.GREEN)

    elif sub == "call":
        payload_str = getattr(args, "payload", "{}")
        if os.path.exists(payload_str) and os.path.isfile(payload_str):
            with open(payload_str, "r", encoding="utf-8", errors="replace") as pf:
                payload = json.load(pf)
        else:
            payload = json.loads(payload_str)
        res = client.call_tool(args.tool, payload)
        print(json.dumps(res, indent=2, ensure_ascii=False))

    else:
        print("Subcomando do Stitch inválido. Use 'amb stitch --help'.")


# -------------------------------------------------------------
# 6. ANTIGRAVITY, VALIDATE, PIPELINE, SCHEMA & CONTEXT
# -------------------------------------------------------------
def cmd_antigravity(args):
    """Comandos cognitivos e operacionais do Google Antigravity / agy."""
    sub = getattr(args, "agy_cmd", None)
    from integrations.antigravity.antigravity_client import AntigravityClient
    from config import RulesManager, get_rules_manager

    if sub in ["status", "check", None]:
        client = AntigravityClient()
        status_data = client.get_status()
        if getattr(args, "json", False):
            print(json.dumps(status_data, indent=2, ensure_ascii=False))
            return
        print(f"\n{Colors.BOLD}{Colors.CYAN}=== 🧠 DIAGNÓSTICO GOOGLE ANTIGRAVITY ==={Colors.RESET}\n")
        status_color = Colors.GREEN if status_data["status"] == "OK" else Colors.YELLOW
        print(f"  • Status Geral: {status_color}{status_data['status']}{Colors.RESET}")
        print(f"  • Modelo Ativo: {Colors.BOLD}{status_data['model']}{Colors.RESET}")
        api_st = f"{Colors.GREEN}Configurada{Colors.RESET}" if status_data["gemini_api_key_configured"] else f"{Colors.RED}Não configurada{Colors.RESET}"
        print(f"  • GEMINI_API_KEY: {api_st}")
        agy_st = f"{Colors.GREEN}Instalada ({status_data['agy_cli_path']}){Colors.RESET}" if status_data["agy_cli_installed"] else f"{Colors.YELLOW}Não encontrada (usando REST API){Colors.RESET}"
        print(f"  • CLI agy: {agy_st}")
        rules_dir_str = status_data["rules_directory"] or "Nenhum diretório de regras encontrado"
        print(f"  • Diretório de Regras: {Colors.DIM}{rules_dir_str}{Colors.RESET} ({status_data['rules_count']} regras)")
        if status_data["rules"]:
            print(f"    Regras ativas: {', '.join(status_data['rules'])}")
        print()

    elif sub in ["prompt", "synthesize", "synth"]:
        from integrations.antigravity.tools.synthesize_prompt import run_synthesize_prompt
        idea = getattr(args, "idea", "")
        role = getattr(args, "role", "general") or "general"
        output_file = getattr(args, "output", None)
        log("ANTIGRAVITY", f"Sintetizando prompt executivo ({role})...", Colors.CYAN)
        res = run_synthesize_prompt(raw_idea=idea, role=role, output_file=output_file)
        if not output_file:
            print("\n" + "=" * 75)
            print(f"{Colors.BOLD}🧠 PROMPT ESTRUTURADO GERADO COM IA:{Colors.RESET}")
            print("=" * 75)
            print(res)
            print("=" * 75 + "\n")

    elif sub in ["validate", "audit", "lint"]:
        from integrations.antigravity.tools.validate_architecture import run_validate_architecture
        target_file = getattr(args, "file", "")
        log("ANTIGRAVITY", f"Auditando conformidade arquitetural de {target_file}...", Colors.CYAN)
        res = run_validate_architecture(file_path=target_file)
        if getattr(args, "json", False):
            print(json.dumps({"file": target_file, "report": res}, indent=2, ensure_ascii=False))
            return
        print("\n" + "=" * 75)
        print(f"{Colors.BOLD}RELATÓRIO DE AUDITORIA ARQUITETURAL:{Colors.RESET}")
        print("=" * 75)
        print(res)
        print("=" * 75 + "\n")

    elif sub == "rules":
        mgr = get_rules_manager()
        rules_dir = mgr.resolve_rules_dir()
        rules_list = mgr.list_rules(rules_dir=rules_dir)
        as_json = getattr(args, "json", False)
        show_content = getattr(args, "content", False)

        if as_json:
            out = {
                "rules_directory": rules_dir,
                "rules": rules_list
            }
            if show_content:
                out["consolidated_content"] = mgr.load_rules(rules_dir=rules_dir)
            print(json.dumps(out, indent=2, ensure_ascii=False))
            return

        print(f"\n{Colors.BOLD}{Colors.CYAN}=== 📋 REGRAS ARQUITETURAIS DO REPOSITÓRIO ==={Colors.RESET}\n")
        print(f"Diretório: {Colors.DIM}{rules_dir or 'Nenhum'}{Colors.RESET} ({len(rules_list)} arquivo(s))\n")
        for r in rules_list:
            print(f"  • {Colors.BOLD}{r['name']:<25}{Colors.RESET} ({r['size_bytes']} bytes)")
            if r["summary"]:
                print(f"    {Colors.DIM}{r['summary']}{Colors.RESET}")
        print()
        if show_content:
            content = mgr.load_rules(rules_dir=rules_dir)
            print("=" * 75)
            print(f"{Colors.BOLD}CONTEÚDO CONSOLIDADO DAS REGRAS:{Colors.RESET}")
            print("=" * 75)
            print(content)
            print("=" * 75 + "\n")

    elif sub in ["run", "eval"]:
        prompt_text = getattr(args, "prompt", "")
        system_text = getattr(args, "system", None)
        model_override = getattr(args, "model", None)
        temp = getattr(args, "temperature", 0.2)
        client = AntigravityClient(model=model_override)
        log("ANTIGRAVITY", f"Executando inferência com {client.model}...", Colors.CYAN)
        res = client.generate_text(
            prompt=prompt_text,
            system_instruction=system_text,
            temperature=temp
        )
        out_f = getattr(args, "output", None)
        if out_f:
            with open(out_f, "w", encoding="utf-8") as f:
                f.write(res)
            log("ANTIGRAVITY", f"Resposta salva em {out_f}", Colors.GREEN)
        else:
            print(res)

    else:
        print("Subcomando do Antigravity inválido. Use 'amb agy --help'.")


def cmd_validate(args):
    """Audita um arquivo de código contra as regras arquiteturais do repositório."""
    from integrations.antigravity.tools.validate_architecture import run_validate_architecture
    log("VALIDATE", f"Auditando arquivo {args.file}...", Colors.CYAN)
    res = run_validate_architecture(args.file)
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
        device_type=getattr(args, "device", None) or getattr(args, "device_type", None),
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


def cmd_git(args):
    """Gerencia comandos locais do Git e ciclo de vida de Pull Requests."""
    sub = getattr(args, "git_cmd", None)
    from integrations.git.git_service import GitService

    if sub in ["status", None]:
        from integrations.git.tools.git_status import run_git_status
        run_git_status(as_json=getattr(args, "json", False))

    elif sub == "sync":
        from integrations.git.tools.sync_branch import run_sync_branch
        remote = getattr(args, "remote", "origin")
        branch = getattr(args, "branch", None)
        auto_stash = getattr(args, "auto_stash", True)
        run_sync_branch(remote=remote, branch=branch, auto_stash=auto_stash)

    elif sub == "diff":
        git = GitService()
        file_path = getattr(args, "file", None)
        base_branch = getattr(args, "base", None)
        cached = getattr(args, "cached", False)
        diff_text = git.get_diff(file_path=file_path, base_branch=base_branch, cached=cached)
        if diff_text:
            print(diff_text)
        else:
            log("GIT", "Nenhuma alteração detectada no diff.", Colors.CYAN)

    elif sub == "pr":
        from integrations.git.tools.pr_manager import run_pr_manager
        pr_action = getattr(args, "pr_cmd", "list") or "list"
        kwargs = {
            "repo_name": getattr(args, "repo", None),
            "pr_number": getattr(args, "number", None),
            "title": getattr(args, "title", None),
            "body": getattr(args, "body", ""),
            "base": getattr(args, "base", None),
            "head": getattr(args, "head", None),
            "draft": getattr(args, "draft", False),
            "include_drafts": not getattr(args, "no_drafts", False),
            "squash": getattr(args, "squash", True),
            "delete_branch": getattr(args, "delete_branch", True),
            "comment": getattr(args, "comment", None),
        }
        res = run_pr_manager(action=pr_action, **kwargs)
        as_json = getattr(args, "json", False)

        if as_json or isinstance(res, (dict, list)):
            print(json.dumps(res, indent=2, ensure_ascii=False))
        elif res:
            print(res)

    else:
        print("Subcomando do Git inválido. Use 'amb git --help'.")

