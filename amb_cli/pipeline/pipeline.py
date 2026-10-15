#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
================================================================================
🚀 AMB_V2 - PIPELINE AUTÔNOMO DESIGN-TO-CODE (ORQUESTRADOR UNIFICADO)
================================================================================
"""
import os
import sys
import argparse
from typing import Optional
from pathlib import Path

from core.bootstrap import ensure_amb_env
ensure_amb_env()

from core.console_presenter import ConsolePresenter
from core.local_telemetry import LocalTelemetry
import time
from core import Colors, log, log_error, AmbError
from workspace import find_repo_root, get_repo_name
from agents.loop_core.loop_state_machine import LoopStateMachine, LoopState
from integrations.jules.jules_client import JulesClient
from integrations.git.git_service import GitService
from integrations.antigravity.antigravity_client import AntigravityClient
from workspace import get_rules_manager

from pipeline.quality_gatekeeper import QualityGatekeeper
from amb_cli.pipeline.pipeline_core.prompt_builder import parse_single_prompt, clean_html_for_summary, synthesize_stitch_ui, build_executive_prompt
from amb_cli.pipeline.pipeline_core.design_stage import process_design_stage

class PipelineOrchestrator:
    """Orquestrador do Pipeline AMB_V2."""

    @classmethod
    def run(
        cls, prompt_file: str = None, stitch_prompt_file: str = None, jules_prompt_file: str = None,
        auto_approve: bool = False, skip_stitch: bool = False, no_qa: bool = False,
        resume_session: str = None, device_type: str = None, edit_screen_id: str = None,
        screen_id: str = None, sync_ds: bool = False, starting_branch: str = None,
        auto_merge: bool = False, no_auto_merge: bool = False, resume: bool = False,
        dry_run: bool = False, json_mode: bool = False
    ):
        if auto_approve and not no_auto_merge:
            auto_merge = True

        cls._current_run_start_time = time.time()
        repo_root = find_repo_root()
        repo_name = get_repo_name()

        machine = LoopStateMachine(repo_root=repo_root)

        starting_branch = starting_branch or GitService(repo_root=repo_root).get_current_branch(cwd=repo_root) or "main"

        if resume:
            resume_session = resume_session or machine.get_current_state().get("session_id")

        if resume_session:
            log("PIPELINE", f"Retomando monitoramento: {resume_session}", Colors.HEADER)
            cls._monitor_jules_session(resume_session, repo_root, no_qa, auto_merge, starting_branch)
            return

        log("ETAPA 1/6", f"📄 Lendo arquivos de prompt...", Colors.HEADER)
        stitch_prompt, jules_prompt, file_label = "", "", ""

        if stitch_prompt_file and os.path.exists(stitch_prompt_file):
            with open(stitch_prompt_file, "r", encoding="utf-8", errors="replace") as f:
                stitch_prompt = f.read().strip()
            file_label += os.path.basename(stitch_prompt_file) + " "

        if jules_prompt_file and os.path.exists(jules_prompt_file):
            with open(jules_prompt_file, "r", encoding="utf-8", errors="replace") as f:
                jules_prompt = f.read().strip()
            file_label += os.path.basename(jules_prompt_file)

        if prompt_file and os.path.exists(prompt_file):
            file_label = file_label or os.path.basename(prompt_file)
            with open(prompt_file, "r", encoding="utf-8", errors="replace") as f:
                raw_content = f.read().strip()
            p_stitch, p_jules = cls._parse_single_prompt(raw_content)
            stitch_prompt = stitch_prompt or p_stitch
            jules_prompt = jules_prompt or p_jules

        file_label = file_label.strip() or "Tarefa Não Identificada"

        if dry_run:
            has_stitch = "Sim" if stitch_prompt and not skip_stitch else "Não"
            has_jules = "Sim" if jules_prompt else "Não"
            print(f"\n{Colors.BOLD}{Colors.CYAN}=== 🔍 SIMULAÇÃO DE ORQUESTRAÇÃO DE PIPELINE [DRY-RUN] ==={Colors.RESET}")
            print(f"  • Prompt Alvo: {file_label}")
            print(f"  • Stitch (Design UI): {has_stitch}")
            print(f"  • Jules (Backend/Código): {has_jules}")
            print(f"  • Branch Alvo: {starting_branch}")
            return

        print(f"\n{Colors.BOLD}{Colors.CYAN}🚀 INICIANDO PIPELINE: {file_label}{Colors.RESET}")
        log("PARSER", f"Visual: {len(stitch_prompt)} chars | Dev: {len(jules_prompt)} chars", Colors.DIM)

        current_screen_id, stitch_html, screenshot_url, screen_title = screen_id or edit_screen_id, "", "", ""

        if not skip_stitch:
            machine.transition_to(LoopState.DESIGN_GENERATING, active_item=file_label)
            d_res = process_design_stage(stitch_prompt, current_screen_id, edit_screen_id, device_type, auto_approve, sync_ds)
            if d_res.get("cancelled"): return
            current_screen_id = d_res.get("current_screen_id")
            stitch_html = d_res.get("stitch_html")
            screenshot_url = d_res.get("screenshot_url")
            screen_title = d_res.get("screen_title")

        log("ETAPA 4/6", "🧠 Síntese Cognitiva e Consolidação do Prompt para o Jules...", Colors.HEADER)
        stitch_summary = ""
        if not skip_stitch and (stitch_html or stitch_prompt):
            client_agy = AntigravityClient()
            stitch_summary = cls._synthesize_stitch_ui(client_agy, stitch_prompt, stitch_html, screen_title)

        rules_summary = cls._extract_clean_rules()

        machine.transition_to(LoopState.PROMPT_SYNTHESIZING)
        executive_prompt = build_executive_prompt(
            repo_name, starting_branch, file_label, jules_prompt, stitch_prompt,
            current_screen_id, screen_title, screenshot_url, stitch_summary, rules_summary, skip_stitch
        )

        log("PIPELINE", f"Prompt consolidado para o Jules gerado!", Colors.GREEN)

        log("ETAPA 5/6", "⚡ Despachando Tarefa na Cloud do Google Jules...", Colors.HEADER)
        jules_client = JulesClient()
        session_resp = jules_client.create_session(
            prompt=executive_prompt,
            source_name=f"sources/github/{repo_name}",
            title=f"Task: {file_label.replace('.md', '').replace('_', ' ').title()}",
            base_branch=starting_branch
        )

        session_id = session_resp.get("name", "").split("/")[-1] or session_resp.get("id", "")
        if not session_id: raise AmbError(f"Resposta inválida Jules: {session_resp}")

        machine.set_active_session(session_id=session_id, item_name=file_label)

        if auto_merge:
            cls._monitor_jules_session(session_id, repo_root, no_qa, auto_merge=auto_merge, starting_branch=starting_branch, json_mode=json_mode)
        else:
            cls._monitor_jules_session(session_id, repo_root, no_qa, json_mode=json_mode)

    @classmethod
    def _monitor_jules_session(
        cls, session_id: str, repo_root: str, no_qa: bool = False,
        auto_merge: bool = False, starting_branch: str = "main", json_mode: bool = False
    ):
        machine = LoopStateMachine(repo_root=repo_root)
        client = JulesClient()
        from agents.autonomous_loop import monitor_and_assist_session
        state = monitor_and_assist_session(client=client, session_id=session_id, auto_reply_ai=True)
        if not no_qa:
            log("ETAPA 6/6", "🛡️ Gatekeeper 2: Validação Local de Integridade", Colors.HEADER)
            machine.transition_to(LoopState.QA_VALIDATING, session_id=session_id, active_item=f"QA for {session_id}")
            qa_ok = QualityGatekeeper.run_qa(repo_root)
            if not qa_ok:
                log_error("PIPELINE", "Validação local de QA falhou. Abortando processo de integração.")
                return
        if auto_merge and state in ["COMPLETED", "SUCCEEDED"]:
            from integrations.jules.tools.merge_session_pr import run_merge_session_pr
            log("PIPELINE", "🔀 Integrando Pull Request automaticamente no Git...", Colors.HEADER)
            run_merge_session_pr(session_id=session_id, target_branch=starting_branch)

        machine.transition_to(LoopState.CYCLE_COMPLETED)

        cls._record_and_present_summary(cls._current_run_start_time if hasattr(cls, '_current_run_start_time') else time.time(), json_mode)


    @staticmethod
    def _parse_single_prompt(markdown_text: str) -> tuple[str, str]:
        return parse_single_prompt(markdown_text)

    @classmethod
    def _extract_clean_rules(cls, rules_dir: Optional[str] = None, max_chars_per_file: int = 1500) -> str:
        return get_rules_manager(custom_dir=rules_dir).load_rules(rules_dir=rules_dir)

    @classmethod
    def _clean_html_for_summary(cls, html: str) -> str:
        return clean_html_for_summary(html)

    @classmethod
    def _synthesize_stitch_ui(cls, client_agy: AntigravityClient, stitch_prompt: str, stitch_html: str, screen_title: str) -> str:
        return synthesize_stitch_ui(client_agy, stitch_prompt, stitch_html, screen_title)

    @classmethod
    def _record_and_present_summary(cls, start_time: float, json_mode: bool):
        round_duration = time.time() - start_time
        metrics = LocalTelemetry.get_round_metrics(start_time)
        metrics["total_duration_seconds"] = round_duration
        metrics["total_items"] = 1
        metrics["total_stitch_screens"] = 1
        LocalTelemetry.record_event("ROUND_COMPLETED", metrics)
        ConsolePresenter(json_mode=json_mode).render_executive_summary(metrics)

def main():
    parser = argparse.ArgumentParser(description="Pipeline Autônomo Design-to-Code (AMB_V2)")
    parser.add_argument("prompt_file", nargs="?", help="Caminho do arquivo markdown de prompt unificado")
    parser.add_argument("--stitch-prompt", "-s", help="Caminho do arquivo markdown contendo a especificação visual para o Stitch")
    parser.add_argument("--jules-prompt", "-j", help="Caminho do arquivo markdown contendo a especificação de engenharia para o Jules")
    parser.add_argument("--auto-approve", "-y", action="store_true", help="Pula confirmações manuais no Gatekeeper 1 de Design")
    parser.add_argument("--skip-stitch", action="store_true", help="Pula a etapa de layout visual do Stitch e vai direto ao Jules")
    parser.add_argument("--no-qa", action="store_true", help="Não executa a verificação local de typecheck/build ao final")
    parser.add_argument("--resume-session", "-r", help="Retoma o monitoramento de uma sessão existente do Jules")
    parser.add_argument("--resume", action="store_true", help="Retoma o monitoramento da sessão ativa salva no loop_state.json")
    parser.add_argument("--device-type", choices=["DESKTOP", "MOBILE", "TABLET"], default=None, help="Tipo de dispositivo alvo para o Stitch")
    parser.add_argument("--screen-id", help="ID de tela existente no Stitch para reaproveitar")
    parser.add_argument("--edit-screen", help="ID de tela existente para refinar com novo prompt")
    parser.add_argument("--sync-ds", action="store_true", help="Sincroniza os design tokens locais com o Stitch antes de iniciar")
    parser.add_argument("--branch", "-b", help="Branch de início para o Jules (Padrão: detecta a atual ou develop)")
    parser.add_argument("--auto-merge", action="store_true", help="Realiza o merge automático do Pull Request no Git após aprovação nos testes locais de QA.")
    parser.add_argument("--json", action="store_true", help="Output json só")
    parser.add_argument("--no-auto-merge", action="store_true", help="Desabilita o merge automático do Pull Request ao concluir.")

    args = parser.parse_args()

    if not args.prompt_file and not args.stitch_prompt and not args.jules_prompt and not args.resume_session and not getattr(args, 'resume', False):
        parser.print_help()
        sys.exit(0)

    try:
        PipelineOrchestrator.run(
            prompt_file=args.prompt_file, stitch_prompt_file=args.stitch_prompt, jules_prompt_file=args.jules_prompt,
            auto_approve=args.auto_approve, skip_stitch=args.skip_stitch, no_qa=args.no_qa,
            resume_session=args.resume_session, device_type=args.device_type, edit_screen_id=args.edit_screen,
            screen_id=args.screen_id, sync_ds=args.sync_ds, starting_branch=args.branch,
            auto_merge=args.auto_merge, no_auto_merge=args.no_auto_merge, resume=getattr(args, "resume", False), json_mode=getattr(args, "json", False)
        )
    except AmbError as e:
        log_error("PIPELINE", e.message, hint=e.hint)
        sys.exit(1)
    except Exception as e:
        log_error("PIPELINE", str(e))
        sys.exit(1)

if __name__ == "__main__":
    main()
