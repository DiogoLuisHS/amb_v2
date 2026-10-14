#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🧠 Antigravity Tool: validate_architecture (Facade)
Localização: amb_v2/integrations/antigravity/tools/validate_architecture.py
Responsabilidade Única: Prover CLI e ponto de entrada funcional para auditoria arquitetural
de arquivos de código contra as diretrizes do repositório ativo.
"""

import sys
import os
import json
import argparse
from typing import Optional, Dict, Any

from core.bootstrap import ensure_amb_env
ensure_amb_env()

from core import Colors, log, log_error, ApiExecutionError
from integrations.antigravity.antigravity_client import validate_code


def run_validate_architecture(
    file_path: str,
    rules_context: Optional[str] = None
) -> str:
    """Executa auditoria de arquitetura e conformidade em um arquivo de código."""
    return validate_code(file_path=file_path, rules_context=rules_context)


def generate_architecture_fix(file_path: str, report: str) -> Optional[str]:
    """
    Lê o conteúdo original do arquivo e as regras violadas indicadas no report, e solicita ao
    AntigravityClient uma correção pontual preservando a lógica e docstrings originais.
    """
    from integrations.antigravity.antigravity_client import AntigravityClient

    if not os.path.exists(file_path):
        return None

    with open(file_path, "r", encoding="utf-8", errors="replace") as f:
        code_content = f.read()

    sys_inst = (
        "Você é o Especialista Sênior em Correção Arquitetural do Google Antigravity. "
        "Sua função é gerar o CÓDIGO CORRIGIDO COMPLETO de um arquivo baseado num relatório de auditoria, "
        "resolvendo cirurgicamente todas as violações relatadas (como limite de linhas, tipagem estrita e SRP). "
        "Preserve a lógica original de negócio, imports e docstrings essenciais. "
        "ATENÇÃO: Retorne APENAS o código puro, sem formatação markdown extra (como ```python) e sem explicações."
    )

    prompt = (
        f"Arquivo Original ({file_path}):\n"
        f"```python\n{code_content}\n```\n\n"
        f"Relatório de Auditoria (Violações a corrigir):\n"
        f"{report}\n\n"
        "Com base nas violações acima, forneça o código completo corrigido. Não retorne markdown, apenas o texto do código novo."
    )

    client = AntigravityClient()
    try:
        new_code = client.generate_text(prompt=prompt, system_instruction=sys_inst)
        # Strip markdown if model still returned it
        if new_code.startswith("```"):
            lines = new_code.splitlines()
            if len(lines) > 2 and lines[0].startswith("```"):
                new_code = "\n".join(lines[1:-1])
                if lines[-1].strip() != "```":
                     new_code += "\n" + lines[-1]
        return new_code.strip() + "\n"
    except Exception as e:
        log_error("ANTIGRAVITY", f"Falha ao gerar correção para {file_path}: {e}")
        return None


def main():
    p = argparse.ArgumentParser(description="Audita o código contra as diretrizes e regras arquiteturais do projeto.")
    p.add_argument("file", help="Caminho do arquivo a ser auditado.")
    p.add_argument("--json", action="store_true", help="Exibe o resultado em formato JSON estruturado.")
    args = p.parse_args()

    try:
        res = run_validate_architecture(file_path=args.file)
        if args.json:
            print(json.dumps({"file": args.file, "report": res}, indent=2, ensure_ascii=False))
        else:
            print(res)
    except Exception as e:
        log_error("ANTIGRAVITY", str(e))
        sys.exit(1)


if __name__ == "__main__":
    main()
