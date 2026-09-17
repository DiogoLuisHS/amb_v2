"""GitHub CLI Operations."""
import json
import os
import re
import shutil
import subprocess
from typing import Any, Dict, List, Optional, Tuple
from config import ApiExecutionError, get_repo_name, find_repo_root

def _run_gh(cmd: List[str], cwd: Optional[str] = None) -> subprocess.CompletedProcess:
    return subprocess.run(
        cmd,
        cwd=cwd or find_repo_root(),
        capture_output=True,
        text=True,
        check=False,
        encoding="utf-8",
        errors="replace",
    )

def is_gh_installed() -> bool:
    return shutil.which("gh") is not None

def check_gh_auth(cwd: Optional[str] = None, fail_silently: bool = False) -> bool:
    if not is_gh_installed():
        if fail_silently:
            return False
        raise ApiExecutionError("GitHub CLI (gh) não encontrada no PATH.")
    res = _run_gh(["gh", "auth", "status"], cwd=cwd)
    if res.returncode != 0:
        if fail_silently:
            return False
        raise ApiExecutionError("GitHub CLI não autenticada.")
    return True

def list_prs(state: str = "open", limit: int = 30, cwd: Optional[str] = None) -> List[Dict[str, Any]]:
    res = _run_gh([
        "gh", "pr", "list", "--state", state, "--limit", str(limit),
        "--json", "number,title,url,headRefName,isDraft,createdAt"
    ], cwd=cwd)
    if res.returncode == 0 and res.stdout.strip():
        try:
            return json.loads(res.stdout)
        except Exception:
            pass
    return []

def get_pr_details(pr_number: int, cwd: Optional[str] = None) -> Dict[str, Any]:
    res = _run_gh([
        "gh", "pr", "view", str(pr_number),
        "--json", "number,title,body,state,url,headRefName,baseRefName,isDraft,mergeable,author,createdAt,updatedAt"
    ], cwd=cwd)
    if res.returncode == 0 and res.stdout.strip():
        try:
            return json.loads(res.stdout)
        except Exception:
            pass
    return {}

def create_pr(title: str, body: str, base: str = "main", head: Optional[str] = None, draft: bool = False, cwd: Optional[str] = None) -> Dict[str, Any]:
    cmd = ["gh", "pr", "create", "--title", title, "--body", body, "--base", base]
    if head:
        cmd.extend(["--head", head])
    if draft:
        cmd.append("--draft")
    res = _run_gh(cmd, cwd=cwd)
    if res.returncode != 0:
        raise ApiExecutionError(f"Falha ao criar PR: {res.stderr.strip() or res.stdout.strip()}")
    pr_url = res.stdout.strip()
    match = re.search(r"/pull/(\d+)", pr_url)
    return {
        "success": True,
        "url": pr_url,
        "number": int(match.group(1)) if match else None,
        "title": title,
        "draft": draft,
    }

def merge_pr(pr_number: int, method: str = "squash", delete_branch: bool = True, cwd: Optional[str] = None) -> bool:
    cmd = ["gh", "pr", "merge", str(pr_number)]
    if method:
        cmd.append(f"--{method}")
    if delete_branch:
        cmd.append("--delete-branch")
    res = _run_gh(cmd, cwd=cwd)
    return res.returncode == 0

def get_pr_checks(pr_number: int, cwd: Optional[str] = None) -> Dict[str, Any]:
    res = _run_gh(["gh", "pr", "checks", str(pr_number), "--json", "name,state,bucket,description,link"], cwd=cwd)
    if res.returncode == 0 and res.stdout.strip():
        try:
            return json.loads(res.stdout)
        except Exception:
            pass
    return {}

def create_release(tag: str, title: str, notes: str, draft: bool = False, cwd: Optional[str] = None) -> str:
    cmd = ["gh", "release", "create", tag, "--title", title, "--notes", notes]
    if draft:
        cmd.append("--draft")
    res = _run_gh(cmd, cwd=cwd)
    if res.returncode != 0:
        raise ApiExecutionError(f"Falha ao criar release: {res.stderr.strip() or res.stdout.strip()}")
    return res.stdout.strip()

# Legacy methods mapping to old GitService signatures
def list_open_prs(repo_name: Optional[str] = None, include_drafts: bool = True) -> List[Dict[str, Any]]:
    target_repo = repo_name or get_repo_name()
    all_prs = []
    seen = set()
    draft_modes = [["--draft"], []] if include_drafts else [[]]
    for draft_args in draft_modes:
        cmd = ["gh", "pr", "list", "--repo", target_repo, "--state", "open", "--json", "number,title,url,headRefName,isDraft,createdAt"] + draft_args
        res = _run_gh(cmd)
        if res.returncode == 0 and res.stdout.strip():
            try:
                prs = json.loads(res.stdout)
                for pr in prs:
                    num = pr.get("number")
                    if num and num not in seen:
                        seen.add(num)
                        all_prs.append(pr)
            except Exception:
                pass
    return sorted(all_prs, key=lambda p: p.get("createdAt", ""), reverse=True)

def get_latest_open_pr(repo_name: Optional[str] = None) -> Optional[Dict[str, Any]]:
    prs = list_open_prs(repo_name=repo_name, include_drafts=True)
    return prs[0] if prs else None

def get_pr_legacy(pr_number: int, repo_name: Optional[str] = None) -> Optional[Dict[str, Any]]:
    target_repo = repo_name or get_repo_name()
    res = _run_gh(["gh", "pr", "view", str(pr_number), "--repo", target_repo, "--json", "number,title,body,state,url,headRefName,baseRefName,isDraft,mergeable,author,createdAt,updatedAt"])
    if res.returncode == 0 and res.stdout.strip():
        try:
            return json.loads(res.stdout)
        except Exception:
            pass
    return None

def create_pr_legacy(title: str, body: str, base: Optional[str] = None, head: Optional[str] = None, draft: bool = False, repo_name: Optional[str] = None, cwd: Optional[str] = None) -> Dict[str, Any]:
    target_repo = repo_name or get_repo_name()
    cmd = ["gh", "pr", "create", "--repo", target_repo, "--title", title, "--body", body]
    if base:
        cmd.extend(["--base", base])
    if head:
        cmd.extend(["--head", head])
    if draft:
        cmd.append("--draft")
    res = _run_gh(cmd, cwd=cwd)
    if res.returncode != 0:
        raise ApiExecutionError(f"Falha ao criar PR: {res.stderr.strip() or res.stdout.strip()}")
    pr_url = res.stdout.strip()
    match = re.search(r"/pull/(\d+)", pr_url)
    return {
        "success": True,
        "url": pr_url,
        "number": int(match.group(1)) if match else None,
        "title": title,
        "draft": draft,
    }

def mark_pr_ready(pr_number: int, repo_name: Optional[str] = None) -> bool:
    target_repo = repo_name or get_repo_name()
    res = _run_gh(["gh", "pr", "ready", str(pr_number), "--repo", target_repo])
    return res.returncode == 0

def approve_pr(pr_number: int, repo_name: Optional[str] = None, body: str = "✅ Aprovado automaticamente pelo AMB_V2 após validação de integridade.") -> bool:
    target_repo = repo_name or get_repo_name()
    res = _run_gh(["gh", "pr", "review", str(pr_number), "--repo", target_repo, "--approve", "--body", body])
    return res.returncode == 0

def merge_pr_legacy(pr_number: int, repo_name: Optional[str] = None, squash: bool = True, delete_branch: bool = True, admin: bool = True) -> bool:
    target_repo = repo_name or get_repo_name()
    base_cmd = ["gh", "pr", "merge", str(pr_number), "--repo", target_repo]
    if squash:
        base_cmd.append("--squash")
    if delete_branch:
        base_cmd.append("--delete-branch")

    if admin:
        admin_cmd = base_cmd + ["--admin"]
        res = _run_gh(admin_cmd)
        if res.returncode == 0:
            return True

    res = _run_gh(base_cmd)
    return res.returncode == 0

def close_pr(pr_number: int, comment: Optional[str] = None, delete_branch: bool = False, repo_name: Optional[str] = None) -> bool:
    target_repo = repo_name or get_repo_name()
    cmd = ["gh", "pr", "close", str(pr_number), "--repo", target_repo]
    if comment:
        cmd.extend(["--comment", comment])
    if delete_branch:
        cmd.append("--delete-branch")
    res = _run_gh(cmd)
    return res.returncode == 0
