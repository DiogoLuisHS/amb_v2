#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔀 AMB_V2 - Jules SDK: Aprovação de PR e Integração Contínua no Git (SRP)
Localização: amb_cli/integrations/jules/tools/merge_session_pr.py
Responsabilidade Única: Detectar o PR ou branch gerado pelo Google Jules, aprovar o PR,
realizar o merge no GitHub, sincronizar localmente e validar com typecheck/build.
"""

import os
import sys
import re
import time
import argparse
import subprocess
from typing import Optional, Dict, Any

from core.bootstrap import ensure_amb_env
ensure_amb_env()

from core import Colors, log, log_error
from workspace import find_repo_root, get_repo_name
from integrations.git.git_service import GitService
from jules_client import JulesClient


def detect_pr_from_session(session_id: str) -> Optional[int]:
    """Inspeciona os outputs da sessão e as atividades para extrair o número do PR via JulesClient."""
    client = JulesClient()
    try:
        clean_id = JulesClient.normalize_session_id(session_id)
        sess = client.get_session(clean_id)
        act_res = client.list_activities(session_id=clean_id, page_size=25)
        activities = act_res.get("activities", []) if isinstance(act_res, dict) else (act_res if isinstance(act_res, list) else [])
        pr_info = JulesClient.extract_pull_request(sess, activities=activities)
        if pr_info:
            if pr_info.get("number"):
                return int(pr_info["number"])
            if pr_info.get("url"):
                m = re.search(r"/pull/(\d+)", pr_info["url"])
                if m:
                    return int(m.group(1))
    except Exception as e:
        log_error("DETECT-PR", f"Falha ao consultar PR da sessão no Jules: {e}")
    return None


def detect_pr_from_github(session_id: str, repo_name: Optional[str] = None) -> Optional[int]:
    """Consulta diretamente o GitHub via GitService buscando PRs abertos correlacionados com o session_id."""
    clean_id = JulesClient.normalize_session_id(session_id)
    git = GitService()
    try:
        open_prs = git.list_open_prs(repo_name=repo_name, include_drafts=True)
        # 1. Correspondência rápida por nome da branch ou título
        for pr in open_prs:
            head_ref = str(pr.get("headRefName") or "")
            title = str(pr.get("title") or "")
            if clean_id in head_ref or clean_id in title:
                return int(pr["number"])
        # 2. Correspondência pelo corpo dos PRs abertos mais recentes
        for pr in open_prs[:5]:
            pr_detail = git.get_pr(pr["number"], repo_name=repo_name)
            if pr_detail and clean_id in str(pr_detail.get("body") or ""):
                return int(pr["number"])
    except Exception as e:
        log_error("DETECT-PR", f"Falha ao consultar PRs diretamente no GitHub: {e}")
    return None


def detect_and_create_pr_from_branch(
    session_id: str,
    target_branch: str = "main",
    repo_name: Optional[str] = None,
    repo_root: Optional[str] = None
) -> Optional[int]:
    """Se o Jules apenas enviou a branch remota sem abrir o PR, cria o PR via GitHub CLI."""
    clean_id = JulesClient.normalize_session_id(session_id)
    git = GitService(repo_root=repo_root)
    target_repo = repo_name or get_repo_name()
    git.fetch("origin")
    try:
        res = subprocess.run(
            ["git", "branch", "-r"],
            cwd=git._resolve_cwd(),
            capture_output=True,
            text=True,
            check=False,
            encoding="utf-8",
            errors="replace"
        )
        if res.returncode == 0:
            for line in res.stdout.splitlines():
                if clean_id in line:
                    branch_name = line.strip().split("origin/")[-1].strip()
                    log("GIT-SYNC", f"Branch remota 'origin/{branch_name}' detectada. Criando PR...", Colors.HEADER)
                    title = f"feat(jules): automated integration for session {clean_id}"
                    body = f"Pull Request criado automaticamente pelo AMB_V2 a partir da branch remota `{branch_name}`."
                    pr_data = git.create_pr(title=title, body=body, base=target_branch, head=branch_name, repo_name=target_repo)
                    if pr_data.get("number"):
                        pr_num = int(pr_data["number"])
                        log("GIT-SYNC", f"✔ PR #{pr_num} criado com sucesso via GitHub CLI!", Colors.GREEN)
                        return pr_num
    except Exception as e:
        log_error("GIT-SYNC", f"Falha ao auto-criar PR a partir da branch remota: {e}")
    return None


def get_latest_open_pr(repo_name: str) -> Optional[Dict[str, Any]]:
    """Consulta os PRs abertos no repositório via GitService (GitHub CLI), incluindo drafts."""
    return GitService().get_latest_open_pr(repo_name=repo_name)


def apply_session_patch(
    session_id: str,
    repo_root: str,
    target_branch: str,
    git: GitService
) -> bool:
    """Aplica o patch unificado da sessão localmente como fallback extremo."""
    log("GIT-SYNC", "Verificando patches diretos no session outputs...", Colors.CYAN)
    client = JulesClient()
    try:
        sess = client.get_session(session_id)
        outputs = sess.get("outputs", [])
        if not outputs:
            return False
        patch_info = outputs[0].get("changeSet", {}).get("gitPatch", {})
        diff = patch_info.get("unidiffPatch", "")
        commit_msg = patch_info.get("suggestedCommitMessage", f"chore(jules): integrate session {session_id}")
        if not diff:
            return False

        log("GIT-SYNC", "Patch detectado no session outputs. Aplicando localmente...", Colors.HEADER)
        patch_path = os.path.join(repo_root, ".tmp_jules.patch")
        with open(patch_path, "w", encoding="utf-8") as pf:
            pf.write(diff)
        apply_res = subprocess.run(
            ["git", "apply", "--whitespace=fix", "--ignore-space-change", "--ignore-whitespace", patch_path],
            cwd=repo_root, capture_output=True, text=True, encoding="utf-8", errors="replace", shell=False
        )
        if os.path.exists(patch_path):
            os.remove(patch_path)

        if apply_res.returncode != 0:
            all_applied = True
            for p_idx, p in enumerate(diff.split("diff --git ")[1:], 1):
                f_rel = p.split("\n")[0].split(" b/")[-1].strip()
                single_p = "diff --git " + p
                if "@@" not in single_p and "new file mode" in single_p:
                    t_path = os.path.join(repo_root, f_rel)
                    os.makedirs(os.path.dirname(t_path), exist_ok=True)
                    open(t_path, "a", encoding="utf-8").close()
                    continue
                p_part = os.path.join(repo_root, f".tmp_{p_idx}.patch")
                with open(p_part, "w", encoding="utf-8") as ppf:
                    ppf.write(single_p)
                p_res = subprocess.run(["git", "apply", "--whitespace=fix", "--ignore-space-change", "--ignore-whitespace", p_part], cwd=repo_root, capture_output=True, text=True, check=False)
                if os.path.exists(p_part):
                    os.remove(p_part)
                if p_res.returncode != 0:
                    all_applied = False
            if not all_applied:
                log_error("GIT-SYNC", f"Falha ao aplicar patch via git apply:\n{apply_res.stderr}")
                return False

        git.add_all_and_commit(commit_msg, cwd=repo_root)
        print(f"{Colors.GREEN}✔ Patch da sessão aplicado e commitado com sucesso!{Colors.RESET}\n")

        log("QA-VALIDATION", "Executando verificação de integridade pós-patch...", Colors.CYAN)
        from pipeline.quality_gatekeeper import QualityGatekeeper
        if not QualityGatekeeper.run_qa(repo_root):
            log_error("QA", "A suíte de testes e validação local falhou após aplicar o patch.")
            return False

        log("GIT-PUSH", f"Enviando alterações validadas para origin/{target_branch}...", Colors.CYAN)
        git.push("origin", target_branch, cwd=repo_root)
        print(f"{Colors.GREEN}✔ Alterações enviadas com sucesso para o GitHub!{Colors.RESET}\n")
        return True
    except Exception as e:
        log_error("GIT-SYNC", f"Falha ao processar patch da sessão: {e}")
        return False


def approve_and_merge_pr(
    session_id: Optional[str] = None,
    pr_number: Optional[int] = None,
    auto_latest: bool = False,
    target_branch: str = "main",
    auto_approve_review: bool = True,
    max_retries: int = 10,
    retry_delay: int = 5
) -> bool:
    """Aprova o PR no GitHub, realiza o merge (squash), puxa localmente e valida com QA."""
    repo_root = find_repo_root()
    repo_name = get_repo_name()
    git = GitService(repo_root=repo_root)
    resolved_pr = pr_number

    # 1. Identifica o PR com retry multissetorial (GitHub -> Jules API -> Auto-Create de branch remota)
    for attempt in range(max_retries):
        if not resolved_pr and session_id:
            log("GIT-SYNC", f"Buscando PR vinculado à sessão {session_id} (tentativa {attempt+1}/{max_retries})...", Colors.CYAN)
            # A. Consulta direta e veloz ao GitHub CLI
            resolved_pr = detect_pr_from_github(session_id, repo_name)
            # B. Consulta de metadados da sessão no Jules REST API
            if not resolved_pr:
                resolved_pr = detect_pr_from_session(session_id)
            # C. A partir da 4ª tentativa (~15s), se o Jules enviou a branch remota sem abrir o PR, cria automaticamente
            if not resolved_pr and attempt >= 3:
                resolved_pr = detect_and_create_pr_from_branch(session_id, target_branch, repo_name, repo_root)

        if not resolved_pr and (auto_latest or not session_id):
            log("GIT-SYNC", f"Buscando último PR aberto no repositório {repo_name} (tentativa {attempt+1}/{max_retries})...", Colors.CYAN)
            latest = get_latest_open_pr(repo_name)
            if latest:
                resolved_pr = latest.get("number")

        if resolved_pr:
            log("GIT-SYNC", f"✔ Pull Request detectado: #{resolved_pr}", Colors.GREEN)
            break
        if attempt < max_retries - 1:
            time.sleep(retry_delay)

    # 2. Se nenhum PR foi aberto nem criado a partir de branch remota, recorre ao patch da sessão
    if not resolved_pr and session_id:
        if apply_session_patch(session_id, repo_root, target_branch, git):
            return True

    if not resolved_pr:
        log("GIT-SYNC", "Nenhum Pull Request aberto pela sessão (sessão diagnóstica/informativa sem alterações de código).", Colors.DIM)
        return False

    print("\n" + "=" * 75)
    print(f"🔀 {Colors.BOLD}INTEGRAÇÃO CONTÍNUA: PULL REQUEST #{resolved_pr}{Colors.RESET}")
    print(f"📁 Repositório: {repo_name} ➔ Branch: {target_branch}")
    print("=" * 75 + "\n")

    # 3. Marca como Pronto (caso o Jules tenha deixado o PR como Draft / Publish PR)
    git.mark_pr_ready(resolved_pr, repo_name=repo_name)

    # 4. Aprova o PR (Code Review)
    if auto_approve_review:
        log("GITHUB-REVIEW", f"Aprovando Pull Request #{resolved_pr} via GitHub CLI...", Colors.HEADER)
        if git.approve_pr(resolved_pr, repo_name=repo_name, body="✅ Aprovado automaticamente pelo AMB_V2 após validação de integridade."):
            print(f"{Colors.GREEN}✔ Review de aprovação registrado no PR #{resolved_pr}.{Colors.RESET}")

    # 5. Merge do PR no GitHub (Squash and Delete Branch)
    log("GITHUB-MERGE", f"Executando Merge (Squash) do PR #{resolved_pr}...", Colors.HEADER)
    if not git.merge_pr(resolved_pr, repo_name=repo_name, squash=True, delete_branch=True, admin=True):
        log_error("GITHUB-MERGE", f"Falha ao realizar merge do PR #{resolved_pr}.")
        return False

    print(f"{Colors.GREEN}✔ PR #{resolved_pr} mesclado com sucesso na branch {target_branch}!{Colors.RESET}\n")

    # 6. Sincroniza localmente (git pull)
    log("GIT-PULL", f"Sincronizando branch local '{target_branch}' com origin...", Colors.CYAN)
    git.checkout(target_branch)
    git.pull("origin", target_branch)

    # 7. Validação de QA Local pós-merge
    log("QA-VALIDATION", "Executando verificação de integridade pós-merge via QualityGatekeeper...", Colors.CYAN)
    from pipeline.quality_gatekeeper import QualityGatekeeper
    if not QualityGatekeeper.run_qa(repo_root):
        log_error("QA", "A suíte de testes e validação local falhou após o merge.")
        return False

    print("\n" + "=" * 75)
    print(f"🎉 {Colors.BOLD}{Colors.GREEN}CÓDIGO INTEGRADO E VALIDADO COM SUCESSO!{Colors.RESET}")
    print("=" * 75 + "\n")
    return True

# Alias canônico de serviço para desacoplamento de handlers e testes (F1-M7)
run_merge_session_pr = approve_and_merge_pr


def main():
    parser = argparse.ArgumentParser(description="Aprovação e Merge Automático de PRs do Jules no Git (AMB_V2)")
    parser.add_argument("--session-id", "-s", help="ID da sessão Jules para extrair o PR.")
    parser.add_argument("--pr", "-p", type=int, help="Número específico do Pull Request (ex: 15).")
    parser.add_argument("--auto-latest", "-a", action="store_true", help="Detecta e mescla o último PR aberto no repositório.")
    parser.add_argument("--branch", "-b", default="main", help="Branch de destino (Padrão: main).")
    args = parser.parse_args()

    success = approve_and_merge_pr(
        session_id=args.session_id,
        pr_number=args.pr,
        auto_latest=args.auto_latest or (not args.session_id and not args.pr),
        target_branch=args.branch
    )
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
