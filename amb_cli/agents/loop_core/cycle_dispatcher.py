#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🤖 AMB_V2 - Cycle Dispatcher (SRP Core)
Localização: amb_cli/agents/loop_core/cycle_dispatcher.py
Responsabilidade Única: Gerenciar a preparação de contexto (arquivos + diffs),
despachar sessões para o Google Jules e cuidar da aprovação e merge de PRs.
"""

import time
from typing import Optional

from config.bootstrap import ensure_amb_env
ensure_amb_env()

from config import Colors, log, log_error, AmbError, find_repo_root
from integrations.jules.jules_client import JulesClient
from integrations.jules.tools.merge_session_pr import approve_and_merge_pr
from integrations.git.git_service import GitService
from pathlib import Path


def build_ai_context(
    base_prompt: str, current_module: Optional[str], role: str
) -> str:
    """Invoca o AI Context Builder de forma programática."""
    full_prompt = base_prompt
    try:
        from architecture.ai_context_builder import ProjectDependencyAnalyzer
        root_dir = Path(find_repo_root())
        builder = ProjectDependencyAnalyzer(root_dir)
        builder.analyze()
        _ctx_query = current_module or role or ""

        # The AIContextBuilder finds the files related to the target using trace_module_chain
        related_files = builder.trace_module_chain(_ctx_query)
        total_ctx_files = len(related_files)

        if total_ctx_files > 0:
            layers = builder.classify_and_order_files(related_files)
            _ctx_md = builder.generate_markdown(_ctx_query, layers)
            full_prompt = (
                f"{full_prompt}\n\n"
                f"---\n\n"
                f"## 📂 ROTEIRO DE LEITURA ARQUITETURAL (gerado por `amb context {_ctx_query}`)\n\n"
                f"**Use este roteiro para iniciar sua análise sem precisar explorar o repositório do zero.**\n"
                f"Leia os arquivos na ordem apresentada (DB → Repositórios → Services → Controllers → UI):\n\n"
                f"{_ctx_md}"
            )
            log(
                "LOOP",
                f"Roteiro arquitetural '{_ctx_query}' ({total_ctx_files} arquivos) anexado ao prompt.",
                Colors.GREEN,
            )
    except Exception as ctx_err:
        log("LOOP", f"Aviso: ai_context_builder falhou — {ctx_err}", Colors.DIM)

    return full_prompt


def dispatch_jules_session(
    client: JulesClient,
    full_prompt: str,
    source_name: str,
    session_title: str,
    branch: str,
) -> str:
    """Cria a sessão no Jules e retorna o ID."""
    log("LOOP", "Criando sessão para persona no Google Jules...", Colors.CYAN)

    session_resp = client.create_session(
        prompt=full_prompt,
        source_name=source_name,
        title=session_title,
        base_branch=branch,
    )

    session_id = session_resp.get("name", "").split("/")[-1] or session_resp.get(
        "id", ""
    )
    if not session_id:
        raise AmbError(f"Falha ao obter ID da sessão: {session_resp}")

    print(f"🎉 Sessão Criada: {Colors.GREEN}{session_id}{Colors.RESET}")
    print(
        f"🔗 Acompanhe: {Colors.BLUE}https://jules.google.com/session/{session_id}{Colors.RESET}\n"
    )

    log("LOOP", "Aguardando provisionamento da VM no Jules (5s)...", Colors.DIM)
    time.sleep(5)

    return session_id


def handle_pr_merge(
    session_id: str, branch: str, repo_root: str, completed_cycles: int
) -> None:
    """Aprova e integra o Pull Request no Git local."""
    log(
        "GIT-MERGE",
        f"Verificando Pull Request da sessão {session_id}...",
        Colors.HEADER,
    )
    try:
        merged = approve_and_merge_pr(session_id=session_id, target_branch=branch)
        if merged:
            log(
                "GIT-SYNC",
                f"✔ Sincronização concluída com sucesso! origin/{branch} atualizado com as mudanças do Ciclo #{completed_cycles}.",
                Colors.GREEN,
            )
            # Garante que o git local puxa e valida origin
            GitService(repo_root=repo_root).pull("origin", branch, cwd=repo_root)
    except Exception as em:
        log_error("GIT-MERGE", f"Aviso na integração do PR: {em}")
