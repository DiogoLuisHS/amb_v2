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
from typing import List, Dict, Any

# Bootstrap dinâmico de caminhos amb_v2
_cur = os.path.dirname(os.path.abspath(__file__))
while _cur and os.path.basename(_cur) != "amb_v2":
    _p = os.path.dirname(_cur)
    if _p == _cur:
        break
    _cur = _p
_AMB = _cur
for _sub in [
    "config", "agents", "pipeline", "dashboard", "dashboard/watchers",
    "integrations/jules", "integrations/jules/tools",
    "integrations/stitch", "integrations/stitch/tools",
    "integrations/antigravity", "integrations/antigravity/tools",
    "integrations/render", "integrations/render/tools",
]:
    _p = os.path.normpath(os.path.join(_AMB, *_sub.split("/")))
    if os.path.exists(_p) and _p not in sys.path:
        sys.path.insert(0, _p)

from config import Colors, log, log_error, get_repo_name
from jules_client import JulesClient


def get_git_merge_history() -> str:
    """Obtém histórico de commits e merges do repositório local."""
    res = subprocess.run(
        ["git", "log", "--oneline", "-n", "300"],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace"
    )
    return res.stdout


def audit_project_sessions(client: JulesClient) -> Dict[str, List[Dict[str, Any]]]:
    """Classifica as sessões do projeto em: merged, completed_no_pr, pending."""
    repo = get_repo_name()
    sessions = client.list_sessions(page_size=100, repo_filter=repo)
    git_history = get_git_merge_history()

    categorized = {
        "merged": [],
        "completed_no_pr": [],
        "pending": [],
    }

    for s in sessions:
        sid = s.get("name", "").split("/")[-1] or s.get("id")
        state = s.get("state", "UNKNOWN")
        title = s.get("title", "Sem título")
        outputs = s.get("outputs", [])
        prs = [o["pullRequest"] for o in outputs if "pullRequest" in o]
        
        pr_url = prs[0].get("url") if prs else None
        pr_num = pr_url.split("/")[-1] if pr_url else None
        
        is_merged = (f"#{pr_num}" in git_history) if pr_num else False

        item = {
            "session_id": sid,
            "state": state,
            "title": title,
            "pr_url": pr_url,
            "is_merged": is_merged,
            "raw": s
        }

        if is_merged:
            categorized["merged"].append(item)
        elif state == "COMPLETED":
            categorized["completed_no_pr"].append(item)
        else:
            categorized["pending"].append(item)

    return categorized


def print_audit_report(categorized: Dict[str, List[Dict[str, Any]]]):
    """Exibe o relatório visual de auditoria."""
    repo = get_repo_name()
    total = sum(len(v) for v in categorized.values())
    print("\n" + "=" * 78)
    print(f"📊 {Colors.BOLD}{Colors.CYAN}AUDITORIA DE SESSÕES DO GOOGLE JULES — {repo}{Colors.RESET}")
    print("=" * 78)
    print(f"Total de sessões encontradas no projeto: {Colors.BOLD}{total}{Colors.RESET}\n")

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


def main():
    parser = argparse.ArgumentParser(description="Auditoria e Limpeza de Sessões do Google Jules.")
    parser.add_argument("--dry-run", action="store_true", help="Simula as ações sem executar exclusões reais.")
    parser.add_argument("--delete-merged", action="store_true", help="Exclui todas as sessões cujos PRs já foram mergeados no Git.")
    parser.add_argument("--delete-all-completed", action="store_true", help="Exclui todas as sessões concluídas (com e sem PR mergeado).")
    parser.add_argument("--delete-id", help="Exclui uma sessão específica por ID.")

    args = parser.parse_args()
    client = JulesClient()
    categorized = audit_project_sessions(client)

    print_audit_report(categorized)

    if args.delete_id:
        found = False
        for cat, items in categorized.items():
            for item in items:
                if item["session_id"] == args.delete_id:
                    execute_deletion(client, [item], dry_run=args.dry_run)
                    found = True
                    break
            if found:
                break
        if not found:
            try:
                session_data = client.get_session(args.delete_id)
                state = session_data.get("state", "UNKNOWN")
                title = session_data.get("title", "Sessão Individual")
                execute_deletion(client, [{"session_id": args.delete_id, "title": title, "state": state}], dry_run=args.dry_run)
            except Exception as e:
                print(f"{Colors.RED}Erro ao buscar sessão {args.delete_id}:{Colors.RESET} {e}")
    elif args.delete_merged:
        execute_deletion(client, categorized["merged"], dry_run=args.dry_run)
    elif args.delete_all_completed:
        all_completed = categorized["merged"] + categorized["completed_no_pr"]
        execute_deletion(client, all_completed, dry_run=args.dry_run)
    elif not args.dry_run:
        print(f"💡 Dica de Execução:")
        print(f"  • Simular exclusão de PRs integrados: python amb_v2/integrations/jules/tools/cleanup_sessions.py --delete-merged --dry-run")
        print(f"  • Excluir PRs já integrados no Git:   python amb_v2/integrations/jules/tools/cleanup_sessions.py --delete-merged")
        print(f"  • Excluir todas as sessões concluídas: python amb_v2/integrations/jules/tools/cleanup_sessions.py --delete-all-completed\n")


if __name__ == "__main__":
    main()
