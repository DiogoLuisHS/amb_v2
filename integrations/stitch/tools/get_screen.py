#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🎨 AMB_V2 - Stitch SDK: Download de Assets e Código HTML da Tela (SRP)
Localização: amb_v2/integrations/stitch/tools/get_screen.py
Responsabilidade Única: Baixar o código HTML e salvar localmente o screenshot de uma tela Stitch.
"""

import os
import sys
import json
import argparse
import subprocess
import urllib.request

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


def get_screen(
    screen_id: str,
    project_id: str = None,
    save_dir: str = None
) -> dict:
    """Recupera os detalhes da tela e baixa seus assets se solicitado."""
    require_env("STITCH_API_KEY")
    resolved_project_id = project_id or require_env("STITCH_PROJECT_ID")

    runner_candidates = [
        os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "client", "stitch_client.mjs")),
        os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "stitch_client.mjs")),
    ]
    runner_path = next((p for p in runner_candidates if os.path.exists(p)), None)

    payload = {
        "projectId": resolved_project_id,
        "screenId": screen_id
    }

    log("STITCH-GET", f"Consultando tela {screen_id}...", Colors.CYAN)

    proc = subprocess.run(
        ["node", runner_path, "get_screen", json.dumps(payload)],
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
        raise ApiExecutionError(f"Falha ao consultar tela no Stitch: {err_msg}")

    data = json.loads(proc.stdout.strip())

    if save_dir:
        os.makedirs(save_dir, exist_ok=True)
        # Salva HTML
        if data.get("htmlCode"):
            html_file = os.path.join(save_dir, f"screen_{screen_id}.html")
            with open(html_file, "w", encoding="utf-8") as f:
                f.write(data["htmlCode"])
            log("STITCH-GET", f"HTML salvo em: {html_file}", Colors.GREEN)

        # Salva Screenshot
        if data.get("screenshotUrl"):
            img_file = os.path.join(save_dir, f"screen_{screen_id}.png")
            try:
                urllib.request.urlretrieve(data["screenshotUrl"], img_file)
                log("STITCH-GET", f"Screenshot salvo em: {img_file}", Colors.GREEN)
            except Exception as e:
                log_error("STITCH-GET", f"Não foi possível baixar screenshot: {e}")

    return data


def main():
    parser = argparse.ArgumentParser(description="Consulta e baixa assets de uma tela do Google Stitch.")
    parser.add_argument("--screen-id", "-s", required=True, help="ID da tela Stitch.")
    parser.add_argument("--project-id", help="ID do projeto Stitch.")
    parser.add_argument("--save-dir", "-d", help="Diretório local para salvar HTML e Screenshot baixados.")
    parser.add_argument("--json", action="store_true", help="Retorna saída JSON.")

    args = parser.parse_args()

    try:
        res = get_screen(
            screen_id=args.screen_id,
            project_id=args.project_id,
            save_dir=args.save_dir
        )
        if args.json:
            print(json.dumps(res, indent=2))
        else:
            log("STITCH-GET", "✅ Detalhes da tela obtidos:", Colors.GREEN)
            print(f"  • Screen ID:      {res.get('screenId')}")
            print(f"  • Título:         {res.get('title') or 'Sem título'}")
            print(f"  • Screenshot URL: {res.get('screenshotUrl') or 'N/A'}")
    except Exception as e:
        log_error("STITCH-GET", str(e))
        sys.exit(1)


if __name__ == "__main__":
    main()
