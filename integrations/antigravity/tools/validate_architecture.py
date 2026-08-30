#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🧠 AMB_V2 - Antigravity SDK: Validador de Regras Arquiteturais (SRP)
Localização: amb_v2/integrations/antigravity/tools/validate_architecture.py
Responsabilidade Única: Avaliar um arquivo ou alteração contra as regras em .antigravity/rules/.
"""

import os
import sys
import argparse

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

from config import Colors, log, log_error, find_repo_root, ApiExecutionError
from antigravity_client import AntigravityClient


def validate_code(file_path: str) -> str:
    """Audita o código contra as diretrizes do projeto."""
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

    client = AntigravityClient()
    return client.generate_text(prompt=prompt, system_instruction=system_instruction)


validate_architecture = validate_code


def main():
    parser = argparse.ArgumentParser(description="Audita um arquivo de código contra as regras do repositório.")
    parser.add_argument("--file", "-f", required=True, help="Caminho do arquivo para validação.")

    args = parser.parse_args()

    try:
        log("ANTIGRAVITY-VAL", f"Auditando arquivo: {args.file}...", Colors.CYAN)
        res = validate_code(args.file)
        print("\n" + "=" * 75)
        print(f"{Colors.BOLD}RELATÓRIO DE AUDITORIA ARQUITETURAL:{Colors.RESET}")
        print("=" * 75)
        print(res)
        print("=" * 75)
    except Exception as e:
        log_error("ANTIGRAVITY-VAL", str(e))
        sys.exit(1)


if __name__ == "__main__":
    main()
