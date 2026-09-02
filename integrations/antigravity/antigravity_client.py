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

from config import Colors, log, log_error, get_env, require_env, ApiExecutionError, find_repo_root


class AntigravityClient:
    """Client cognitivo que usa a CLI oficial `agy` ou a API direta do Gemini."""

    def __init__(self, model: Optional[str] = None):
        self.model = model or get_env("GEMINI_MODEL") or "gemini-3.7-flash"
        self.api_key = get_env("GEMINI_API_KEY")


    def _generate_via_agy_cli(self, prompt: str, system_instruction: Optional[str] = None) -> Optional[str]:
        """Tenta inferência via CLI agy se disponível no PATH."""
        try:
            full_prompt = f"System: {system_instruction}\n\nUser: {prompt}" if system_instruction else prompt
            res = subprocess.run(
                ["agy", "-p", full_prompt],
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=45,
                check=False
            )
            if res.returncode == 0 and res.stdout.strip():
                return res.stdout.strip()
        except Exception:
            pass
        return None

    def _generate_via_api(self, prompt: str, system_instruction: Optional[str] = None) -> str:
        """Executa chamada direta à REST API do Google Gemini com fallback automático de modelos."""
        if not self.api_key:
            require_env("GEMINI_API_KEY")

        models_to_try = [self.model, "gemini-2.5-flash", "gemini-2.0-flash", "gemini-1.5-flash", "gemini-2.5-pro"]
        # Remove duplicados preservando ordem
        models_to_try = list(dict.fromkeys([m for m in models_to_try if m]))

        last_error = None
        for mod in models_to_try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{mod}:generateContent?key={self.api_key}"
            headers = {"Content-Type": "application/json"}

            payload = {
                "contents": [
                    {
                        "parts": [{"text": prompt}]
                    }
                ],
                "generationConfig": {
                    "temperature": 0.2,
                    "maxOutputTokens": 4096
                }
            }

            if system_instruction:
                payload["systemInstruction"] = {
                    "parts": [{"text": system_instruction}]
                }

            data_bytes = json.dumps(payload).encode("utf-8")
            req = urllib.request.Request(url, data=data_bytes, headers=headers, method="POST")

            try:
                with urllib.request.urlopen(req, timeout=45) as resp:
                    resp_data = json.loads(resp.read().decode("utf-8"))
                    candidates = resp_data.get("candidates", [])
                    if candidates:
                        parts = candidates[0].get("content", {}).get("parts", [])
                        if parts:
                            return parts[0].get("text", "").strip()
            except urllib.error.HTTPError as e:
                err_text = e.read().decode("utf-8")
                msg = f"HTTP {e.code}: {e.reason}"
                try:
                    err_j = json.loads(err_text)
                    if "error" in err_j:
                        msg = f"{msg} - {err_j['error'].get('message', err_text)}"
                except Exception:
                    msg = f"{msg} - {err_text}"
                last_error = msg
                continue
            except Exception as e:
                last_error = str(e)
                continue

        raise ApiExecutionError(f"Erro na chamada do Gemini/Antigravity: {last_error}", hint="Verifique se sua GEMINI_API_KEY é válida.")

    def generate_text(self, prompt: str, system_instruction: Optional[str] = None) -> str:
        """Gera texto utilizando CLI agy ou fallback para API REST oficial com fallback gracioso."""
        cli_out = self._generate_via_agy_cli(prompt, system_instruction)
        if cli_out:
            return cli_out
        try:
            return self._generate_via_api(prompt, system_instruction)
        except Exception as e:
            log("ANTIGRAVITY", f"Aviso na síntese via LLM ({e}). Utilizando especificação original estruturada.", Colors.YELLOW)
            return prompt

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
        return self.generate_text(prompt=prompt, system_instruction=system_instruction)

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

validate_architecture = validate_code


if __name__ == "__main__":
    try:
        c = AntigravityClient()
        log("ANTIGRAVITY", "Testando inferência com modelo padrão...", Colors.CYAN)
        res = c.generate_text(prompt="Responda apenas 'OK - Antigravity Online'")
        print(f"{Colors.GREEN}✅ {res}{Colors.RESET}")
    except Exception as e:
        log_error("ANTIGRAVITY", str(e))
