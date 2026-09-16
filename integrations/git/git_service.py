#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
⚡ AMB_V2 - Serviço Central de Abstração Git e GitHub CLI (F1-M4)
Localização: amb_v2/integrations/git/git_service.py
Responsabilidade Única: Prover interface única, testável e robusta para operações do Git
e da GitHub CLI (gh), isolando chamadas a subprocess e oferecendo validação fail-fast.
"""

import json
import os
import re
import shutil
import subprocess
from typing import Any, Dict, List, Optional

from config.bootstrap import ensure_amb_env
ensure_amb_env()

from config import ApiExecutionError, Colors, find_repo_root, get_repo_name, log, log_error


class GitService:
    """Abstração para comandos Git e GitHub CLI."""

    def __init__(self, repo_root: Optional[str] = None):
        self.repo_root = repo_root or find_repo_root()

    def _resolve_cwd(self, cwd: Optional[str] = None) -> str:
        return cwd or self.repo_root

    # ---------------------------------------------------------------------------
    # Operações Locais do Git
    # ---------------------------------------------------------------------------

    def get_current_branch(self, cwd: Optional[str] = None) -> str:
        """Obtém o nome da branch ativa do Git."""
        try:
            res = subprocess.run(
                ["git", "branch", "--show-current"],
                cwd=self._resolve_cwd(cwd),
                capture_output=True,
                text=True,
                check=False,
                encoding="utf-8",
                errors="replace",
            )
            if res.returncode == 0 and res.stdout.strip():
                return res.stdout.strip()
        except Exception:
            pass
        return "main"

    def get_remote_url(self, remote: str = "origin", cwd: Optional[str] = None) -> Optional[str]:
        """Obtém a URL configurada para o remote especificado."""
        try:
            res = subprocess.run(
                ["git", "remote", "get-url", remote],
                cwd=self._resolve_cwd(cwd),
                capture_output=True,
                text=True,
                timeout=5,
                check=False,
                encoding="utf-8",
                errors="replace",
            )
            if res.returncode == 0 and res.stdout.strip():
                return res.stdout.strip()
        except Exception:
            pass
        return None

    def detect_github_repo(self, cwd: Optional[str] = None) -> Optional[str]:
        """Identifica o owner/repo do repositório no GitHub via remote origin ou .git/config."""
        target_root = self._resolve_cwd(cwd)
        url = self.get_remote_url("origin", cwd=target_root)
        if url:
            match = re.search(r"github\.com[:/]([^/]+)/([^/.]+)", url)
            if match:
                return f"{match.group(1)}/{match.group(2)}"

        git_config = os.path.join(target_root, ".git", "config")
        if os.path.exists(git_config):
            try:
                with open(git_config, "r", encoding="utf-8", errors="replace") as f:
                    match = re.search(r"url\s*=\s*.*github\.com[:/]([^/]+)/([^/.]+)", f.read())
                    if match:
                        return f"{match.group(1)}/{match.group(2)}"
            except Exception:
                pass
        return None

    def get_log_oneline(self, count: int = 300, cwd: Optional[str] = None) -> str:
        """Obtém o histórico de commits compactado em uma linha por commit."""
        try:
            res = subprocess.run(
                ["git", "log", "--oneline", "-n", str(count)],
                cwd=self._resolve_cwd(cwd),
                capture_output=True,
                text=True,
                check=False,
                encoding="utf-8",
                errors="replace",
            )
            return res.stdout if res.returncode == 0 else ""
        except Exception:
            return ""

    def get_status(self, cwd: Optional[str] = None) -> str:
        """Retorna o output de git status --porcelain."""
        try:
            res = subprocess.run(
                ["git", "status", "--porcelain"],
                cwd=self._resolve_cwd(cwd),
                capture_output=True,
                text=True,
                check=False,
                encoding="utf-8",
                errors="replace",
            )
            return res.stdout.strip() if res.returncode == 0 else ""
        except Exception:
            return ""

    def is_clean(self, cwd: Optional[str] = None) -> bool:
        """Verifica se a working tree está limpa sem alterações não commitadas."""
        return len(self.get_status(cwd=cwd)) == 0

    def checkout(self, branch: str, create: bool = False, cwd: Optional[str] = None) -> bool:
        """Executa git checkout para alternar ou criar branches."""
        cmd = ["git", "checkout"]
        if create:
            cmd.append("-b")
        cmd.append(branch)
        res = subprocess.run(
            cmd,
            cwd=self._resolve_cwd(cwd),
            capture_output=True,
            text=True,
            check=False,
            encoding="utf-8",
            errors="replace",
        )
        return res.returncode == 0

    def pull(self, remote: str = "origin", branch: Optional[str] = None, cwd: Optional[str] = None) -> bool:
        """Executa git pull do remote e branch especificados."""
        cmd = ["git", "pull", remote]
        if branch:
            cmd.append(branch)
        res = subprocess.run(
            cmd,
            cwd=self._resolve_cwd(cwd),
            capture_output=True,
            text=True,
            check=False,
            encoding="utf-8",
            errors="replace",
        )
        return res.returncode == 0

    def apply_patch(self, patch_path: str, cwd: Optional[str] = None, whitespace_fix: bool = True) -> bool:
        """Aplica um arquivo de patch unificado via git apply."""
        cmd = ["git", "apply"]
        if whitespace_fix:
            cmd.extend(["--whitespace=fix", "--ignore-space-change", "--ignore-whitespace"])
        cmd.append(patch_path)
        res = subprocess.run(
            cmd,
            cwd=self._resolve_cwd(cwd),
            capture_output=True,
            text=True,
            check=False,
            encoding="utf-8",
            errors="replace",
        )
        return res.returncode == 0

    def add_all_and_commit(self, message: str, cwd: Optional[str] = None) -> bool:
        """Adiciona todos os arquivos modificados e realiza o commit."""
        target_cwd = self._resolve_cwd(cwd)
        subprocess.run(["git", "add", "."], cwd=target_cwd, capture_output=True, check=False)
        res = subprocess.run(
            ["git", "commit", "-m", message],
            cwd=target_cwd,
            capture_output=True,
            text=True,
            check=False,
            encoding="utf-8",
            errors="replace",
        )
        return res.returncode == 0

    def push(self, remote: str = "origin", branch: Optional[str] = None, cwd: Optional[str] = None) -> bool:
        """Envia alterações locais para o repositório remoto."""
        cmd = ["git", "push", remote]
        if branch:
            cmd.append(branch)
        res = subprocess.run(
            cmd,
            cwd=self._resolve_cwd(cwd),
            capture_output=True,
            text=True,
            check=False,
            encoding="utf-8",
            errors="replace",
        )
        return res.returncode == 0

    # ---------------------------------------------------------------------------
    # Operações do GitHub CLI (gh)
    # ---------------------------------------------------------------------------

    @staticmethod
    def is_gh_installed() -> bool:
        """Verifica se o binário gh está presente no PATH do sistema."""
        return shutil.which("gh") is not None

    def check_gh_auth(self) -> bool:
        """Verifica se a CLI gh está instalada e autenticada com sucesso."""
        if not self.is_gh_installed():
            raise ApiExecutionError(
                "GitHub CLI (gh) não encontrada no PATH.",
                hint="Instale a GitHub CLI (winget install GitHub.cli / brew install gh) para habilitar automações de PR.",
            )

        res = subprocess.run(
            ["gh", "auth", "status"],
            capture_output=True,
            text=True,
            check=False,
            encoding="utf-8",
            errors="replace",
        )
        if res.returncode != 0:
            raise ApiExecutionError(
                "GitHub CLI não autenticada.",
                hint="Execute 'gh auth login' no terminal para autenticar sua conta do GitHub.",
            )
        return True

    def list_open_prs(
        self, repo_name: Optional[str] = None, include_drafts: bool = True
    ) -> List[Dict[str, Any]]:
        """Lista Pull Requests abertos no repositório, incluindo drafts se solicitado."""
        target_repo = repo_name or get_repo_name()
        all_prs = []
        seen_numbers = set()

        draft_modes = [["--draft"], []] if include_drafts else [[]]

        for draft_args in draft_modes:
            cmd = [
                "gh",
                "pr",
                "list",
                "--repo",
                target_repo,
                "--state",
                "open",
                "--json",
                "number,title,url,headRefName,isDraft,createdAt",
            ] + draft_args

            res = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=False,
                encoding="utf-8",
                errors="replace",
            )
            if res.returncode == 0 and res.stdout.strip():
                try:
                    prs = json.loads(res.stdout)
                    for pr in prs:
                        num = pr.get("number")
                        if num and num not in seen_numbers:
                            seen_numbers.add(num)
                            all_prs.append(pr)
                except Exception:
                    pass

        return sorted(all_prs, key=lambda p: p.get("createdAt", ""), reverse=True)

    def get_latest_open_pr(self, repo_name: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Retorna o Pull Request aberto mais recente do repositório."""
        prs = self.list_open_prs(repo_name=repo_name, include_drafts=True)
        return prs[0] if prs else None

    def mark_pr_ready(self, pr_number: int, repo_name: Optional[str] = None) -> bool:
        """Remove o estado de Draft do PR transformando-o em Ready for Review."""
        target_repo = repo_name or get_repo_name()
        res = subprocess.run(
            ["gh", "pr", "ready", str(pr_number), "--repo", target_repo],
            capture_output=True,
            text=True,
            check=False,
            encoding="utf-8",
            errors="replace",
        )
        return res.returncode == 0

    def approve_pr(
        self,
        pr_number: int,
        repo_name: Optional[str] = None,
        body: str = "✅ Aprovado automaticamente pelo AMB_V2 após validação de integridade.",
    ) -> bool:
        """Aprova formalmente o Pull Request via gh pr review."""
        target_repo = repo_name or get_repo_name()
        res = subprocess.run(
            ["gh", "pr", "review", str(pr_number), "--repo", target_repo, "--approve", "--body", body],
            capture_output=True,
            text=True,
            check=False,
            encoding="utf-8",
            errors="replace",
        )
        return res.returncode == 0

    def merge_pr(
        self,
        pr_number: int,
        repo_name: Optional[str] = None,
        squash: bool = True,
        delete_branch: bool = True,
        admin: bool = True,
    ) -> bool:
        """Realiza o merge do Pull Request com squash e deleção de branch."""
        target_repo = repo_name or get_repo_name()
        base_cmd = ["gh", "pr", "merge", str(pr_number), "--repo", target_repo]
        if squash:
            base_cmd.append("--squash")
        if delete_branch:
            base_cmd.append("--delete-branch")

        # Tenta com --admin primeiro se solicitado
        if admin:
            admin_cmd = base_cmd + ["--admin"]
            res = subprocess.run(
                admin_cmd,
                capture_output=True,
                text=True,
                check=False,
                encoding="utf-8",
                errors="replace",
            )
            if res.returncode == 0:
                return True

        # Fallback para merge normal sem --admin
        res = subprocess.run(
            base_cmd,
            capture_output=True,
            text=True,
            check=False,
            encoding="utf-8",
            errors="replace",
        )
        return res.returncode == 0
