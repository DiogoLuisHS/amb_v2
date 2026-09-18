#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AMB_V2 - Google Antigravity SDK & Cognitive Client (SRP)
Localização: amb_v2/integrations/antigravity/antigravity_client.py
"""

import os
import sys
import json
import shutil
import subprocess
from typing import Dict, Any, Optional, List

from core.bootstrap import ensure_amb_env
ensure_amb_env()

from core import (
    Colors,
    log,
    log_error,
    get_env,
    require_env,
    ApiExecutionError,
)
from workspace import (
    find_repo_root,
    load_project_json,
    RulesManager,
    get_rules_manager,
)
from integrations.common.base_google_client import BaseGoogleClient
from integrations.antigravity.antigravity_core.gemini_backend import GeminiBackend


class AntigravityClient:
    """Client cognitivo que usa a CLI agy ou a API direta do Gemini."""

    def __init__(self, model: Optional[str] = None):
        self.model = self._resolve_model(model)
        self.api_key = get_env("GEMINI_API_KEY")
        self.google_client = BaseGoogleClient(
            service_name="GEMINI",
            timeout=35,
            max_retries=2,
            base_delay=1.0,
        )
        self.backend = GeminiBackend(api_key=self.api_key, google_client=self.google_client)

    @staticmethod
    def _resolve_model(model: Optional[str] = None) -> str:
        if model: return model
        env_m = get_env("ANTIGRAVITY_MODEL") or get_env("GEMINI_MODEL")
        if env_m: return env_m
        p_data = load_project_json()
        if isinstance(p_data, dict):
            if isinstance(p_data.get("antigravity"), dict) and p_data["antigravity"].get("model"): return p_data["antigravity"]["model"]
            if isinstance(p_data.get("gemini"), dict) and p_data["gemini"].get("model"): return p_data["gemini"]["model"]
        return "gemini-3.8-flash"

    def _generate_via_agy_cli(self, prompt: str, system_instruction: Optional[str] = None) -> Optional[str]:
        if not shutil.which("agy"): return None
        try:
            full_prompt = f"System: {system_instruction}\n\nUser: {prompt}" if system_instruction else prompt
            res = subprocess.run(["agy", "-p", full_prompt], capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=20, check=False)
            if res.returncode == 0 and res.stdout.strip(): return res.stdout.strip()
        except Exception: pass
        return None

    def generate_text(self, prompt: str, system_instruction: Optional[str] = None, temperature: float = 0.2, max_output_tokens: int = 8192) -> str:
        if self.api_key:
            self.backend.api_key = self.api_key
            try:
                return self.backend._generate_via_gemini_api(prompt, self.model, system_instruction, temperature, max_output_tokens)
            except Exception as e:
                log("ANTIGRAVITY", f"Chamada REST indisponível ({e}). Tentando CLI agy...", Colors.YELLOW)
                cli_out = self._generate_via_agy_cli(prompt, system_instruction)
                if cli_out: return cli_out
                raise e
        cli_out = self._generate_via_agy_cli(prompt, system_instruction)
        if cli_out: return cli_out
        self.backend.api_key = self.api_key
        return self.backend._generate_via_gemini_api(prompt, self.model, system_instruction, temperature, max_output_tokens)

    def generate_content(self, prompt: str, system_instruction: Optional[str] = None, json_mode: bool = False) -> str:
        return self.generate_text(prompt=prompt, system_instruction=system_instruction, temperature=0.0 if json_mode else 0.2)

    def synthesize_prompt(self, base_prompt: str = "", task_type: str = "feature", rules_dir: Optional[str] = None, include_context: bool = True, **kwargs) -> str:
        raw_idea, role, rules_context = kwargs.get("raw_idea", base_prompt), kwargs.get("role", task_type), kwargs.get("rules_context", rules_dir)
        active_rules = rules_context if rules_context is not None else get_rules_manager().load_rules()
        sys_inst = "Você é o Arquiteto de Software Principal e Coordenador Técnico. Gere um prompt executivo rigoroso, definindo critérios de aceitação, SRP e stack."
        prompt = f'Ideia:\n"{raw_idea}"\nPapel: {role}\nDiretrizes:\n{active_rules or "SRP, tipagem rigorosa, testes, 0 quebras."}\nGere o prompt final.'
        try:
            return self.generate_text(prompt=prompt, system_instruction=sys_inst)
        except Exception as e:
            log("ANTIGRAVITY", f"Aviso: Síntese via IA indisponível ({e}). Usando template...", Colors.YELLOW)
            return f"# 🎯 ESCOPO TÉCNICO EXECUTIVO\n\n## 📌 Contexto\n{raw_idea}\n\n## 📐 Diretrizes\n- SRP, Tipagem, Qualidade.\n\n{active_rules}\n"

    def validate_code(self, file_path: str, rules_context: Optional[str] = None) -> str:
        """Audita o código contra regras arquiteturais."""
        root = find_repo_root()
        full_path = os.path.abspath(os.path.join(root, file_path)) if not os.path.isabs(file_path) else file_path

        if not os.path.exists(full_path):
            raise ApiExecutionError(f"Arquivo não encontrado para validação: {full_path}")

        with open(full_path, "r", encoding="utf-8", errors="replace") as f:
            code_content = f.read()

        rules_mgr = get_rules_manager()
        active_rules = rules_context if rules_context is not None else rules_mgr.load_rules()

        ext = os.path.splitext(full_path)[1].lower()
        lang_map = {
            ".py": "Python", ".ts": "TypeScript", ".tsx": "TypeScript/React",
            ".js": "JavaScript", ".jsx": "JavaScript/React", ".go": "Go"
        }
        lang_detected = lang_map.get(ext, f"código fonte ({ext or 'texto'})")

        system_instruction = (
            f"Você é o Auditor de Qualidade de Código do Google Antigravity para projetos {lang_detected}. "
            "Analise o arquivo e aponte violações de tipagem, boas práticas, SRP e não conformidade."
        )

        prompt = f"""Arquivo: {file_path} (Linguagem: {lang_detected})\nCÓDIGO:\n```\n{code_content[:6000]}\n```\nREGRAS:\n{active_rules or 'Tipagem, SRP, coesão.'}"""
        return self.generate_text(prompt=prompt, system_instruction=system_instruction)

    def validate_architecture(
        self,
        file_paths: Optional[List[str]] = None,
        rules_dir: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Audita múltiplos arquivos e retorna dicionário."""
        file_path = kwargs.get("file_path")
        rules_context = kwargs.get("rules_context", rules_dir)
        if file_path and not file_paths:
            return {"result": self.validate_code(file_path, rules_context)}

        results = {}
        for path in (file_paths or []):
            try:
                results[path] = self.validate_code(path, rules_context)
            except Exception as e:
                results[path] = str(e)
        return {"results": results}

    def get_status(self) -> Dict[str, Any]:
        agy_cli = shutil.which("agy")
        mgr = get_rules_manager()
        r_dir = mgr.resolve_rules_dir()
        r_list = mgr.list_rules(rules_dir=r_dir) if r_dir else []
        hk, hc = bool(self.api_key), bool(agy_cli)
        return {
            "status": "OK" if (hk or hc) else "WARNING", "model": self.model,
            "gemini_api_key_configured": hk, "agy_cli_installed": hc,
            "agy_cli_path": agy_cli, "rules_directory": r_dir,
            "rules_count": len(r_list), "rules": [r["name"] for r in r_list]
        }

def synthesize_prompt(raw_idea: str, role: str = "general", rules_context: Optional[str] = None) -> str:
    return AntigravityClient().synthesize_prompt(raw_idea, role=role, rules_context=rules_context)

def validate_code(file_path: str, rules_context: Optional[str] = None) -> str:
    return AntigravityClient().validate_code(file_path, rules_context=rules_context)

validate_architecture = validate_code
