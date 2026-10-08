#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🏃 AMB_V2 - Concurrent Loop Runner (SRP Core)
Localização: amb_cli/agents/loop_core/concurrent_runner.py
Responsabilidade Única: Executar lotes de prompts/issues no Jules com paralelismo
controlado, mantendo até `max_concurrency` sessões ativas na nuvem,
e garantindo merge sequencial ordenado no Git local.
"""

import time
import concurrent.futures
from typing import List, Dict, Any, Optional

from core.bootstrap import ensure_amb_env
ensure_amb_env()

from core import Colors, log, log_error
from workspace import find_repo_root
from integrations.jules.jules_client import JulesClient
from agents.loop_core.cycle_dispatcher import dispatch_jules_session, handle_pr_merge
from agents.loop_core.session_assistant import monitor_and_assist_session


class ConcurrentLoopRunner:
    """Runner para execução concorrente de tarefas do loop no Jules."""

    def __init__(
        self,
        items: List[Dict[str, Any]],
        max_concurrency: int,
        client: JulesClient,
        branch: str,
        repo_root: str,
        source_name: str,
        completed_cycles: int,
        syncer: Optional[Any] = None,
        no_auto_merge: bool = False
    ):
        self.items = items
        self.max_concurrency = max_concurrency
        self.client = client
        self.branch = branch
        self.repo_root = repo_root
        self.source_name = source_name
        self.completed_cycles = completed_cycles
        self.syncer = syncer
        self.no_auto_merge = no_auto_merge

    def _process_item_jules(self, item: Dict[str, Any], idx: int) -> Dict[str, Any]:
        """Cria e monitora uma sessão do Jules. (Executado em thread)"""
        try:
            item_name = item["name"]

            # Reconstroi dados para o prompt
            full_prompt = item.get("_full_prompt", "")
            session_title = item.get("_session_title", f"Task: {item_name}")

            print(f"[{idx}/{len(self.items)}] 🚀 Despachando sessão Jules: {Colors.BOLD}{item_name}{Colors.RESET}")
            session_id = dispatch_jules_session(
                self.client, full_prompt, self.source_name, session_title, self.branch
            )

            state = monitor_and_assist_session(
                client=self.client, session_id=session_id, auto_reply_ai=True, quiet=True
            )

            return {
                "item": item,
                "session_id": session_id,
                "state": state,
                "success": state in ["COMPLETED", "SUCCEEDED"],
                "error": None
            }
        except Exception as e:
            return {
                "item": item,
                "session_id": None,
                "state": "FAILED",
                "success": False,
                "error": str(e)
            }

    def run(self) -> bool:
        """
        Executa os itens usando ThreadPoolExecutor.
        Aguarda a conclusão de cada um e, em seguida, enfileira o PR merge.
        Retorna True se todos os merges tiverem sucesso.
        """
        print(f"\n{Colors.BOLD}{Colors.CYAN}⚡ INICIANDO EXECUÇÃO CONCORRENTE ({self.max_concurrency} workers){Colors.RESET}\n")

        results = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_concurrency) as executor:
            future_to_item = {
                executor.submit(self._process_item_jules, item, idx): item
                for idx, item in enumerate(self.items, 1)
            }

            for future in concurrent.futures.as_completed(future_to_item):
                item = future_to_item[future]
                try:
                    result = future.result()
                    results.append(result)
                except Exception as exc:
                    log_error("CONCURRENCY", f"A tarefa {item['name']} gerou uma exceção: {exc}")
                    results.append({
                        "item": item, "session_id": None, "state": "FAILED", "success": False, "error": str(exc)
                    })

        # Processar merges sequencialmente para evitar conflitos no git
        print(f"\n{Colors.BOLD}{Colors.CYAN}🔗 INICIANDO INTEGRAÇÃO SEQUENCIAL DE PRs{Colors.RESET}\n")

        all_success = True
        for result in results:
            item = result["item"]
            session_id = result.get("session_id")
            item_name = item["name"]

            if not result["success"]:
                log_error(
                    "CONCURRENCY",
                    f"A sessão Jules de '{item_name}' (ID: {session_id}) falhou (Estado: {result.get('state')}). Erro: {result.get('error')}"
                )
                all_success = False
                continue

            if not self.no_auto_merge and session_id:
                merged = handle_pr_merge(session_id, self.branch, self.repo_root, self.completed_cycles)
                if not merged:
                    log_error("CONCURRENCY", f"Falha na integração de '{item_name}' na branch '{self.branch}'.")
                    all_success = False
                else:
                    if self.syncer and item.get("type") == "issue" and item.get("issue_number", 0) > 0:
                        self.syncer.close_issue(
                            item["issue_number"],
                            comment=f"✅ Concluído e integrado com sucesso pelo AMB_V2 (Sessão Jules: {session_id}, Ciclo #{self.completed_cycles})."
                        )
                        log("ISSUE", f"✔ GitHub Issue #{item['issue_number']} encerrada com sucesso!", Colors.GREEN)

        return all_success
