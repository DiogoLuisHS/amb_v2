import json
from typing import Any
from core.bootstrap import ensure_amb_env

ensure_amb_env()

def handle_cmd_jules(args: Any) -> None:
    """Roteia comandos específicos da integração com o Google Jules."""
    sub = args.jules_cmd

    from core import Colors, log, log_error

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
            from agents.auto_reply import advise_and_reply
            advise_and_reply(session_id=sid, auto_approve=getattr(args, "auto_approve", False))
        else:
            from agents.auto_reply import run_auto_advisor
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
