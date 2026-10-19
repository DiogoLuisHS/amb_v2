#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Responsabilidade Única: Orquestrador de alto nível dos ciclos de desenvolvimento autônomo contínuo, delegando despacho e preparação de contexto para `amb_cli/agents/loop_core/cycle_dispatcher.py` e monitoramento/assistência cognitiva para `amb_cli/agents/loop_core/session_assistant.py`.
"""
import os
import sys
import time
import argparse
from pathlib import Path
from typing import List, Optional
from core.bootstrap import ensure_amb_env
ensure_amb_env()
from core import Colors, log, log_error, AmbError
from core.console_presenter import ConsolePresenter
from core.local_telemetry import LocalTelemetry
from workspace import find_repo_root, get_repo_name, IssueSynchronizer
from integrations.git.git_service import GitService
from integrations.jules.jules_client import JulesClient
from amb_cli.agents.persona_engine import PersonaEngine
from agents.loop_core.session_assistant import monitor_and_assist_session
from agents.loop_core.cycle_dispatcher import build_ai_context, dispatch_jules_session, handle_pr_merge
from pipeline.pipeline import PipelineOrchestrator
def _record_and_present_summary(start_time: float, items_count: int, json_mode: bool):
    round_duration = time.time() - start_time
    metrics = LocalTelemetry.get_round_metrics(start_time)
    metrics.update({"total_duration_seconds": round_duration, "total_items": items_count})
    LocalTelemetry.record_event("ROUND_COMPLETED", metrics)
    ConsolePresenter(json_mode=json_mode).render_executive_summary(metrics)
def run_autonomous_loop(
    role: Optional[str] = None,
    all_personas: bool = False,
    prompt_file: Optional[str] = None,
    modules: Optional[List[str]] = None,
    max_cycles: Optional[int] = None,
    delay_between_cycles: int = 0,
    branch: Optional[str] = None,
    no_auto_merge: bool = False,
    use_issues: bool = False,
    concurrency: int = 1,
    use_pipeline: bool = False, dry_run: bool = False, json_mode: bool = False) -> None:
    """Executa o loop contínuo de envio, monitoramento, auto-resposta e re-disparo para personas, prompts ou issues."""
    repo_name = get_repo_name()
    repo_root = find_repo_root()
    client = JulesClient()
    source_name = f"sources/github/{repo_name}"
    if not branch or branch in ["develop", "main"]:
        branch = GitService(repo_root=repo_root).get_current_branch(cwd=repo_root)
    branch = branch or "main"
    engine = PersonaEngine(repo_root=repo_root)
    discovered = engine.discover_personas()
    syncer = IssueSynchronizer(repo_root=repo_root)
    items_to_run = syncer.resolve_items_queue(prompt_file, use_issues=use_issues)
    if not items_to_run:
        if prompt_file or use_issues:
            log_error("AGENT", "Nenhum item válido encontrado na fila para processamento.")
            return
        if all_personas:
            items_to_run = [{"type": "persona", "name": k} for k in discovered.keys()] if discovered else [{"type": "persona", "name": "engineer"}]
        elif role:
            items_to_run = [{"type": "persona", "name": role}]
        else:
            items_to_run = [{"type": "persona", "name": k} for k in discovered.keys()] if discovered else [{"type": "persona", "name": "engineer"}]
    if dry_run:
        print(f"\n{Colors.BOLD}{Colors.CYAN}=== 🔍 SIMULAÇÃO DE ORQUESTRAÇÃO EM LOTE [DRY-RUN] ==={Colors.RESET}")
        print(f"  • Total de Itens: {len(items_to_run)}")
        print(f"  • Branch Base: {branch}")
        print(f"  • Fila Ordenada de Execução:")
        for idx, item in enumerate(items_to_run, 1):
            if item["type"] == "issue":
                title = item.get("title", f"Issue #{item.get('issue_number')}")
                print(f"    {idx}. [Issue] {item.get('issue_number')} -> \"{title}\"")
            elif item["type"] == "prompt":
                p_path = Path(item["path"])
                title = p_path.stem.replace('_', ' ').title()
                mode = "Pipeline Visual" if use_pipeline else "Jules Direct"
                print(f"    {idx}. [Prompt] {p_path.name} -> \"{title}\" ({mode})")
            else:
                print(f"    {idx}. [Persona] {item['name'].capitalize()} Agent")
        return
    modules_list = modules or [""]
    print(f"\n{Colors.BOLD}{Colors.CYAN}🔁 INICIANDO LOOP AUTÔNOMO JULES + ANTIGRAVITY{Colors.RESET}")
    print(f"📁 Repositório: {Colors.BOLD}{repo_name}{Colors.RESET} (Branch: {branch})")
    if items_to_run and items_to_run[0]["type"] == "issue":
        issues_summary = ", ".join(f"#{it.get('issue_number')}" for it in items_to_run)
        print(f"📋 Fila de Issues ({len(items_to_run)}): {Colors.BOLD}{issues_summary}{Colors.RESET}")
    elif items_to_run and items_to_run[0]["type"] == "prompt":
        print(f"📄 Prompts no Lote ({len(items_to_run)}): {Colors.BOLD}{', '.join([it['name'] for it in items_to_run])}{Colors.RESET}")
    else:
        print(f"🤖 Personas no Ciclo ({len(items_to_run)}): {Colors.BOLD}{', '.join([it['name'] for it in items_to_run])}{Colors.RESET}")
    if modules and modules != [""]:
        print(f"🎯 Módulos em Rotação: {', '.join(modules)}")
    print(f"⏱️ Limite de Ciclos: {f'{max_cycles} rodadas completas' if max_cycles else 'Infinito (Contínuo)'}")
    print(f"🔀 Nível de Concorrência: {concurrency}\n")
    completed_cycles = 0
    round_start_time = time.time()
    while True:
        completed_cycles += 1
        print(f"\n🔄 {Colors.BOLD}CICLO #{completed_cycles} DE {max_cycles if max_cycles else '∞'}{Colors.RESET}\n")
        current_module = modules_list[(completed_cycles - 1) % len(modules_list)]
        # Preparar prompts para todos os itens primeiro
        prepared_items = []
        for item in items_to_run:
            item_name = item["name"]
            if item["type"] == "issue":
                iss_num = item["issue_number"]
                iss_title = item["title"]
                task_content = (
                    f"# 🎯 GitHub Issue #{iss_num}: {iss_title}\n"
                    f"- URL: {item.get('url', '')}\n\n"
                    f"{item['content']}\n\n"
                    f"---\n"
                    f"- **Fechamento**: Inclua `Closes #{iss_num}` no corpo do Pull Request.\n"
                )
                session_title = f"[Issue #{iss_num}] {iss_title} - Ciclo #{completed_cycles}" if iss_num > 0 else f"{iss_title} - Ciclo #{completed_cycles}"
                stem_name = item.get("path").stem if item.get("path") else f"issue_{iss_num}"
                full_prompt = build_ai_context(task_content, None, stem_name)
            elif item["type"] == "prompt":
                p_path = Path(item["path"])
                base_prompt = item.get("content") or p_path.read_text(encoding="utf-8", errors="replace")
                title = f"Task: {p_path.stem.replace('_', ' ').title()}"
                session_title = f"{title} - Ciclo #{completed_cycles}"
                full_prompt = build_ai_context(base_prompt, None, p_path.stem)
            else:
                # Usar PersonaEngine para unificação e DRY
                base_prompt_raw = engine.load_persona(item_name)
                if not base_prompt_raw:
                    if item_name.lower() == "engineer":
                        base_prompt_raw = (
                            "Você é o Autonomous Software Engineer. Sua missão é dar continuidade ao desenvolvimento do projeto.\n"
                            "Analise débitos técnicos, implemente melhorias e abra o Pull Request quando concluído."
                        )
                    else:
                        base_prompt_raw = f"Você é o agente especialista {item_name} do projeto."
                    log("AGENT", f"Persona '{item_name}' não encontrada. Usando fallback padrão.", Colors.YELLOW)
                base_prompt = engine.render_persona_template(base_prompt_raw)
                # Para manter compatibilidade de pegar title:
                # O title vem da descoberta ou de fallback.
                title = item_name.capitalize() + " Agent"
                if discovered and item_name.lower() in discovered:
                    title = discovered[item_name.lower()].get("title", title)
                elif item_name.lower() == "engineer":
                    title = "Autonomous Software Engineer"
                if current_module:
                    full_prompt = (
                        f"{base_prompt}\n\n---\n\n"
                        f"**Foco Modular**: Concentre auditoria e alterações estritamente no módulo `{current_module}`."
                    )
                    session_title = f"{title} [{current_module}] - Ciclo #{completed_cycles}"
                else:
                    session_title = f"{title} - Ciclo #{completed_cycles}"
                    full_prompt = base_prompt
                full_prompt = build_ai_context(full_prompt, current_module, item_name)
            item["_full_prompt"] = full_prompt
            item["_session_title"] = session_title
            prepared_items.append(item)
        if concurrency > 1:
            from agents.loop_core.concurrent_runner import ConcurrentLoopRunner
            runner = ConcurrentLoopRunner(
                items=prepared_items,
                max_concurrency=concurrency,
                client=client,
                branch=branch,
                repo_root=repo_root,
                source_name=source_name,
                completed_cycles=completed_cycles,
                syncer=syncer,
                no_auto_merge=no_auto_merge
            )
            try:
                success = runner.run()
                if not success:
                    log_error("LOOP", "Um ou mais itens falharam durante a execução concorrente. Interrompendo a esteira.")
                    return
            except KeyboardInterrupt:
                print(f"\n{Colors.YELLOW}Loop interrompido pelo usuário.{Colors.RESET}")
                _record_and_present_summary(round_start_time, len(items_to_run) * completed_cycles, json_mode)
                return
        else:
            for item_idx, item in enumerate(prepared_items, 1):
                item_name = item["name"]
                if item["type"] == "issue":
                    print(f"\n📦 [{item_idx}/{len(prepared_items)}] Executando Issue #{item['issue_number']}: {Colors.BOLD}{item['title']}{Colors.RESET}")
                elif item["type"] == "prompt":
                    print(f"\n📦 [{item_idx}/{len(prepared_items)}] Executando Prompt: {Colors.BOLD}{item_name}{Colors.RESET}")
                else:
                    print(
                        f"\n📦 [{item_idx}/{len(prepared_items)}] Executando Persona: {Colors.BOLD}{item_name.upper()}{Colors.RESET}"
                        + (f" - Módulo: [{current_module}]" if current_module else "")
                    )
                # Despacho no Jules
                try:
                    if use_pipeline and item.get("path") and item.get("path").exists():
                        log("PIPELINE", f"Executando Pipeline para '{item_name}'", Colors.CYAN)
                        PipelineOrchestrator.run(
                            prompt_file=str(item["path"]),
                            auto_approve=True,
                            auto_merge=not no_auto_merge,
                            starting_branch=branch,
                        )
                        if item.get("type") == "issue" and item.get("issue_number", 0) > 0:
                            syncer.close_issue(item["issue_number"], comment=f"✅ Concluído via Pipeline em Lote (Ciclo #{completed_cycles}).")
                        if item.get("path"):
                            c_dir = item["path"].parent / "_completed"
                            c_dir.mkdir(parents=True, exist_ok=True)
                            try:
                                item["path"].rename(c_dir / item["path"].name)
                            except Exception:
                                pass
                        continue
                    session_id = dispatch_jules_session(
                        client, item["_full_prompt"], source_name, item["_session_title"], branch
                    )
                    # Monitoramento + Auto-Resposta
                    state = monitor_and_assist_session(
                        client=client, session_id=session_id, auto_reply_ai=True, require_pr=not no_auto_merge
                    )
                    # Aprovação e Integração do PR no Git com QA pós-merge
                    if state in ["COMPLETED", "SUCCEEDED"] and not no_auto_merge:
                        merged = handle_pr_merge(session_id, branch, repo_root, completed_cycles)
                        if not merged:
                            log_error(
                                "LOOP",
                                f"Integração obrigatória do item '{item_name}' na branch '{branch}' falhou. "
                                f"Interrompendo a esteira para garantir a integridade da branch principal.",
                            )
                            return
                        if item.get("type") == "issue" and item.get("issue_number", 0) > 0:
                            syncer.close_issue(item["issue_number"], comment=f"✅ Concluído e integrado com sucesso pelo AMB_V2 (Sessão Jules: {session_id}, Ciclo #{completed_cycles}).")
                            log("ISSUE", f"✔ GitHub Issue #{item['issue_number']} encerrada com sucesso!", Colors.GREEN)
                            if item.get("path") and item["path"].exists():
                                c_dir = item["path"].parent / "_completed"
                                c_dir.mkdir(parents=True, exist_ok=True)
                                try:
                                    item["path"].rename(c_dir / item["path"].name)
                                except Exception:
                                    pass
                    elif state == "COMPLETED_WITHOUT_PR":
                        log_error(
                            "LOOP",
                            f"A sessão Jules ({session_id}) do item '{item_name}' encerrou sem abrir Pull Request nem gerar alterações válidas. "
                            f"Interrompendo a esteira para evitar regressões.",
                        )
                        return
                    elif state not in ["COMPLETED", "SUCCEEDED"]:
                        log_error(
                            "LOOP",
                            f"A sessão Jules ({session_id}) do item '{item_name}' encerrou sem sucesso (Estado: {state}). "
                            f"Interrompendo a esteira para evitar regressões.",
                        )
                        return
                except KeyboardInterrupt:
                    print(f"\n{Colors.YELLOW}Loop interrompido pelo usuário.{Colors.RESET}")
                    _record_and_present_summary(round_start_time, len(items_to_run) * completed_cycles, json_mode)
                    return
                except Exception as e:
                    log_error("LOOP", f"Erro no processamento de '{item_name}': {e}")
                    return
                if delay_between_cycles > 0 and len(prepared_items) > 1:
                    log("LOOP", f"Pausa de {delay_between_cycles}s antes do próximo item...", Colors.DIM)
                    time.sleep(delay_between_cycles)
        if max_cycles and completed_cycles >= max_cycles:
            log("LOOP", f"Limite de {max_cycles} ciclos atingido. Todas as personas foram executadas com sucesso!", Colors.GREEN)
            _record_and_present_summary(round_start_time, len(items_to_run) * completed_cycles, json_mode)
            break
        log("LOOP", f"Ciclo #{completed_cycles} concluído. Iniciando Ciclo #{completed_cycles + 1}...", Colors.CYAN)
        if delay_between_cycles > 0:
            time.sleep(delay_between_cycles)
