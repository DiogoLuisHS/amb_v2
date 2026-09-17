#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
⚡ AMB_V2 - Serviço Central de Abstração Git e GitHub CLI (F1-M4 - SRP)
Localização: amb_v2/integrations/git/git_service.py
Responsabilidade Única: Prover interface única, testável e robusta para operações do Git.
"""
import os
import re
import subprocess
from typing import Any, Dict, List, Optional, Tuple

from config.bootstrap import ensure_amb_env
ensure_amb_env()
from config import find_repo_root
from integrations.git.git_core.gh_cli import (
    is_gh_installed, check_gh_auth, list_open_prs, get_latest_open_pr,
    get_pr_legacy, create_pr_legacy, mark_pr_ready, approve_pr,
    merge_pr_legacy, close_pr
)

class GitService:
    def __init__(self, repo_root: Optional[str] = None):
        """  init   method."""
        self.repo_root = repo_root or find_repo_root()

    def _resolve_cwd(self, cwd: Optional[str] = None) -> str:
        """ resolve cwd method."""
        return cwd or self.repo_root

    def _run_git(self, cmd: List[str], cwd: Optional[str] = None, check: bool = False) -> subprocess.CompletedProcess:
        """ run git method."""
        return subprocess.run(cmd, cwd=self._resolve_cwd(cwd), capture_output=True, text=True, check=check, encoding="utf-8", errors="replace")

    def get_current_branch(self, cwd: Optional[str] = None) -> str:
        """Get current branch method."""
        res = self._run_git(["git", "branch", "--show-current"], cwd)
        return res.stdout.strip() if res.returncode == 0 and res.stdout.strip() else "main"

    def get_remote_url(self, remote: str = "origin", cwd: Optional[str] = None) -> Optional[str]:
        """Get remote url method."""
        res = self._run_git(["git", "remote", "get-url", remote], cwd)
        return res.stdout.strip() if res.returncode == 0 and res.stdout.strip() else None

    def detect_github_repo(self, cwd: Optional[str] = None) -> Optional[str]:
        """Detect github repo method."""
        target_root = self._resolve_cwd(cwd)
        url = self.get_remote_url("origin", target_root)
        if url:
            m = re.search(r"github\.com[:/]([^/]+)/([^/.]+)", url)
            if m: return f"{m.group(1)}/{m.group(2)}"
        try:
            with open(os.path.join(target_root, ".git", "config"), "r", encoding="utf-8", errors="replace") as f:
                m = re.search(r"url\s*=\s*.*github\.com[:/]([^/]+)/([^/.]+)", f.read())
                if m: return f"{m.group(1)}/{m.group(2)}"
        except: pass
        return None

    def get_log_oneline(self, count: int = 300, cwd: Optional[str] = None) -> str:
        """Get log oneline method."""
        return self._run_git(["git", "log", "--oneline", "-n", str(count)], cwd).stdout

    def get_status(self, cwd: Optional[str] = None) -> str:
        """Get status method."""
        res = self._run_git(["git", "status", "--porcelain"], cwd)
        return res.stdout.rstrip() if res.returncode == 0 else ""

    def get_status_porcelain(self, cwd: Optional[str] = None) -> str:
        """Get status porcelain method."""
        return self.get_status(cwd)

    def is_clean(self, cwd: Optional[str] = None) -> bool:
        """Is clean method."""
        return len(self.get_status(cwd).strip()) == 0

    def get_untracked_files(self, cwd: Optional[str] = None) -> List[str]:
        """Get untracked files method."""
        res = self._run_git(["git", "ls-files", "--others", "--exclude-standard"], cwd)
        return res.stdout.splitlines() if res.returncode == 0 else []

    def get_upstream_branch(self, cwd: Optional[str] = None) -> Optional[str]:
        """Get upstream branch method."""
        res = self._run_git(["git", "rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{u}"], cwd)
        return res.stdout.strip() if res.returncode == 0 and res.stdout.strip() else None

    def get_ahead_behind(self, cwd: Optional[str] = None) -> Tuple[int, int]:
        """Get ahead behind method."""
        res = self._run_git(["git", "rev-list", "--left-right", "--count", "HEAD...@{u}"], cwd)
        if res.returncode == 0 and res.stdout.strip():
            p = res.stdout.strip().split()
            if len(p) == 2: return int(p[0]), int(p[1])
        return 0, 0

    def get_detailed_status(self, cwd: Optional[str] = None) -> Dict[str, Any]:
        """Get detailed status method."""
        target_cwd = self._resolve_cwd(cwd)
        raw = self.get_status(target_cwd)
        staged, unstaged, untracked = [], [], []
        for line in raw.splitlines():
            if len(line) < 3: continue
            x, y, fname = line[0], line[1], line[3:].strip()
            if x == "?": untracked.append(fname)
            else:
                if x != " ": staged.append(f"{x} {fname}")
                if y != " ": unstaged.append(f"{y} {fname}")
        return {
            "branch": self.get_current_branch(target_cwd),
            "upstream": self.get_upstream_branch(target_cwd),
            "ahead": self.get_ahead_behind(target_cwd)[0],
            "behind": self.get_ahead_behind(target_cwd)[1],
            "is_clean": len(raw) == 0,
            "staged": staged, "unstaged": unstaged, "untracked": untracked,
            "repo_root": target_cwd,
            "github_repo": self.detect_github_repo(target_cwd)
        }

    def checkout(self, branch: str, create: bool = False, cwd: Optional[str] = None) -> bool:
        """Checkout method."""
        cmd = ["git", "checkout", "-b", branch] if create else ["git", "checkout", branch]
        return self._run_git(cmd, cwd).returncode == 0

    def checkout_branch(self, branch: str, cwd: Optional[str] = None) -> bool:
        """Checkout branch method."""
        return self.checkout(branch, create=False, cwd=cwd)

    def create_and_checkout_branch(self, branch: str, cwd: Optional[str] = None) -> bool:
        """Create and checkout branch method."""
        return self.checkout(branch, create=True, cwd=cwd)

    def pull(self, remote: str = "origin", branch: Optional[str] = None, cwd: Optional[str] = None) -> bool:
        """Pull method."""
        cmd = ["git", "pull", remote]
        if branch: cmd.append(branch)
        return self._run_git(cmd, cwd).returncode == 0

    def fetch(self, remote: str = "origin", prune: bool = True, cwd: Optional[str] = None) -> bool:
        """Fetch method."""
        cmd = ["git", "fetch", remote]
        if prune: cmd.append("--prune")
        return self._run_git(cmd, cwd).returncode == 0

    def sync_with_remote(self, remote: str = "origin", branch: Optional[str] = None, cwd: Optional[str] = None) -> bool:
        """Sync with remote method."""
        return self.fetch(remote, True, cwd) and self.pull(remote, branch, cwd)

    def stash(self, action: str = "push", message: Optional[str] = None, cwd: Optional[str] = None) -> bool:
        """Stash method."""
        cmd = ["git", "stash", action]
        if action == "push" and message: cmd.extend(["-m", message])
        return self._run_git(cmd, cwd).returncode == 0

    def get_diff(self, file_path: Optional[str] = None, base_branch: Optional[str] = None, cached: bool = False, cwd: Optional[str] = None) -> str:
        """Get diff method."""
        cmd = ["git", "diff"]
        if cached: cmd.append("--cached")
        if base_branch: cmd.append(base_branch)
        if file_path: cmd.extend(["--", file_path])
        res = self._run_git(cmd, cwd)
        return res.stdout if res.returncode == 0 else ""

    def get_diff_summary(self, cwd: Optional[str] = None) -> str:
        """Get diff summary method."""
        res = self._run_git(["git", "diff", "--stat"], cwd)
        return res.stdout if res.returncode == 0 else ""

    def create_branch(self, branch_name: str, from_branch: Optional[str] = None, checkout: bool = True, cwd: Optional[str] = None) -> bool:
        """Create branch method."""
        cmd = ["git", "checkout", "-b", branch_name] if checkout else ["git", "branch", branch_name]
        if from_branch: cmd.append(from_branch)
        return self._run_git(cmd, cwd).returncode == 0

    def apply_patch(self, patch_path: str, cwd: Optional[str] = None, whitespace_fix: bool = True) -> bool:
        """Apply patch method."""
        cmd = ["git", "apply"]
        if whitespace_fix: cmd.extend(["--whitespace=fix", "--ignore-space-change", "--ignore-whitespace"])
        cmd.append(patch_path)
        return self._run_git(cmd, cwd).returncode == 0

    def add_all_and_commit(self, message: str, cwd: Optional[str] = None) -> bool:
        """Add all and commit method."""
        self._run_git(["git", "add", "."], cwd)
        return self._run_git(["git", "commit", "-m", message], cwd).returncode == 0

    def add_and_commit(self, message: str, cwd: Optional[str] = None) -> bool:
        """Add and commit method."""
        return self.add_all_and_commit(message, cwd)

    def push(self, remote: str = "origin", branch: Optional[str] = None, cwd: Optional[str] = None) -> bool:
        """Push method."""
        cmd = ["git", "push", remote]
        if branch: cmd.append(branch)
        return self._run_git(cmd, cwd).returncode == 0

    def create_tag(self, tag: str, message: Optional[str] = None, cwd: Optional[str] = None) -> bool:
        """Create tag method."""
        cmd = ["git", "tag", tag]
        if message: cmd.extend(["-m", message])
        return self._run_git(cmd, cwd).returncode == 0

    def reset_hard(self, ref: str = "HEAD", cwd: Optional[str] = None) -> bool:
        """Reset hard method."""
        return self._run_git(["git", "reset", "--hard", ref], cwd).returncode == 0

    @staticmethod
    def is_gh_installed() -> bool:
        return is_gh_installed()

    def check_gh_auth(self, cwd: Optional[str] = None, fail_silently: bool = False) -> bool:
        """Check gh auth method."""
        return check_gh_auth(cwd=self._resolve_cwd(cwd), fail_silently=fail_silently)

    def list_open_prs(self, repo_name: Optional[str] = None, include_drafts: bool = True) -> List[Dict[str, Any]]:
        """List open prs method."""
        return list_open_prs(repo_name, include_drafts)

    def get_latest_open_pr(self, repo_name: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Get latest open pr method."""
        return get_latest_open_pr(repo_name)

    def get_pr(self, pr_number: int, repo_name: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Get pr method."""
        return get_pr_legacy(pr_number, repo_name)

    def create_pr(self, title: str, body: str, base: Optional[str] = None, head: Optional[str] = None, draft: bool = False, repo_name: Optional[str] = None) -> Dict[str, Any]:
        """Create pr method."""
        return create_pr_legacy(title, body, base, head, draft, repo_name, cwd=self.repo_root)

    def mark_pr_ready(self, pr_number: int, repo_name: Optional[str] = None) -> bool:
        """Mark pr ready method."""
        return mark_pr_ready(pr_number, repo_name)

    def approve_pr(self, pr_number: int, repo_name: Optional[str] = None, body: str = "✅ Aprovado automaticamente pelo AMB_V2 após validação de integridade.") -> bool:
        """Approve pr method."""
        return approve_pr(pr_number, repo_name, body)

    def merge_pr(self, pr_number: int, repo_name: Optional[str] = None, squash: bool = True, delete_branch: bool = True, admin: bool = True) -> bool:
        """Merge pr method."""
        return merge_pr_legacy(pr_number, repo_name, squash, delete_branch, admin)

    def close_pr(self, pr_number: int, comment: Optional[str] = None, delete_branch: bool = False, repo_name: Optional[str] = None) -> bool:
        """Close pr method."""
        return close_pr(pr_number, comment, delete_branch, repo_name)
