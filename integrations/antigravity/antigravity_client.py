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

        # Apenas modelos modernos de última geração (3.7 e 3.6)
        models_to_try = [self.model]
        for fallback_m in ["gemini-3.7-flash", "gemini-3.6-flash"]:
            if fallback_m not in models_to_try:
                models_to_try.append(fallback_m)

        last_err = None
        for current_m in models_to_try:
            for attempt in range(3):
                url = f"https://generativelanguage.googleapis.com/v1beta/models/{current_m}:generateContent?key={self.api_key}"
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
                    with urllib.request.urlopen(req, timeout=35) as resp:
                        resp_data = json.loads(resp.read().decode("utf-8"))
                        candidates = resp_data.get("candidates", [])
                        if candidates:
                            parts = candidates[0].get("content", {}).get("parts", [])
                            if parts:
                                return parts[0].get("text", "").strip()
                        raise ApiExecutionError("Resposta vazia retornada pelo modelo Gemini.")
                except urllib.error.HTTPError as e:
                    err_text = e.read().decode("utf-8")
                    msg = f"HTTP {e.code}: {e.reason}"
                    try:
                        err_j = json.loads(err_text)
                        if "error" in err_j:
                            msg = f"{msg} - {err_j['error'].get('message', err_text)}"
                    except Exception:
                        msg = f"{msg} - {err_text}"

                    last_err = ApiExecutionError(f"Erro no modelo {current_m}: {msg}")

                    # Se for 429 (Rate Limit por minuto) ou 503 (alta demanda)
                    if e.code in [429, 503] and attempt < 2:
                        import time
                        import re
                        retry_match = re.search(r"Please retry in (\d+(\.\d+)?)s", err_text, re.IGNORECASE)
                        if retry_match:
                            wait_sec = min(float(retry_match.group(1)) + 1.0, 35.0)
                        else:
                            wait_sec = 3.0 * (attempt + 1)
                        log("ANTIGRAVITY", f"Limite temporário de requisições ({current_m}). Aguardando {int(wait_sec)}s para liberação da cota...", Colors.YELLOW)
                        time.sleep(wait_sec)
                        continue
                    else:
                        break
                except Exception as e:
                    last_err = ApiExecutionError(f"Falha de conexão com a API do Gemini ({current_m}): {e}")
                    break

        raise last_err or ApiExecutionError("Falha na chamada REST dos modelos Gemini 3.7/3.6.")



    def generate_text(self, prompt: str, system_instruction: Optional[str] = None) -> str:
        """Gera texto utilizando Gemini 3.7/3.6 com controle de autorização prévia e fallback agy."""
        from config import is_gemini_confirmation_required

        # Verificação de Autorização Prévia (Configurável no Setup / .env / amb_project.json)
        if is_gemini_confirmation_required():
            print("\n" + "=" * 65)
            print(f"🛡️  {Colors.BOLD}{Colors.YELLOW}[AUTORIZAÇÃO GEMINI NECESSÁRIA]{Colors.RESET}")
            print(f"📦 Modelo Configurado: {Colors.CYAN}{self.model}{Colors.RESET}")
            preview = prompt.strip().replace("\n", " ")[:160] + ("..." if len(prompt) > 160 else "")
            print(f"💬 Prompt Preview: \"{preview}\"")
            print("=" * 65)
            try:
                ans = input(f"{Colors.BOLD}❓ Deseja autorizar o envio desta requisição ao Gemini? [s/N]: {Colors.RESET}").strip().lower()
                if ans not in ["s", "y", "sim", "yes"]:
                    print(f"{Colors.YELLOW}🚫 Requisição ao Gemini não autorizada. Operação cancelada.{Colors.RESET}\n")
                    raise ApiExecutionError("Chamada ao Gemini cancelada pelo usuário (autorização negada).")
                print(f"{Colors.GREEN}✔ Requisição autorizada. Enviando para o Gemini...{Colors.RESET}\n")
            except (EOFError, KeyboardInterrupt):
                print(f"\n{Colors.YELLOW}🚫 Requisição ao Gemini cancelada.{Colors.RESET}\n")
                raise ApiExecutionError("Chamada ao Gemini cancelada.")

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
