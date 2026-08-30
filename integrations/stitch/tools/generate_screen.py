#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🎨 AMB_V2 - Stitch SDK: Geração de Tela a partir de Prompt (SRP)
Localização: amb_v2/integrations/stitch/tools/generate_screen.py
Responsabilidade Única: Enviar uma descrição textual para o Google Stitch SDK e
retornar os dados da tela gerada (ID, screenshot, HTML e metadados).
"""

import os
import sys
import json
import argparse
import subprocess

# Configuração de sys.path para importação de 00_setup_config
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

from config import Colors, log, log_error, require_env, get_env, ApiExecutionError


def generate_screen(
    prompt: str,
    project_id: str = None,
    device_type: str = "DESKTOP",
    model_id: str = "GEMINI_3_1_PRO",
    design_system: str = None
) -> dict:
    """Invoca o Stitch SDK para gerar uma nova tela visual."""
    require_env("STITCH_API_KEY")
    resolved_project_id = project_id or require_env("STITCH_PROJECT_ID")

    # Localiza o runner no client/ ou na raiz do módulo
    runner_candidates = [
        os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "client", "stitch_client.mjs")),
        os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "stitch_client.mjs")),
    ]
    runner_path = next((p for p in runner_candidates if os.path.exists(p)), None)
    if not runner_path:
        raise ApiExecutionError(f"Runner Stitch não encontrado em {runner_candidates[0]}")

    payload = {
        "projectId": resolved_project_id,
        "prompt": prompt,
        "deviceType": device_type,
        "modelId": model_id
    }
    if design_system:
        payload["designSystem"] = design_system

    log("STITCH", f"Gerando nova tela no projeto {resolved_project_id} ({device_type})...", Colors.CYAN)
    
    proc = subprocess.run(
        ["node", runner_path, "generate_screen", json.dumps(payload)],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace"
    )

    if proc.returncode != 0:
        err_msg = proc.stderr.strip() or proc.stdout.strip()
        try:
            err_json = json.loads(err_msg)
            err_msg = err_json.get("error", err_msg)
        except Exception:
            pass
        raise ApiExecutionError(f"Falha ao gerar tela no Stitch: {err_msg}")

    try:
        data = json.loads(proc.stdout.strip())
        return data
    except Exception as e:
        raise ApiExecutionError(f"Resposta inválida do Stitch SDK: {e}\nSaída bruta: {proc.stdout}")


def main():
    parser = argparse.ArgumentParser(description="Gera uma nova tela visual no Google Stitch SDK.")
    parser.add_argument("--prompt", "-p", required=True, help="Descrição da tela e elementos visuais a serem gerados.")
    parser.add_argument("--project-id", help="ID do projeto Stitch (padrão: STITCH_PROJECT_ID do .env).")
    parser.add_argument("--device", choices=["DESKTOP", "MOBILE", "TABLET"], default="DESKTOP", help="Tipo de viewport.")
    parser.add_argument("--json", action="store_true", help="Retorna saída em formato JSON puro.")

    args = parser.parse_args()

    try:
        res = generate_screen(
            prompt=args.prompt,
            project_id=args.project_id,
            device_type=args.device
        )
        if args.json:
            print(json.dumps(res, indent=2))
        else:
            log("STITCH", f"✅ Tela gerada com sucesso!", Colors.GREEN)
            print(f"  • Screen ID:      {Colors.BOLD}{res.get('screenId')}{Colors.RESET}")
            print(f"  • Título:         {res.get('title') or 'Sem título'}")
            print(f"  • Screenshot URL: {res.get('screenshotUrl') or 'N/A'}")
            print(f"  • HTML Gerado:    {'Sim (' + str(len(res.get('htmlCode', ''))) + ' bytes)' if res.get('htmlCode') else 'Não'}")
    except Exception as e:
        log_error("STITCH", str(e))
        sys.exit(1)


if __name__ == "__main__":
    main()
