#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🧠 AMB_V2 - RulesManager Centralizado (F1-M6 - SRP)
Localização: amb_v2/config/rules_manager.py
Responsabilidade Única: Descobrir, ler, sanitizar, fechar fences markdown e gerenciar
em cache as diretrizes arquiteturais e regras operacionais do repositório ativo,
sem qualquer premissa tecnológica a priori.
"""

import os
import re
from typing import List, Dict, Any, Optional

from config.bootstrap import ensure_amb_env
ensure_amb_env()

from config import find_repo_root, log, Colors


class RulesManager:
    """Gerenciador central de regras arquiteturais do repositório."""

    _instance: Optional["RulesManager"] = None
    _cached_rules_by_dir: Dict[str, str] = {}
    _cached_list_by_dir: Dict[str, List[Dict[str, Any]]] = {}

    def __init__(self, custom_rules_dir: Optional[str] = None) -> None:
        self.custom_rules_dir = custom_rules_dir

    @classmethod
    def get_instance(cls, custom_rules_dir: Optional[str] = None) -> "RulesManager":
        """Retorna instância singleton do RulesManager com cache central."""
        if cls._instance is None or custom_rules_dir is not None:
            cls._instance = cls(custom_rules_dir=custom_rules_dir)
        return cls._instance

    @classmethod
    def invalidate_cache(cls) -> None:
        """Limpa o cache em memória para forçar releitura do disco."""
        cls._cached_rules_by_dir.clear()
        cls._cached_list_by_dir.clear()

    def resolve_rules_dir(self, custom_dir: Optional[str] = None, root: Optional[str] = None) -> Optional[str]:
        """
        Determina o diretório de regras ativo seguindo a ordem de prioridade:
        1. Diretório informado explicitamente (parâmetro ou construtor).
        2. .antigravity/rules/
        3. .gemini/rules/
        4. .agents/rules/ ou rules/
        5. Diretório raiz se contiver AGENTS.md ou GEMINI.md
        """
        target_dir = custom_dir or self.custom_rules_dir
        if target_dir and os.path.exists(target_dir):
            return os.path.abspath(target_dir)

        repo_root = root or find_repo_root()
        candidates = [
            os.path.join(repo_root, ".antigravity", "rules"),
            os.path.join(repo_root, ".gemini", "rules"),
            os.path.join(repo_root, ".agents", "rules"),
            os.path.join(repo_root, "rules"),
        ]

        for cand in candidates:
            if os.path.exists(cand) and os.path.isdir(cand):
                return os.path.abspath(cand)

        # Checa se existem arquivos avulsos de regras na raiz
        for single_file in ["AGENTS.md", "GEMINI.md"]:
            if os.path.exists(os.path.join(repo_root, single_file)):
                return os.path.abspath(repo_root)

        return None

    def list_rules(self, rules_dir: Optional[str] = None, root: Optional[str] = None) -> List[Dict[str, Any]]:
        """Lista todos os arquivos de regras descobertos com metadados básicos."""
        resolved = self.resolve_rules_dir(custom_dir=rules_dir, root=root)
        if not resolved or not os.path.exists(resolved):
            return []

        if resolved in self._cached_list_by_dir:
            return self._cached_list_by_dir[resolved]

        rules: List[Dict[str, Any]] = []

        if os.path.isdir(resolved):
            for fname in sorted(os.listdir(resolved)):
                if not fname.endswith(".md") or fname.startswith("_"):
                    continue
                fpath = os.path.join(resolved, fname)
                if not os.path.isfile(fpath):
                    continue
                size = os.path.getsize(fpath)
                snippet = ""
                try:
                    with open(fpath, "r", encoding="utf-8", errors="replace") as f:
                        lines = [line.strip() for line in f if line.strip() and not line.startswith("#")]
                        snippet = lines[0][:100] if lines else ""
                except Exception:
                    pass

                rules.append({
                    "name": fname,
                    "path": fpath,
                    "size_bytes": size,
                    "summary": snippet
                })
        else:
            # Caso especial: caminho direto para um arquivo específico
            rules.append({
                "name": os.path.basename(resolved),
                "path": resolved,
                "size_bytes": os.path.getsize(resolved),
                "summary": "Arquivo de regras direto."
            })

        self._cached_list_by_dir[resolved] = rules
        return rules

    @staticmethod
    def clean_markdown_snippet(text: str, max_chars: int = 3000) -> str:
        """
        Sanitiza o conteúdo markdown removendo frontmatter YAML, comentários HTML
        e garantindo que blocos de código (fences ```) fiquem fechados se truncados.
        """
        if not text:
            return ""

        # Remove frontmatter YAML (--- ... ---) no início do arquivo
        cleaned = re.sub(r"^---\s*\n.*?\n---\s*\n", "", text, flags=re.DOTALL)

        # Remove comentários HTML
        cleaned = re.sub(r"<!--.*?-->", "", cleaned, flags=re.DOTALL)

        # Trunca se exceder max_chars
        if len(cleaned) > max_chars:
            truncated = cleaned[:max_chars].rstrip()
            # Garante que blocos de código abertos com ``` sejam fechados
            code_fence_count = truncated.count("```")
            if code_fence_count % 2 != 0:
                truncated += "\n```"
            cleaned = truncated + "\n... [regras truncadas para concisão]"

        return cleaned.strip()

    def load_rules(
        self,
        rules_dir: Optional[str] = None,
        max_chars: int = 8000,
        root: Optional[str] = None
    ) -> str:
        """
        Carrega, sanitiza e consolida todas as regras arquiteturais ativas.
        Retorna string formatada para injeção direta em prompts de IA.
        """
        resolved = self.resolve_rules_dir(custom_dir=rules_dir, root=root)
        if not resolved or not os.path.exists(resolved):
            return ""

        cache_key = f"{resolved}_{max_chars}"
        if cache_key in self._cached_rules_by_dir:
            return self._cached_rules_by_dir[cache_key]

        rule_files = self.list_rules(rules_dir=resolved, root=root)
        if not rule_files:
            return ""

        extracted_rules: List[str] = []
        per_file_budget = max(500, max_chars // len(rule_files)) if rule_files else max_chars

        for rf in rule_files:
            fpath = rf["path"]
            fname = rf["name"]
            try:
                with open(fpath, "r", encoding="utf-8", errors="replace") as f:
                    content = f.read()
                cleaned = self.clean_markdown_snippet(content, max_chars=per_file_budget)
                if cleaned:
                    extracted_rules.append(f"### 📋 Regra: {fname}\n{cleaned}")
            except Exception as e:
                log("RULES", f"Aviso: falha ao ler regra {fname}: {e}", Colors.YELLOW)

        combined = "\n\n".join(extracted_rules).strip()
        if len(combined) > max_chars:
            combined = self.clean_markdown_snippet(combined, max_chars=max_chars)

        self._cached_rules_by_dir[cache_key] = combined
        return combined

    def filter_rules_for_agent(
        self,
        rules_text: Optional[str] = None,
        role: Optional[str] = None,
        max_chars: int = 6000
    ) -> str:
        """
        Filtra e prioriza regras relevantes para o papel do agente (ex: frontend, backend, qa).
        Se nenhum filtro específico se aplicar, retorna as regras consolidadas padrão.
        """
        base_text = rules_text if rules_text is not None else self.load_rules(max_chars=max_chars)
        if not base_text or not role:
            return base_text

        # Priorização baseada em tópicos relevantes ao papel do agente
        role_lower = role.lower()
        paragraphs = base_text.split("\n\n### 📋 Regra: ")
        if len(paragraphs) <= 1:
            return base_text

        header = paragraphs[0]
        rules_blocks = ["### 📋 Regra: " + p for p in paragraphs[1:]]

        matched = []
        unmatched = []

        for block in rules_blocks:
            b_lower = block.lower()
            if role_lower in b_lower:
                matched.append(block)
            else:
                unmatched.append(block)

        # Coloca as regras com correspondência semântica no topo
        ordered = matched + unmatched
        result = (header + "\n\n" if header.strip() else "") + "\n\n".join(ordered)
        return self.clean_markdown_snippet(result, max_chars=max_chars)


# Utilitários de acesso rápido
def get_rules_manager(custom_dir: Optional[str] = None) -> RulesManager:
    return RulesManager.get_instance(custom_rules_dir=custom_dir)

def load_project_rules(rules_dir: Optional[str] = None, max_chars: int = 8000) -> str:
    return get_rules_manager(custom_dir=rules_dir).load_rules(max_chars=max_chars)
