#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🎨 AMB_V2 - Stitch SDK: Edição e Refinamento de Tela Existente (SRP)
Localização: amb_v2/integrations/stitch/tools/edit_screen.py
Responsabilidade Única: Modificar/refinar elementos específicos de uma tela existente no Stitch.
"""

import os
import sys
import json
import argparse
import subprocess

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

from config import Colors, log, log_error, require_env, ApiExecutionError


def edit_screen(
    screen_id: str,
    prompt: str,
    project_id: str = None,
    device_type: str = "DESKTOP"
) -> dict:
    """Aplica edições em uma tela já existente."""
    require_env("STITCH_API_KEY")
    resolved_project_id = project_id or require_env("STITCH_PROJECT_ID")

    runner_candidates = [
        os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "client", "stitch_client.mjs")),
        os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "stitch_client.mjs")),
    ]
    runner_path = next((p for p in runner_candidates if os.path.exists(p)), None)

    payload = {
        "projectId": resolved_project_id,
        "selectedScreenIds": [screen_id],
        "prompt": prompt,
        "deviceType": device_type
    }

    log("STITCH-EDIT", f"Refinando tela {screen_id} no projeto {resolved_project_id}...", Colors.CYAN)

    proc = subprocess.run(
        ["node", runner_path, "edit_screen", json.dumps(payload)],
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
        raise ApiExecutionError(f"Falha ao editar tela no Stitch: {err_msg}")

    return json.loads(proc.stdout.strip())


def main():
    parser = argparse.ArgumentParser(description="Edita e refina uma tela existente no Google Stitch.")
    parser.add_argument("--screen-id", "-s", required=True, help="ID da tela a ser editada.")
    parser.add_argument("--prompt", "-p", required=True, help="Instruções de edição/ajuste visual.")
    parser.add_argument("--project-id", help="ID do projeto Stitch (padrão: STITCH_PROJECT_ID do .env).")
    parser.add_argument("--json", action="store_true", help="Retorna saída JSON.")

    args = parser.parse_args()

    try:
        res = edit_screen(
            screen_id=args.screen_id,
            prompt=args.prompt,
            project_id=args.project_id
        )
        if args.json:
            print(json.dumps(res, indent=2))
        else:
            log("STITCH-EDIT", "✅ Tela refinada com sucesso!", Colors.GREEN)
            print(f"  • Screen ID Resultante: {res.get('screenId')}")
            print(f"  • Screenshot URL:       {res.get('screenshotUrl') or 'N/A'}")
    except Exception as e:
        log_error("STITCH-EDIT", str(e))
        sys.exit(1)


if __name__ == "__main__":
    main()
