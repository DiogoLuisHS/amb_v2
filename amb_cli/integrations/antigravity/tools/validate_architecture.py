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
