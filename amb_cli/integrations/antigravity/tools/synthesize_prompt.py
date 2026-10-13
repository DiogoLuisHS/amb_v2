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

from core.bootstrap import ensure_amb_env
ensure_amb_env()

from core import Colors, log, log_error, ApiExecutionError
from integrations.antigravity.antigravity_client import synthesize_prompt


def run_synthesize_prompt(
    raw_idea: str,
    role: str = "general",
    output_file: Optional[str] = None,
    image_path: Optional[str] = None,
    queue: bool = False,
) -> str:
    """Executa a síntese de prompt e opcionalmente grava no arquivo de destino ou enfileira na pasta de prompts."""
    res = synthesize_prompt(raw_idea=raw_idea, role=role, image_path=image_path)

    final_output_file = output_file
    if queue and not final_output_file:
        from amb_cli.workspace.project_context import get_next_prompt_filepath, find_repo_root
        from pathlib import Path

        # Extract title from the generated prompt
        lines = res.strip().split("\n")
        title = "prompt"
        for line in lines:
            if line.startswith("# "):
                title = line[2:].strip()
                break

        root = find_repo_root()
        prompts_dir = Path(root) / ".amb" / "prompts"
        final_output_file = str(get_next_prompt_filepath(prompts_dir, title))

    if final_output_file:
        out_abs = os.path.abspath(final_output_file)
        os.makedirs(os.path.dirname(out_abs), exist_ok=True)
        with open(out_abs, "w", encoding="utf-8") as f:
            f.write(res)
        if queue and not output_file:
            log("ANTIGRAVITY", f"Prompt adicionado à fila: {out_abs} (Execute: amb agent -p .amb/prompts/)", Colors.GREEN)
        else:
            log("ANTIGRAVITY", f"Prompt sintetizado salvo em: {out_abs}", Colors.GREEN)
    return res


def main():
    p = argparse.ArgumentParser(description="Sintetiza um prompt formal para execução autônoma via IA.")
    p.add_argument("--idea", "-i", required=True, help="Ideia informal ou requisito a sintetizar.")
    p.add_argument("--role", "-r", default="general", help="Especialidade ou papel do agente (padrão: general).")
    p.add_argument("--image", "-m", help="Caminho do mockup visual (PNG/JPEG/WEBP) para síntese multimodal.")
    p.add_argument("--output", "-o", help="Caminho do arquivo markdown de saída.")
    p.add_argument("--queue", "-q", action="store_true", help="Salva o prompt automaticamente como a próxima User Story sequencial na fila.")
    args = p.parse_args()

    try:
        res = run_synthesize_prompt(
            raw_idea=args.idea,
            role=args.role,
            output_file=args.output,
            image_path=args.image,
            queue=getattr(args, "queue", False),
        )
        if not args.output:
            print(res)
    except Exception as e:
        log_error("ANTIGRAVITY", str(e))
        sys.exit(1)


if __name__ == "__main__":
    main()
