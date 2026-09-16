#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🧠 AMB_V2 - Google Antigravity SDK & Cognitive Client (SRP)
Localização: amb_v2/integrations/antigravity/antigravity_client.py
Responsabilidade Única: Prover interface unificada para geração de texto, inferência cognitiva,
síntese de prompts executivos e auditoria de código utilizando a CLI oficial `agy`
ou chamada direta à REST API do Gemini com fail-fast e regras dinâmicas do projeto.
"""

import os
import sys
import json
import shutil
import subprocess
from typing import Dict, Any, Optional, List

from config.bootstrap import ensure_amb_env
ensure_amb_env()

from config import (
    Colors,
    log,
    log_error,
    get_env,
    require_env,
    ApiExecutionError,
    find_repo_root,
    load_project_json,
    RulesManager,
    get_rules_manager
)
from integrations.common.base_google_client import BaseGoogleClient


class AntigravityClient:
    """Client cognitivo que usa a CLI oficial `agy` ou a API direta do Gemini com resolução dinâmica."""

    def __init__(self, model: Optional[str] = None):
        self.model = self._resolve_model(model)
        self.api_key = get_env("GEMINI_API_KEY")
        self.google_client = BaseGoogleClient(
            service_name="GEMINI",
            timeout=35,
            max_retries=2,
            base_delay=1.0,
        )

    @staticmethod
    def _resolve_model(model: Optional[str] = None) -> str:
        """Determina o modelo cognitivo ativo seguindo a hierarquia de configuração."""
        if model:
            return model
        env_model = get_env("ANTIGRAVITY_MODEL") or get_env("GEMINI_MODEL")
        if env_model:
            return env_model
        project_data = load_project_json()
        if isinstance(project_data, dict):
            agy_cfg = project_data.get("antigravity", {})
            if isinstance(agy_cfg, dict) and agy_cfg.get("model"):
                return agy_cfg["model"]
            gemini_cfg = project_data.get("gemini", {})
            if isinstance(gemini_cfg, dict) and gemini_cfg.get("model"):
                return gemini_cfg["model"]
        return "gemini-3.8-flash"

    def _generate_via_agy_cli(self, prompt: str, system_instruction: Optional[str] = None) -> Optional[str]:
        """Tenta inferência via CLI agy se disponível no PATH."""
        if not shutil.which("agy"):
            return None
        try:
            full_prompt = f"System: {system_instruction}\n\nUser: {prompt}" if system_instruction else prompt
            res = subprocess.run(
                ["agy", "-p", full_prompt],
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=20,
                check=False
            )
            if res.returncode == 0 and res.stdout.strip():
                return res.stdout.strip()
        except Exception:
            pass
        return None

    def _generate_via_api(
        self,
        prompt: str,
        system_instruction: Optional[str] = None,
        temperature: float = 0.2,
        max_output_tokens: int = 8192
    ) -> str:
        """Executa chamada direta à REST API do Google Gemini com retry e fallback inteligente."""
        if not self.api_key:
            require_env("GEMINI_API_KEY")

        # Modelos modernos de última geração para failover de quota
        models_to_try = [self.model]
        for fallback_m in ["gemini-3.8-flash", "gemini-3.7-flash", "gemini-3.6-flash", "gemini-3.1-pro-preview"]:
            if fallback_m not in models_to_try:
                models_to_try.append(fallback_m)

        last_err = None
        for current_m in models_to_try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{current_m}:generateContent"
            payload = {
                "contents": [
                    {
                        "parts": [{"text": prompt}]
                    }
                ],
                "generationConfig": {
                    "temperature": temperature,
                    "maxOutputTokens": max_output_tokens
                }
            }

            if system_instruction:
                payload["systemInstruction"] = {
                    "parts": [{"text": system_instruction}]
                }

            try:
                resp_data = self.google_client.execute_request(
                    method="POST",
                    path_or_url=url,
                    params={"key": self.api_key},
                    data=payload,
                    timeout=35,
                )
                candidates = resp_data.get("candidates", [])
                if candidates:
                    parts = candidates[0].get("content", {}).get("parts", [])
                    if parts:
                        return parts[0].get("text", "").strip()
                raise ApiExecutionError("Resposta vazia retornada pelo modelo Gemini.")
            except ApiExecutionError as e:
                last_err = e
                # Se for 429 ou 503, tenta o próximo modelo de fallback
                if "429" in str(e) or "503" in str(e) or "Rate Limit" in getattr(e, "hint", ""):
                    log("ANTIGRAVITY", f"Limite ou instabilidade no modelo ({current_m}). Tentando fallback...", Colors.YELLOW)
                    continue
                raise e
            except Exception as e:
                last_err = ApiExecutionError(f"Falha de conexão com a API do Gemini ({current_m}): {e}")
                continue

        raise last_err or ApiExecutionError("Falha na chamada REST dos modelos Gemini.")

    def generate_text(
        self,
        prompt: str,
        system_instruction: Optional[str] = None,
        temperature: float = 0.2,
        max_output_tokens: int = 8192
    ) -> str:
        """Gera texto utilizando os modelos Gemini modernos via REST e fallback para o CLI Antigravity (agy)."""
        if self.api_key:
            try:
                return self._generate_via_api(
                    prompt=prompt,
                    system_instruction=system_instruction,
                    temperature=temperature,
                    max_output_tokens=max_output_tokens
                )
            except Exception as e:
                log("ANTIGRAVITY", f"Chamada REST indisponível ({e}). Tentando fallback para CLI agy...", Colors.YELLOW)
                cli_out = self._generate_via_agy_cli(prompt, system_instruction)
                if cli_out:
                    return cli_out
                raise e

        cli_out = self._generate_via_agy_cli(prompt, system_instruction)
        if cli_out:
            return cli_out
        return self._generate_via_api(
            prompt=prompt,
            system_instruction=system_instruction,
            temperature=temperature,
            max_output_tokens=max_output_tokens
        )

    def synthesize_prompt(
        self,
        raw_idea: str,
        role: str = "general",
        rules_context: Optional[str] = None
    ) -> str:
        """Sintetiza um prompt executivo formal baseado nas regras do projeto ativo (sem premissas a priori)."""
        rules_mgr = get_rules_manager()
        active_rules = rules_context if rules_context is not None else rules_mgr.load_rules()

        system_instruction = (
            "Você é o Arquiteto de Software Principal e Coordenador Técnico do projeto. "
            "Sua missão é ler uma especificação informal ou requisito do usuário e gerar um prompt executivo "
            "estruturado, detalhado e rigoroso, definindo critérios de aceitação, separação de responsabilidades (SRP) "
            "e conformidade com as convenções e stack do repositório."
        )

        prompt = f"""Ideia / Solicitação do Usuário:
"{raw_idea}"

Papel / Especialidade: {role}

Diretrizes Arquiteturais do Repositório:
{active_rules or 'Mantenha tipagem rigorosa da linguagem/stack do projeto, SRP, componentes modulares, testes automatizados e 0 quebras de contrato.'}

Gere o prompt executivo final pronto para despacho."""
        try:
            return self.generate_text(prompt=prompt, system_instruction=system_instruction)
        except Exception as e:
            log("ANTIGRAVITY", f"Aviso: Síntese via IA indisponível temporariamente ({e}). Usando template executivo estruturado...", Colors.YELLOW)
            return f"""# 🎯 ESCOPO TÉCNICO EXECUTIVO (AMB_V2)

## 📌 Contexto & Requisitos de Engenharia
{raw_idea}

## 📐 Diretrizes de Arquitetura & Qualidade
- **Princípio da Responsabilidade Única (SRP)**: Módulos focados e funções coesas.
- **Tipagem Estrita**: Tipos rigorosos de acordo com a stack do projeto, sem tipos opacos ou permissivos desnecessários.
- **Qualidade & Validação**: Execução de suíte de testes locais e validação de sintaxe/build.

{active_rules}
"""

    def validate_code(self, file_path: str, rules_context: Optional[str] = None) -> str:
        """Audita o código contra as diretrizes e regras arquiteturais da stack do repositório."""
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
            ".py": "Python",
            ".ts": "TypeScript",
            ".tsx": "TypeScript/React",
            ".js": "JavaScript",
            ".jsx": "JavaScript/React",
            ".go": "Go",
            ".rs": "Rust",
            ".java": "Java",
            ".rb": "Ruby",
            ".php": "PHP",
            ".cs": "C#",
            ".cpp": "C++",
            ".c": "C",
        }
        lang_detected = lang_map.get(ext, f"código fonte ({ext or 'texto'})")

        system_instruction = (
            f"Você é o Auditor de Qualidade de Código do Google Antigravity para projetos {lang_detected}. "
            "Analise o arquivo fornecido e aponte violações de tipagem e boas práticas da linguagem, "
            "violações do Princípio da Responsabilidade Única (SRP), dependências mortas ou não utilizadas, "
            "ausência de tratamento de erros e não conformidade com as regras arquiteturais do repositório."
        )

        prompt = f"""Arquivo analisado: {file_path} (Linguagem: {lang_detected})

CÓDIGO:
```
{code_content[:6000]}
```

REGRAS ARQUITETURAIS DO PROJETO:
{active_rules or 'Tipagem estrita, SRP, módulos coesos, imports limpos e robustez no tratamento de erros.'}

Aponte de forma estruturada:
1. Conformidade geral (Conforme / Não Conforme).
2. Problemas identificados (se houver, com linha aproximada ou função afetada).
3. Recomendações objetivas de refatoração para adequação às regras do projeto."""
        return self.generate_text(prompt=prompt, system_instruction=system_instruction)

    def get_status(self) -> Dict[str, Any]:
        """Retorna o status consolidado de runtime do cliente Antigravity e Gemini."""
        agy_cli = shutil.which("agy")
        rules_mgr = get_rules_manager()
        rules_dir = rules_mgr.resolve_rules_dir()
        rules_list = rules_mgr.list_rules(rules_dir=rules_dir) if rules_dir else []

        has_api_key = bool(self.api_key)
        has_agy_cli = bool(agy_cli)

        status = "OK" if (has_api_key or has_agy_cli) else "WARNING"

        return {
            "status": status,
            "model": self.model,
            "gemini_api_key_configured": has_api_key,
            "agy_cli_installed": has_agy_cli,
            "agy_cli_path": agy_cli,
            "rules_directory": rules_dir,
            "rules_count": len(rules_list),
            "rules": [r["name"] for r in rules_list]
        }


# Funções utilitárias avulsas para import direto
def synthesize_prompt(raw_idea: str, role: str = "general", rules_context: Optional[str] = None) -> str:
    return AntigravityClient().synthesize_prompt(raw_idea, role=role, rules_context=rules_context)

def validate_code(file_path: str, rules_context: Optional[str] = None) -> str:
    return AntigravityClient().validate_code(file_path, rules_context=rules_context)

validate_architecture = validate_code


if __name__ == "__main__":
    try:
        c = AntigravityClient()
        log("ANTIGRAVITY", "Testando inferência com modelo padrão...", Colors.CYAN)
        res = c.generate_text(prompt="Responda apenas 'OK - Antigravity Online'")
        print(f"{Colors.GREEN}✅ {res}{Colors.RESET}")
    except Exception as e:
        log_error("ANTIGRAVITY", str(e))
