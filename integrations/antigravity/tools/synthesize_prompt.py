#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🧠 AMB_V2 - Antigravity SDK: Síntese Cognitiva de Prompts (SRP)
Localização: amb_v2/integrations/antigravity/tools/synthesize_prompt.py
Responsabilidade Única: Transformar ideias informais em prompts estruturados para Jules/Stitch.
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

from config import Colors, log, log_error, find_repo_root
from antigravity_client import AntigravityClient


def synthesize_prompt(raw_idea: str, role: str = "general") -> str:
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

Gere o prompt executivo final."""

    client = AntigravityClient()
    return client.generate_text(prompt=prompt, system_instruction=system_instruction)


def main():
    parser = argparse.ArgumentParser(description="Sintetiza um prompt informal em especificação técnica estruturada.")
    parser.add_argument("--raw", "-r", required=True, help="Texto da ideia informal.")
    parser.add_argument("--role", default="general", help="Especialidade do agente (ex: refactor, a11y, feature, deadwood).")

    args = parser.parse_args()

    try:
        log("ANTIGRAVITY-SYNTH", "Sintetizando prompt executivo com IA...", Colors.CYAN)
        res = synthesize_prompt(raw_idea=args.raw, role=args.role)
        print("\n" + "=" * 75)
        print(f"{Colors.BOLD}{Colors.GREEN}PROMPT EXECUTIVO SINTETIZADO:{Colors.RESET}")
        print("=" * 75)
        print(res)
        print("=" * 75)
    except Exception as e:
        log_error("ANTIGRAVITY-SYNTH", str(e))
        sys.exit(1)


if __name__ == "__main__":
    main()
