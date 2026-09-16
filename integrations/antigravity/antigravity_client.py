#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🧠 AMB_V2 - Google Antigravity SDK & Cognitive Client (SRP)
Localização: amb_v2/integrations/antigravity/antigravity_client.py
Responsabilidade Única: Prover interface unificada para geração de texto e inferência cognitiva
utilizando a CLI oficial `agy` ou chamada direta à REST API do Gemini com fail-fast.
"""

import os
import sys
import json
import subprocess
import urllib.request
import urllib.error
from typing import Dict, Any, Optional

from config.bootstrap import ensure_amb_env
ensure_amb_env()

from config import Colors, log, log_error, get_env, require_env, ApiExecutionError, find_repo_root
from integrations.common.base_google_client import BaseGoogleClient


class AntigravityClient:
    """Client cognitivo que usa a CLI oficial `agy` ou a API direta do Gemini."""

    def __init__(self, model: Optional[str] = None):
        self.model = model or get_env("GEMINI_MODEL") or "gemini-3.8-flash"
        self.api_key = get_env("GEMINI_API_KEY")
        self.google_client = BaseGoogleClient(
            service_name="GEMINI",
            timeout=35,
            max_retries=2,
            base_delay=1.0,
        )

    def _generate_via_agy_cli(self, prompt: str, system_instruction: Optional[str] = None) -> Optional[str]:
        """Tenta inferência via CLI agy se disponível no PATH."""
        import shutil
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
                timeout=10,
                check=False
            )
            if res.returncode == 0 and res.stdout.strip():
                return res.stdout.strip()
        except Exception:
            pass
        return None

    def _generate_via_api(self, prompt: str, system_instruction: Optional[str] = None) -> str:
        """Executa chamada direta à REST API do Google Gemini com retry e fallback inteligente."""
        if not self.api_key:
            require_env("GEMINI_API_KEY")

        # Apenas modelos modernos de última geração
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
                    "temperature": 0.2,
                    "maxOutputTokens": 8192
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



    def generate_text(self, prompt: str, system_instruction: Optional[str] = None) -> str:
        """Gera texto utilizando os modelos Gemini modernos via REST e fallback final para o CLI Antigravity (agy)."""
        if self.api_key:
            try:
                return self._generate_via_api(prompt, system_instruction)
            except Exception as e:
                log("ANTIGRAVITY", f"Chamada REST indisponível ({e}). Tentando fallback para CLI agy...", Colors.YELLOW)
                cli_out = self._generate_via_agy_cli(prompt, system_instruction)
                if cli_out:
                    return cli_out
                raise e

        cli_out = self._generate_via_agy_cli(prompt, system_instruction)
        if cli_out:
            return cli_out
        return self._generate_via_api(prompt, system_instruction)




    def synthesize_prompt(self, raw_idea: str, role: str = "general") -> str:
        """Sintetiza um prompt formal para execução autônoma."""
        root = find_repo_root()
        rules_dir = os.path.join(root, ".antigravity", "rules")
        if not os.path.exists(rules_dir):
            rules_dir = os.path.join(root, ".gemini", "rules")

        rules_content = ""
        if os.path.exists(rules_dir):
            for f in sorted(os.listdir(rules_dir)):
                if f.endswith(".md"):
                    try:
                        with open(os.path.join(rules_dir, f), "r", encoding="utf-8", errors="replace") as rf:
                            rules_content += f"\n--- [{f}] ---\n" + rf.read()[:500]
                    except Exception:
                        pass

        system_instruction = (
            "Você é o Arquiteto de Software Principal do projeto. "
            "Sua missão é ler uma especificação informal de tarefa e gerar um prompt técnico "
            "extremamente detalhado, com critérios de aceitação, separação de responsabilidades (SRP) "
            "e contratos estritos de tipos."
        )

        prompt = f"""Ideia / Solicitação do Usuário:
"{raw_idea}"

Papel / Especialidade: {role}

Regras Arquiteturais do Repositório:
{rules_content or 'TypeScript estrito, SRP, componentes modulares, validação com build/typecheck.'}

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
- **Tipagem Estrita**: Tipos rigorosos, 0 `any` e conformidade com schemas.
- **Qualidade & Validação**: Realizar testes locais e validação de build/syntax.

{rules_content}
"""


    def validate_code(self, file_path: str) -> str:
        """Audita o código contra as diretrizes e regras arquiteturais do projeto."""
        root = find_repo_root()
        full_path = os.path.abspath(os.path.join(root, file_path)) if not os.path.isabs(file_path) else file_path

        if not os.path.exists(full_path):
            raise ApiExecutionError(f"Arquivo não encontrado para validação: {full_path}")

        with open(full_path, "r", encoding="utf-8", errors="replace") as f:
            code_content = f.read()

        rules_dir = os.path.join(root, ".antigravity", "rules")
        if not os.path.exists(rules_dir):
            rules_dir = os.path.join(root, ".gemini", "rules")

        rules_text = ""
        if os.path.exists(rules_dir):
            for rf in sorted(os.listdir(rules_dir)):
                if rf.endswith(".md"):
                    try:
                        with open(os.path.join(rules_dir, rf), "r", encoding="utf-8", errors="replace") as rule_file:
                            rules_text += f"\n--- [{rf}] ---\n" + rule_file.read()
                    except Exception:
                        pass

        system_instruction = (
            "Você é o Auditor de Qualidade de Código do Antigravity. "
            "Analise o arquivo fornecido e aponte violações de tipagem TypeScript, Princípio da Responsabilidade Única (SRP), "
            "imports mortos, falta de validação ou não conformidade com as regras do repositório."
        )

        prompt = f"""Arquivo analisado: {file_path}

CÓDIGO:
```
{code_content[:4000]}
```

REGRAS ARQUITETURAIS:
{rules_text or 'TypeScript estrito, SRP, componentes isolados, 0 any, 0 imports mortos.'}

Aponte se o código está em conformidade. Se houver problemas, liste os pontos específicos para correção."""
        return self.generate_text(prompt=prompt, system_instruction=system_instruction)


# Funções utilitárias avulsas para import direto
def synthesize_prompt(raw_idea: str, role: str = "general") -> str:
    return AntigravityClient().synthesize_prompt(raw_idea, role=role)

def validate_code(file_path: str) -> str:
    return AntigravityClient().validate_code(file_path)

if __name__ == "__main__":
    try:
        c = AntigravityClient()
        log("ANTIGRAVITY", "Testando inferência com modelo padrão...", Colors.CYAN)
        res = c.generate_text(prompt="Responda apenas 'OK - Antigravity Online'")
        print(f"{Colors.GREEN}✅ {res}{Colors.RESET}")
    except Exception as e:
        log_error("ANTIGRAVITY", str(e))


validate_architecture = validate_code


if __name__ == "__main__":
    try:
        c = AntigravityClient()
        log("ANTIGRAVITY", "Testando inferência com modelo padrão...", Colors.CYAN)
        res = c.generate_text(prompt="Responda apenas 'OK - Antigravity Online'")
        print(f"{Colors.GREEN}✅ {res}{Colors.RESET}")
    except Exception as e:
        log_error("ANTIGRAVITY", str(e))
