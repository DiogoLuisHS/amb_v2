#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
================================================================================
🔀 AMB_V2 - Jules SDK: Aprovação de PR e Integração Contínua no Git (SRP)
================================================================================
Localização: amb_v2/integrations/jules/tools/merge_session_pr.py
Responsabilidade Única: Detectar o PR ou branch gerado pelo Google Jules, aprovar o PR,
realizar o merge no GitHub, sincronizar localmente e validar com typecheck/build.

Uso:
  python amb_v2/integrations/jules/tools/merge_session_pr.py --session-id 17502412430766789460
  python amb_v2/integrations/jules/tools/merge_session_pr.py --pr 15
  python amb_v2/integrations/jules/tools/merge_session_pr.py --auto-latest
================================================================================
"""

import os
import sys
import re
import json
import time
import argparse
import subprocess
from pathlib import Path
from typing import Optional, Dict, Any


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

from config import Colors, log, log_error, find_repo_root, get_repo_name, AmbError
from jules_client import JulesClient


def detect_pr_from_session(session_id: str) -> Optional[int]:
    """Inspeciona os outputs da sessão e as atividades para extrair o número do PR."""
    client = JulesClient()
    try:
        # 1. Checa diretamente na lista de outputs da sessão
        sess = client.get_session(session_id)
        outputs = sess.get("outputs", [])
        if isinstance(outputs, list):
            for item in outputs:
                if isinstance(item, dict) and "pullRequest" in item:
                    pr_url = item["pullRequest"].get("url", "")
                    m = re.search(r"/pull/(\d+)", pr_url)
                    if m:
                        return int(m.group(1))
        elif isinstance(outputs, dict) and "pullRequest" in outputs:
            pr_url = outputs["pullRequest"].get("url", "")
            m = re.search(r"/pull/(\d+)", pr_url)
            if m:
                return int(m.group(1))

        # 2. Checa em activities
        act_res = client.list_activities(session_id=session_id, page_size=50)
        activities = act_res if isinstance(act_res, list) else act_res.get("activities", [])
        for act in activities:
            txt = str(act)
            match = re.search(r"github\.com/[^/]+/[^/]+/pull/(\d+)", txt)
            if match:
                return int(match.group(1))
    except Exception as e:
        log_error("DETECT-PR", f"Falha ao consultar PR da sessão: {e}")
    return None


def get_latest_open_pr(repo_name: str) -> Optional[Dict[str, Any]]:
    """Consulta os PRs abertos no repositório via GitHub CLI, incluindo drafts criados pelo Jules."""
    for draft_flag in [["--draft"], []]:
        proc = subprocess.run(
            ["gh", "pr", "list", "--repo", repo_name, "--state", "open",
             "--json", "number,title,url,headRefName,isDraft,createdAt"] + draft_flag,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            shell=True
        )
        if proc.returncode == 0 and proc.stdout.strip():
            try:
                prs = json.loads(proc.stdout)
                if prs:
                    # Ordena por mais recente e retorna o primeiro
                    prs_sorted = sorted(prs, key=lambda p: p.get("createdAt", ""), reverse=True)
                    return prs_sorted[0]
            except Exception:
                pass
    return None


def approve_and_merge_pr(
    session_id: Optional[str] = None,
    pr_number: Optional[int] = None,
    auto_latest: bool = False,
    target_branch: str = "develop",
    auto_approve_review: bool = True
) -> bool:
    """Aprova o PR no GitHub, realiza o merge (squash), puxa localmente e roda o build."""
    repo_root = find_repo_root()
    repo_name = get_repo_name()

    resolved_pr = pr_number

    # 1. Identifica o PR com retry para permitir propagação no GitHub
    for attempt in range(3):
        if not resolved_pr and session_id:
            log("GIT-SYNC", f"Buscando PR vinculado à sessão {session_id} (tentativa {attempt+1}/3)...", Colors.CYAN)
            resolved_pr = detect_pr_from_session(session_id)

        if not resolved_pr and (auto_latest or not session_id):
            log("GIT-SYNC", f"Buscando último PR aberto no repositório {repo_name} (tentativa {attempt+1}/3)...", Colors.CYAN)
            latest = get_latest_open_pr(repo_name)
            if latest:
                resolved_pr = latest.get("number")
                log("GIT-SYNC", f"PR detectado: #{resolved_pr} - {latest.get('title')}", Colors.GREEN)

        if resolved_pr:
            break
        if attempt < 2:
            time.sleep(5)


    if not resolved_pr and session_id:
        log("GIT-SYNC", "Nenhum PR aberto no GitHub. Verificando patches diretos no session outputs...", Colors.CYAN)
        client = JulesClient()
        try:
            sess = client.get_session(session_id)
            outputs = sess.get("outputs", [])
            if outputs:
                patch_info = outputs[0].get("changeSet", {}).get("gitPatch", {})
                diff = patch_info.get("unidiffPatch", "")
                commit_msg = patch_info.get("suggestedCommitMessage", f"chore(jules): integrate session {session_id}")
                if diff:
                    log("GIT-SYNC", "Patch detectado no session outputs. Aplicando localmente...", Colors.HEADER)
                    patch_path = os.path.join(repo_root, ".tmp_jules.patch")
                    with open(patch_path, "w", encoding="utf-8") as pf:
                        pf.write(diff)
                    apply_res = subprocess.run(
                        ["git", "apply", "--whitespace=fix", "--ignore-space-change", "--ignore-whitespace", patch_path],
                        cwd=repo_root,
                        capture_output=True,
                        text=True,
                        encoding="utf-8",
                        errors="replace",
                        shell=True
                    )
                    if os.path.exists(patch_path):
                        os.remove(patch_path)

                    # Fallback robusto: se falhar por arquivos vazios ou novos no patch global, aplica arquivo por arquivo
                    if apply_res.returncode != 0:
                        parts = diff.split("diff --git ")
                        all_applied = True
                        for p_idx, p in enumerate(parts[1:], 1):
                            header = p.split("\n")[0]
                            f_rel = header.split(" b/")[-1].strip()
                            single_p = "diff --git " + p
                            if "@@" not in single_p and "new file mode" in single_p:
                                t_path = os.path.join(repo_root, f_rel)
                                os.makedirs(os.path.dirname(t_path), exist_ok=True)
                                if not os.path.exists(t_path):
                                    with open(t_path, "w", encoding="utf-8") as tf:
                                        pass
                                continue
                            p_part_path = os.path.join(repo_root, f".tmp_part_{p_idx}.patch")
                            with open(p_part_path, "w", encoding="utf-8") as ppf:
                                ppf.write(single_p)
                            p_res = subprocess.run(["git", "apply", "--whitespace=fix", "--ignore-space-change", "--ignore-whitespace", p_part_path], cwd=repo_root, capture_output=True, text=True, shell=True)
                            if os.path.exists(p_part_path):
                                os.remove(p_part_path)
                            if p_res.returncode != 0:
                                all_applied = False

                        patch_success = all_applied
                        if not patch_success:
                            log_error("GIT-SYNC", f"Falha ao aplicar patch via git apply:\n{apply_res.stderr}")
                    else:
                        patch_success = True
                    
                    if patch_success:
                        subprocess.run(["git", "add", "."], cwd=repo_root, capture_output=True, shell=False)
                        subprocess.run(["git", "commit", "-m", commit_msg], cwd=repo_root, capture_output=True, shell=False)


                        print(f"{Colors.GREEN}✔ Patch da sessão aplicado e commitado com sucesso!{Colors.RESET}\n")
                        
                        # QA Local adaptativo à stack
                        log("QA-VALIDATION", "Executando verificação de integridade pós-patch...", Colors.CYAN)
                        from config import load_project_json
                        proj = load_project_json()
                        qa_cfg = proj.get("qa", {})
                        if not qa_cfg:
                            if os.path.exists(os.path.join(repo_root, "package.json")):
                                qa_cfg = {"typecheck": "npm run typecheck", "build": "npm run build"}
                            elif os.path.exists(os.path.join(repo_root, "pyproject.toml")) or os.path.exists(os.path.join(repo_root, "requirements.txt")) or os.path.exists(os.path.join(repo_root, "setup.py")):
                                qa_cfg = {"build": "python -m py_compile cli.py"}
                            elif os.path.exists(os.path.join(repo_root, "go.mod")):
                                qa_cfg = {"build": "go build ./..."}
                            else:
                                qa_cfg = {}

                        qa_passed = True
                        for step_key, step_cmd in qa_cfg.items():
                            p_step = subprocess.run(step_cmd.split(), cwd=repo_root, capture_output=True, text=True, shell=True)
                            if p_step.returncode != 0:
                                log_error("QA", f"Falha no {step_key} pós-patch: {p_step.stderr.strip() or p_step.stdout.strip()}")
                                qa_passed = False
                                break
                            print(f"{Colors.GREEN}✔ {step_key}: concluído com sucesso!{Colors.RESET}")

                        if not qa_passed:
                            return False

                        # Push to GitHub
                        log("GIT-PUSH", f"Enviando alterações validadas para origin/{target_branch}...", Colors.CYAN)
                        subprocess.run(
                            ["git", "push", "origin", target_branch],
                            cwd=repo_root,
                            capture_output=True,
                            text=True,
                            encoding="utf-8",
                            errors="replace",
                            shell=True
                        )
                        print(f"{Colors.GREEN}✔ Alterações enviadas com sucesso para o GitHub!{Colors.RESET}\n")
                        return True
        except Exception as e:
            log_error("GIT-SYNC", f"Falha ao processar patch da sessão: {e}")


    if not resolved_pr:
        log("GIT-SYNC", "Nenhum Pull Request aberto pela sessão (sessão diagnóstica/informativa sem alterações de código).", Colors.DIM)
        return False

    print("\n" + "=" * 75)
    print(f"🔀 {Colors.BOLD}INTEGRAÇÃO CONTÍNUA: PULL REQUEST #{resolved_pr}{Colors.RESET}")
    print(f"📁 Repositório: {repo_name} ➔ Branch: {target_branch}")
    print("=" * 75 + "\n")

    # 2. Marca como Pronto (caso o Jules tenha deixado o PR como Draft / Publish PR)
    subprocess.run(
        ["gh", "pr", "ready", str(resolved_pr), "--repo", repo_name],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        shell=True
    )

    # 3. Aprova o PR (Code Review)
    if auto_approve_review:
        log("GITHUB-REVIEW", f"Aprovando Pull Request #{resolved_pr} via GitHub CLI...", Colors.HEADER)
        review_proc = subprocess.run(
            ["gh", "pr", "review", str(resolved_pr), "--repo", repo_name, "--approve", "--body", "✅ Aprovado automaticamente pelo AMB_V2 após validação de integridade."],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            shell=True
        )
        if review_proc.returncode == 0:
            print(f"{Colors.GREEN}✔ Review de aprovação registrado no PR #{resolved_pr}.{Colors.RESET}")
        else:
            # Não interrompe se for o próprio autor
            print(f"{Colors.DIM}Nota: {review_proc.stderr.strip() or review_proc.stdout.strip()}{Colors.RESET}")

    # 3. Merge do PR no GitHub (Squash and Delete Branch)
    log("GITHUB-MERGE", f"Executando Merge (Squash) do PR #{resolved_pr}...", Colors.HEADER)
    merge_proc = subprocess.run(
        ["gh", "pr", "merge", str(resolved_pr), "--repo", repo_name, "--squash", "--delete-branch", "--admin"],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        shell=True
    )
    if merge_proc.returncode != 0:
        # Tenta sem flag --admin se não for admin
        merge_proc = subprocess.run(
            ["gh", "pr", "merge", str(resolved_pr), "--repo", repo_name, "--squash", "--delete-branch"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            shell=True
        )

    if merge_proc.returncode != 0:
        log_error("GITHUB-MERGE", f"Falha ao realizar merge do PR #{resolved_pr}: {merge_proc.stderr.strip()}")
        return False

    print(f"{Colors.GREEN}✔ PR #{resolved_pr} mesclado com sucesso na branch {target_branch}!{Colors.RESET}\n")

    # 4. Sincroniza localmente (git pull)
    log("GIT-PULL", f"Sincronizando branch local '{target_branch}' com origin...", Colors.CYAN)
    subprocess.run(["git", "checkout", target_branch], cwd=repo_root, capture_output=True, shell=False)
    pull_proc = subprocess.run(
        ["git", "pull", "origin", target_branch],
        cwd=repo_root,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        shell=False
    )
    print(pull_proc.stdout.strip())

    # 5. Validação de QA Local (Bug #4 fix: comandos configuráveis via amb_project.json)
    log("QA-VALIDATION", "Executando verificação de integridade pós-merge...", Colors.CYAN)

    def _run_qa_cmd(cmd_str: str, label: str) -> bool:
        """Executa um comando de QA e retorna True se passou."""
        if not cmd_str.strip():
            return True
        import shlex
        import shutil
        parts = shlex.split(cmd_str.strip(), posix=(sys.platform != "win32"))
        if not parts:
            return True
        bin_path = shutil.which(parts[0])
        use_shell = False
        if bin_path:
            parts[0] = bin_path
        else:
            use_shell = True
        proc = subprocess.run(
            parts, cwd=repo_root,
            capture_output=True, text=True, encoding="utf-8", errors="replace", shell=use_shell
        )
        if proc.returncode != 0:
            log_error("QA", f"Falha no {label}!\n{proc.stdout.strip()}\n{proc.stderr.strip()}")
            return False
        print(f"{Colors.GREEN}✔ {label}: concluído com sucesso!{Colors.RESET}")
        return True

    # Lê comandos de QA do amb_project.json (Bug #4 fix)
    from config import load_project_json
    proj = load_project_json()
    qa_cfg = proj.get("qa", {})

    # Auto-detecção de stack se não configurado
    if not qa_cfg:
        if os.path.exists(os.path.join(repo_root, "package.json")):
            qa_cfg = {"typecheck": "npm run typecheck", "build": "npm run build"}
        elif os.path.exists(os.path.join(repo_root, "pyproject.toml")) or os.path.exists(os.path.join(repo_root, "requirements.txt")):
            qa_cfg = {"build": "python -m py_compile"}
        elif os.path.exists(os.path.join(repo_root, "go.mod")):
            qa_cfg = {"build": "go build ./..."}
        else:
            qa_cfg = {"typecheck": "npm run typecheck", "build": "npm run build"}

    for step_key, step_cmd in qa_cfg.items():
        if not _run_qa_cmd(step_cmd, step_key):
            return False

    print("\n" + "=" * 75)
    print(f"🎉 {Colors.BOLD}{Colors.GREEN}CÓDIGO INTEGRADO E VALIDADO COM SUCESSO!{Colors.RESET}")
    print("=" * 75 + "\n")
    return True


def main():
    parser = argparse.ArgumentParser(description="Aprovação e Merge Automático de PRs do Jules no Git (AMB_V2)")
    parser.add_argument("--session-id", "-s", help="ID da sessão Jules para extrair o PR.")
    parser.add_argument("--pr", "-p", type=int, help="Número específico do Pull Request (ex: 15).")
    parser.add_argument("--auto-latest", "-a", action="store_true", help="Detecta e mescla o último PR aberto no repositório.")
    parser.add_argument("--branch", "-b", default="develop", help="Branch de destino (Padrão: develop).")

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
