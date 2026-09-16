#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🧠 Antigravity Tool: synthesize_prompt (Facade)
Localização: amb_v2/integrations/antigravity/tools/synthesize_prompt.py
Responsabilidade Única: Prover CLI e ponto de entrada funcional para síntese de prompts
executivos formais com IA a partir de ideias informais.
"""

import sys
import os
import argparse
from typing import Optional

from config.bootstrap import ensure_amb_env
ensure_amb_env()

from config import Colors, log, log_error, ApiExecutionError
from integrations.antigravity.antigravity_client import synthesize_prompt


def run_synthesize_prompt(
    raw_idea: str,
    role: str = "general",
    output_file: Optional[str] = None
) -> str:
    """Executa a síntese de prompt e opcionalmente grava no arquivo de destino."""
    res = synthesize_prompt(raw_idea=raw_idea, role=role)
    if output_file:
        out_abs = os.path.abspath(output_file)
        os.makedirs(os.path.dirname(out_abs), exist_ok=True)
        with open(out_abs, "w", encoding="utf-8") as f:
            f.write(res)
        log("ANTIGRAVITY", f"Prompt sintetizado salvo em: {out_abs}", Colors.GREEN)
    return res


def main():
    p = argparse.ArgumentParser(description="Sintetiza um prompt formal para execução autônoma via IA.")
    p.add_argument("--idea", "-i", required=True, help="Ideia informal ou requisito a sintetizar.")
    p.add_argument("--role", "-r", default="general", help="Especialidade ou papel do agente (padrão: general).")
    p.add_argument("--output", "-o", help="Caminho do arquivo markdown de saída.")
    args = p.parse_args()

    try:
        res = run_synthesize_prompt(
            raw_idea=args.idea,
            role=args.role,
            output_file=args.output
        )
        if not args.output:
            print(res)
    except Exception as e:
        log_error("ANTIGRAVITY", str(e))
        sys.exit(1)


if __name__ == "__main__":
    main()
