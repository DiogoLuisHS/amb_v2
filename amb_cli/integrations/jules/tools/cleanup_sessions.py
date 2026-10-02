#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🧹 AMB_V2 - Jules SDK: Limpeza e Auditoria Segura de Sessões (SRP)
Localização: amb_v2/integrations/jules/tools/cleanup_sessions.py
Responsabilidade Única: Auditar sessões do Google Jules do repositório atual,
identificar quais foram integradas no Git e executar a exclusão segura na nuvem.
"""

import sys
import os
import argparse
import subprocess
import concurrent.futures
from typing import List, Dict, Any, Optional

from core.bootstrap import ensure_amb_env
ensure_amb_env()

from core import Colors, log, log_error
from workspace import get_repo_name
from integrations.git.git_service import GitService
from jules_client import JulesClient


def get_git_merge_history() -> str:
    """Obtém histórico de commits e merges do repositório local via GitService."""
    return GitService().get_log_oneline(count=300)


def audit_project_sessions(
    client: JulesClient,
    all_repos: bool = False,
    days: Optional[int] = None
) -> Dict[str, List[Dict[str, Any]]]:
    """Classifica as sessões do projeto em: merged, completed_no_pr, pending."""
    from datetime import datetime, timezone, timedelta
    cutoff = datetime.now(timezone.utc) - timedelta(days=days) if days is not None else None

    repo = None if all_repos else get_repo_name()
    sessions = client.list_sessions(page_size=100, repo_filter=repo, fetch_all=True)
    git_history = get_git_merge_history() if not all_repos else ""

    categorized = {
        "merged": [],
        "completed_no_pr": [],
        "failed": [],
        "pending": [],
    }

    for s in sessions:
        ctime_str = s.get("createTime")
        if cutoff and ctime_str:
            try:
                s_clean = (ctime_str[:26] + "Z") if "." in ctime_str else ctime_str
                dt = datetime.fromisoformat(s_clean)
                if dt.tzinfo is None:
                    dt = dt.replace(tzinfo=timezone.utc)
                if dt >= cutoff:
                    continue  # Mais recente que a data limite: preserva
            except Exception:
                continue  # Em caso de falha de parsing, preserva por segurança
        elif cutoff and not ctime_str:
            continue

        sid = JulesClient.normalize_session_id(s.get("name", "") or s.get("id"))
        state = s.get("state", "UNKNOWN")
        title = s.get("title", "Sem título")
        pr_info = JulesClient.extract_pull_request(s)
        pr_url = pr_info.get("url") if pr_info else None
        pr_num = str(pr_info.get("number")) if pr_info and pr_info.get("number") else (pr_url.split("/")[-1] if pr_url else None)
        
        is_merged = (f"#{pr_num}" in git_history) if (pr_num and git_history) else False

        item = {
            "session_id": sid,
            "state": state,
            "title": title,
            "pr_url": pr_url,
            "is_merged": is_merged,
            "create_time": ctime_str,
            "raw": s
        }

        if state == "FAILED":
            categorized["failed"].append(item)
        elif is_merged:
            categorized["merged"].append(item)
        elif state == "COMPLETED":
            categorized["completed_no_pr"].append(item)
        else:
            categorized["pending"].append(item)

    return categorized


def print_audit_report(categorized: Dict[str, List[Dict[str, Any]]], all_repos: bool = False, days: Optional[int] = None):
    """Exibe o relatório visual de auditoria."""
    repo = "Todos os Repositórios Conectados" if all_repos else get_repo_name()
    total = sum(len(v) for v in categorized.values())
    filter_str = f" (> {days} dias atrás)" if days is not None else ""
    print("\n" + "=" * 78)
    print(f"📊 {Colors.BOLD}{Colors.CYAN}AUDITORIA DE SESSÕES DO GOOGLE JULES — {repo}{filter_str}{Colors.RESET}")
    print("=" * 78)
    print(f"Total de sessões encontradas no escopo: {Colors.BOLD}{total}{Colors.RESET}\n")

    print(f"✅ {Colors.BOLD}{Colors.GREEN}[1] SESSÕES COM PRs JÁ MERGEADOS NO GIT ({len(categorized['merged'])}) — SEGURAS PARA EXCLUSÃO:{Colors.RESET}")
    for it in categorized["merged"]:
        print(f"   • {Colors.GREEN}✔{Colors.RESET} ID: {Colors.DIM}{it['session_id']}{Colors.RESET} | PR: {it['pr_url']} | {it['title'][:55]}")

    if categorized["completed_no_pr"]:
        print(f"\n📁 {Colors.BOLD}{Colors.BLUE}[2] SESSÕES CONCLUÍDAS SEM PR OU PR FECHADO ({len(categorized['completed_no_pr'])}):{Colors.RESET}")
        for it in categorized["completed_no_pr"]:
            pr_str = f" (PR: {it['pr_url']})" if it.get("pr_url") else " (Sem PR)"
            print(f"   • {Colors.BLUE}ℹ{Colors.RESET} ID: {Colors.DIM}{it['session_id']}{Colors.RESET}{pr_str} | {it['title'][:55]}")

    if categorized["pending"]:
        print(f"\n⏳ {Colors.BOLD}{Colors.YELLOW}[3] SESSÕES ATIVAS / PENDENTES / EM PROGRESSO ({len(categorized['pending'])}):{Colors.RESET}")
        for it in categorized["pending"]:
            print(f"   • {Colors.YELLOW}⏳{Colors.RESET} [{it['state']}] ID: {Colors.DIM}{it['session_id']}{Colors.RESET} | {it['title'][:55]}")

    if categorized["failed"]:
        print(f"\n❌ {Colors.BOLD}{Colors.RED}[4] SESSÕES COM ERRO FATAL (FAILED) ({len(categorized['failed'])}):{Colors.RESET}")
        for it in categorized["failed"]:
            print(f"   • {Colors.RED}✖{Colors.RESET} ID: {Colors.DIM}{it['session_id']}{Colors.RESET} | {it['title'][:55]}")

    print("\n" + "=" * 78 + "\n")


def execute_deletion(client: JulesClient, sessions_to_delete: List[Dict[str, Any]], dry_run: bool = False):
    """Executa a deleção das sessões selecionadas."""
    if not sessions_to_delete:
        print(f"{Colors.YELLOW}Nenhuma sessão para excluir.{Colors.RESET}")
        return

    total_sessions = len(sessions_to_delete)
    print(f"{'🔍 [DRY-RUN]' if dry_run else '🗑️ [EXCLUSÃO]'} Processando {total_sessions} sessões...")
    deleted_count = 0
    errors_count = 0
    skipped_count = 0

    terminal_states = {"COMPLETED", "SUCCEEDED", "FAILED", "CANCELED"}

    def delete_task(idx, it):
        sid = it["session_id"]
        title = it["title"][:50]
        state = it.get("state", "UNKNOWN")

        if state not in terminal_states:
            print(f"   [{idx}/{total_sessions}] {Colors.YELLOW}⏭️ Ignorada (estado '{state}'):{Colors.RESET} ID {sid} - {title}")
            return "SKIPPED", None

        if dry_run:
            print(f"   [{idx}/{total_sessions}] Seria excluída: ID {sid} - {title}")
            return "SUCCESS", None
        else:
            try:
                client.delete_session(sid)
                print(f"   [{idx}/{total_sessions}] {Colors.GREEN}✔ Excluída com sucesso:{Colors.RESET} ID {sid} - {title}")
                return "SUCCESS", None
            except Exception as e:
                print(f"   [{idx}/{total_sessions}] {Colors.RED}✖ Falha ao excluir {sid}:{Colors.RESET} {e}")
                return "ERROR", e

    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        futures = [executor.submit(delete_task, idx, it) for idx, it in enumerate(sessions_to_delete, 1)]

        for future in concurrent.futures.as_completed(futures):
            status, _ = future.result()
            if status == "SUCCESS":
                deleted_count += 1
            elif status == "ERROR":
                errors_count += 1
            elif status == "SKIPPED":
                skipped_count += 1

    print("\n" + "=" * 78)
    if dry_run:
        print(f"🔍 Dry-run concluído: {deleted_count} sessões seriam removidas | {skipped_count} ignoradas.")
    else:
        print(f"🎉 Limpeza concluída: {deleted_count} sessões excluídas | {errors_count} falhas | {skipped_count} ignoradas.")
    print("=" * 78 + "\n")


def run_cleanup_sessions(
    delete_mode: str = "merged",
    dry_run: bool = True,
    delete_id: Optional[str] = None,
    client: Optional[JulesClient] = None,
    days: Optional[int] = None,
    all_repos: bool = False
) -> Dict[str, Any]:
    """Serviço canônico de auditoria e limpeza de sessões do Jules para chamadas diretas de CLI e API (F1-M7)."""
    c = client or JulesClient()
    categorized = audit_project_sessions(c, all_repos=all_repos, days=days)
    print_audit_report(categorized, all_repos=all_repos, days=days)

    effective_mode = delete_mode
    if days is not None and delete_mode == "merged":
        effective_mode = "all_completed"

    if delete_id:
        found = False
        for cat, items in categorized.items():
            for item in items:
                if item["session_id"] == delete_id:
                    execute_deletion(c, [item], dry_run=dry_run)
                    found = True
                    break
            if found:
                break
        if not found:
            try:
                session_data = c.get_session(delete_id)
                state = session_data.get("state", "UNKNOWN")
                title = session_data.get("title", "Sessão Individual")
                execute_deletion(c, [{"session_id": delete_id, "title": title, "state": state}], dry_run=dry_run)
            except Exception as e:
                print(f"{Colors.RED}Erro ao buscar sessão {delete_id}:{Colors.RESET} {e}")
    elif effective_mode == "merged":
        execute_deletion(c, categorized["merged"], dry_run=dry_run)
    elif effective_mode == "failed":
        execute_deletion(c, categorized["failed"], dry_run=dry_run)
    elif effective_mode in ["all", "all_completed"]:
        all_completed = categorized["merged"] + categorized["completed_no_pr"]
        execute_deletion(c, all_completed, dry_run=dry_run)
    elif not dry_run:
        print(f"💡 Dica de Execução:")
        print(f"  • Simular exclusão de PRs integrados: amb jules clean")
        print(f"  • Excluir PRs já integrados no Git:   amb jules clean --force")
        print(f"  • Excluir sessões falhas (FAILED):     amb jules clean --failed --force")
        print(f"  • Excluir sessões com mais de N dias:  amb jules clean --days 3 --force\n")

    return categorized


def main():
    parser = argparse.ArgumentParser(description="Auditoria e Limpeza de Sessões do Google Jules.")
    parser.add_argument("--dry-run", action="store_true", help="Simula as ações sem executar exclusões reais.")
    parser.add_argument("--delete-merged", action="store_true", help="Exclui todas as sessões cujos PRs já foram mergeados no Git.")
    parser.add_argument("--delete-all-completed", action="store_true", help="Exclui todas as sessões concluídas (com e sem PR mergeado).")
    parser.add_argument("--delete-failed", action="store_true", help="Exclui todas as sessões que falharam (FAILED).")
    parser.add_argument("--delete-id", help="Exclui uma sessão específica por ID.")
    parser.add_argument("--days", "-d", type=int, help="Filtra apenas sessões criadas há mais de N dias.")
    parser.add_argument("--all-repos", action="store_true", help="Audita e limpa sessões de todos os repositórios conectados à conta.")

    args = parser.parse_args()

    mode = "merged"
    if args.delete_failed:
        mode = "failed"
    elif args.delete_all_completed:
        mode = "all_completed"

    run_cleanup_sessions(
        delete_mode=mode,
        dry_run=args.dry_run,
        delete_id=args.delete_id,
        days=args.days,
        all_repos=args.all_repos
    )


if __name__ == "__main__":
    main()
