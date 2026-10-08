#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
📋 AMB_V2 - Sincronizador de Prompts com GitHub Issues (SRP)
Localização: amb_cli/workspace/issue_synchronizer.py
Responsabilidade Única: Mapeamento idempotente entre arquivos de prompts (.md)
e GitHub Issues, garantindo fila sequencial e rastreabilidade ponta a ponta.
"""

from pathlib import Path
import re
from typing import Any, Dict, List, Optional, TypedDict, Union

from core import Colors, log_error
from core.bootstrap import ensure_amb_env
from workspace.project_context import find_repo_root

ensure_amb_env()


class PromptSyncItem(TypedDict):
    """Estrutura determinística do item de fila sincronizado."""
    issue_number: int
    url: str
    title: str
    file_name: str
    path: Optional[Path]
    content: str
    is_new: bool


def natural_sort_key(p: Path) -> List[Union[int, str]]:
    """Chave para ordenação natural de arquivos numéricos (ex: 1, 2, 10)."""
    return [
        int(text) if text.isdigit() else text.lower()
        for text in re.split(r"(\d+)", p.name)
    ]


class IssueSynchronizer:
    """Sincronizador idempotente de prompts com o GitHub Issues."""

    DEFAULT_LABEL = "amb:prompt"

    def __init__(
        self,
        repo_root: Optional[Union[str, Path]] = None,
        git_service: Optional[Any] = None,
    ) -> None:
        self.repo_root = Path(repo_root or find_repo_root())
        self._git = git_service

    @property
    def git(self) -> Any:
        """Obtém instância do GitService de forma desacoplada."""
        if self._git is None:
            from integrations.git.git_service import GitService
            self._git = GitService(repo_root=str(self.repo_root))
        return self._git

    @git.setter
    def git(self, value: Any) -> None:
        self._git = value

    @staticmethod
    def make_prompt_marker(file_name: str) -> str:
        """Gera marcador HTML invisível para identificação idempotente."""
        return f"<!-- amb:prompt: {file_name} -->"

    @staticmethod
    def extract_prompt_title(file_path: Path, content: str) -> str:
        """Extrai o título do primeiro cabeçalho Markdown (# ...) ou usa o nome do arquivo."""
        for line in content.splitlines():
            stripped = line.strip()
            if stripped.startswith("# "):
                title = stripped.lstrip("#").strip()
                if title:
                    return title
        cleaned = file_path.stem.replace("_", " ").replace("-", " ")
        return cleaned.title()

    def find_matching_issue(
        self, open_issues: List[Dict[str, Any]], file_name: str
    ) -> Optional[Dict[str, Any]]:
        """Verifica se já existe uma issue aberta vinculada a este arquivo de prompt."""
        marker = self.make_prompt_marker(file_name)
        for issue in open_issues:
            body = issue.get("body") or ""
            if marker in body:
                return issue
        return None

    def discover_prompt_files(self, prompts_target: Union[str, Path]) -> List[Path]:
        """Localiza e ordena deterministamente os arquivos .md a processar."""
        target = Path(prompts_target)
        if not target.is_absolute():
            target = self.repo_root / target

        if not target.exists():
            log_error("SYNC", f"Caminho de prompts '{prompts_target}' não encontrado.")
            return []

        if target.is_file():
            return [target]

        files = [
            f
            for f in target.glob("*.md")
            if f.name.lower() != "readme.md" and not f.name.startswith(("_", "."))
        ]
        return sorted(files, key=natural_sort_key)

    @staticmethod
    def _create_item(
        issue_number: int,
        url: str,
        title: str,
        file_name: str,
        path: Optional[Path],
        content: str,
        is_new: bool,
    ) -> PromptSyncItem:
        """Fábrica privada para padronização de registros na fila."""
        return {
            "issue_number": issue_number,
            "url": url,
            "title": title,
            "file_name": file_name,
            "path": path,
            "content": content,
            "is_new": is_new,
        }

    def sync_prompts(
        self,
        prompts_target: Union[str, Path],
        labels: Optional[List[str]] = None,
        dry_run: bool = False,
    ) -> List[PromptSyncItem]:
        """Sincroniza arquivos de prompts com o GitHub Issues de forma idempotente."""
        files = self.discover_prompt_files(prompts_target)
        if not files:
            return []

        active_labels = labels or [self.DEFAULT_LABEL]
        open_issues: List[Dict[str, Any]] = []

        try:
            open_issues = self.git.list_issues(state="open")
        except Exception as e:
            log_error("SYNC", f"Aviso ao consultar issues existentes: {e}")

        queue: List[PromptSyncItem] = []

        for f in files:
            content = f.read_text(encoding="utf-8", errors="replace")
            title = self.extract_prompt_title(f, content)
            existing = self.find_matching_issue(open_issues, f.name)

            if existing:
                queue.append(
                    self._create_item(
                        issue_number=int(existing["number"]),
                        url=existing.get("url", ""),
                        title=existing.get("title", title),
                        file_name=f.name,
                        path=f,
                        content=content,
                        is_new=False,
                    )
                )
                continue

            if dry_run:
                queue.append(
                    self._create_item(
                        issue_number=0,
                        url="https://github.com/dry-run",
                        title=title,
                        file_name=f.name,
                        path=f,
                        content=content,
                        is_new=True,
                    )
                )
                continue

            marker = self.make_prompt_marker(f.name)
            body = f"{content}\n\n---\n{marker}\n*Sincronizado automaticamente pelo AMB_V2.*"

            try:
                res = self.git.create_issue(title=title, body=body, labels=active_labels)
                queue.append(
                    self._create_item(
                        issue_number=int(res.get("number") or 0),
                        url=res.get("url", ""),
                        title=title,
                        file_name=f.name,
                        path=f,
                        content=content,
                        is_new=True,
                    )
                )
            except Exception as e:
                log_error("SYNC", f"Falha ao criar issue para '{f.name}': {e}")
                queue.append(
                    self._create_item(
                        issue_number=0,
                        url="",
                        title=title,
                        file_name=f.name,
                        path=f,
                        content=content,
                        is_new=False,
                    )
                )

        return queue

    def list_open_issue_queue(
        self, label: Optional[str] = None
    ) -> List[PromptSyncItem]:
        """Recupera a fila de execução diretamente das issues abertas no GitHub."""
        target_label = label or self.DEFAULT_LABEL
        issues = self.git.list_issues(state="open", labels=[target_label])
        queue: List[PromptSyncItem] = []

        for iss in issues:
            queue.append(
                self._create_item(
                    issue_number=int(iss.get("number") or 0),
                    url=iss.get("url", ""),
                    title=iss.get("title", ""),
                    file_name=f"issue_{iss.get('number')}.md",
                    path=None,
                    content=iss.get("body", ""),
                    is_new=False,
                )
            )

        return sorted(queue, key=lambda x: x["issue_number"])

    def close_issue(
        self, issue_number: int, comment: Optional[str] = None
    ) -> bool:
        """Fecha uma issue no GitHub com comentário opcional."""
        if issue_number <= 0:
            return False
        return self.git.close_issue(issue_number=issue_number, comment=comment)

    def resolve_items_queue(
        self,
        prompt_target: Optional[Union[str, Path]] = None,
        use_issues: bool = False,
    ) -> List[Dict[str, Any]]:
        """Resolve a fila unificada de execução para prompts locais ou issues do GitHub."""
        if use_issues:
            queue_source = self.sync_prompts(prompt_target) if prompt_target else self.list_open_issue_queue()
            if prompt_target:
                print(f"\n{Colors.BOLD}{Colors.CYAN}📋 SINCRONIZANDO PROMPTS COM GITHUB ISSUES...{Colors.RESET}")
                for s in queue_source:
                    status_tag = f"{Colors.GREEN}[Criada]#{s['issue_number']}{Colors.RESET}" if s.get("is_new") else f"{Colors.YELLOW}[Reaproveitada]#{s['issue_number']}{Colors.RESET}"
                    print(f"  ✔ {status_tag} {s['title']} ({s['file_name']})")
            return [
                {
                    "type": "issue",
                    "name": f"Issue #{s['issue_number']}: {s['title']}",
                    "issue_number": s["issue_number"],
                    "url": s.get("url", ""),
                    "title": s["title"],
                    "path": s.get("path"),
                    "content": s["content"],
                    "file_name": s["file_name"],
                }
                for s in queue_source
            ]

        if prompt_target:
            files = self.discover_prompt_files(prompt_target)
            return [
                {
                    "type": "prompt",
                    "name": f.stem,
                    "title": f.stem.replace("_", " ").title(),
                    "path": f,
                    "file_name": f.name,
                    "content": f.read_text(encoding="utf-8", errors="replace"),
                }
                for f in files
            ]

        return []
