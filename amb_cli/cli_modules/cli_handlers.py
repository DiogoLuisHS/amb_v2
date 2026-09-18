import os
import sys
import json
from typing import Any
from config.bootstrap import ensure_amb_env
from config import Colors, log, log_error

ensure_amb_env()

# -------------------------------------------------------------
# 1. SETUP & CHECK
# -------------------------------------------------------------
def cmd_setup(args: Any) -> None:
    """Executa o assistente de setup no repositório atual."""
    from config.setup_project import run_setup, print_setup_prompt
    if getattr(args, "prompt", False):
        print_setup_prompt()
    else:
        run_setup(
            interactive=not args.auto,
            target_dir=getattr(args, "path", None),
            force=getattr(args, "force", False),
            dry_run=getattr(args, "dry_run", False)
        )


def cmd_prompt(args: Any) -> None:
    """Exibe o Prompt Mestre ou sintetiza um prompt com IA a partir de uma ideia informal."""
    if getattr(args, "synthesize", None):
        from cli_modules.handlers_core.antigravity_handler import handle_cmd_antigravity
        args.agy_cmd = "prompt"
        args.idea = args.synthesize
        handle_cmd_antigravity(args)
    else:
        from config.setup_project import print_setup_prompt
        print_setup_prompt()


def cmd_check(args: Any) -> None:
    """Verifica e valida as chaves de API e configurações do projeto ativo."""
    import config as cfg
    cfg.main(as_json=getattr(args, "json", False))


# -------------------------------------------------------------
# 2. MONITOR & ADVISOR & DASHBOARD
# -------------------------------------------------------------
def cmd_monitor(args: Any) -> None:
    """Inicia o sentinela unificado em tempo real (ou menu interativo se --interactive)."""
    if getattr(args, "interactive", False):
        from agents.auto_reply import run_auto_advisor
        run_auto_advisor(auto_approve=args.auto_approve)
        return

    from agents.monitor import UnifiedMonitor
    monitor = UnifiedMonitor(interval=args.interval, auto_approve=args.auto_approve)
    monitor.run(check_once=args.check_once)


def cmd_advisor(args: Any) -> None:
    """Menu cognitivo para tirar dúvidas pendentes do Jules com IA (atalho para amb jules reply)."""
    from cli_modules.handlers_core.jules_handler import handle_cmd_jules
    args.jules_cmd = "reply"
    handle_cmd_jules(args)


def cmd_gui(args: Any) -> None:
    """Inicia o Assistente Gráfico (Tkinter UI)."""
    from gui.wizard_app import start_wizard
    start_wizard()


def cmd_config(args: Any) -> None:
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
# 3. AGENT (Jules Agent Local Runner)
# -------------------------------------------------------------
def cmd_agent(args: Any) -> None:
    """Executa personas dinâmicas localmente, em loop contínuo ou na nuvem."""
    if getattr(args, "loop", False) or getattr(args, "prompt", None):
        from agents.autonomous_loop import run_autonomous_loop
        prompt_file = getattr(args, "prompt", None) or (args.task if (getattr(args, "task", None) and os.path.exists(args.task)) else None)
        max_c = getattr(args, "max_cycles", None)
        if max_c is None and getattr(args, "prompt", None) and not getattr(args, "loop", False):
            max_c = 1
        raw_modules = getattr(args, "modules", None)
        mod_list = [m.strip() for m in raw_modules.split(",")] if raw_modules else None
        run_autonomous_loop(
            role=args.role,
            all_personas=getattr(args, "all", False),
            prompt_file=prompt_file,
            modules=mod_list,
            max_cycles=max_c,
            branch=getattr(args, "branch", None),
            no_auto_merge=getattr(args, "no_auto_merge", False)
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
# 4. JULES (Gerenciamento de Sessões e Tarefas)
# -------------------------------------------------------------
def cmd_jules(args: Any) -> None:
    """Roteia comandos da integração com a Jules API."""
    from cli_modules.handlers_core.jules_handler import handle_cmd_jules
    handle_cmd_jules(args)


# -------------------------------------------------------------
# 5. GOOGLE STITCH
# -------------------------------------------------------------
def cmd_stitch(args: Any) -> None:
    """Roteia comandos da integração com o Google Stitch SDK."""
    from cli_modules.handlers_core.stitch_handler import handle_cmd_stitch
    handle_cmd_stitch(args)


# -------------------------------------------------------------
# 6. ANTIGRAVITY, VALIDATE, PIPELINE, SCHEMA & CONTEXT
# -------------------------------------------------------------
def cmd_antigravity(args: Any) -> None:
    """Comandos cognitivos e operacionais do Google Antigravity / agy."""
    from cli_modules.handlers_core.antigravity_handler import handle_cmd_antigravity
    handle_cmd_antigravity(args)


def cmd_validate(args: Any) -> None:
    """Audita um arquivo de código contra as regras arquiteturais do repositório (atalho para amb agy validate)."""
    from cli_modules.handlers_core.antigravity_handler import handle_cmd_antigravity
    args.agy_cmd = "validate"
    handle_cmd_antigravity(args)


def cmd_pipeline(args: Any) -> None:
    """Executa o pipeline completo Design-to-Deploy."""
    from pipeline.pipeline import PipelineOrchestrator
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


def cmd_schema(args: Any) -> None:
    """Exibe o catálogo de schemas e tabelas do banco de dados (Read-Only)."""
    from architecture.db_schema_reader import show_schema
    show_schema(filter_term=args.target)


def cmd_context(args: Any) -> None:
    """Gera o roteiro de arquivos ordenados por camadas de dependência para a IA."""
    from architecture.ai_context_builder import generate_context
    generate_context(target=args.module, output_json=args.json)


def cmd_git(args: Any) -> None:
    """Gerencia comandos locais do Git e ciclo de vida de Pull Requests."""
    from cli_modules.handlers_core.git_handler import handle_cmd_git
    handle_cmd_git(args)
