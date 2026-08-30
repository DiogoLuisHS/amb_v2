#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🎨 AMB_V2 - Stitch SDK: Sincronização de Design Tokens e Markdown (SRP)
Localização: amb_v2/integrations/stitch/tools/sync_design_system.py
Responsabilidade Única: Fazer upload de um arquivo design.md para gerar/atualizar o Design System no Stitch.
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

from config import Colors, log, log_error, require_env, find_repo_root, ApiExecutionError


def sync_design_system(
    design_md_path: str = None,
    project_id: str = None
) -> dict:
    """Lê o arquivo markdown com regras visuais e sincroniza com o Stitch."""
    require_env("STITCH_API_KEY")
    resolved_project_id = project_id or require_env("STITCH_PROJECT_ID")

    root = find_repo_root()
    default_paths = [
        os.path.join(root, "design.md"),
        os.path.join(root, "docs", "design.md"),
        os.path.join(root, ".antigravity", "rules", "design.md"),
    ]
    resolved_file = design_md_path or next((p for p in default_paths if os.path.exists(p)), None)

    if not resolved_file or not os.path.exists(resolved_file):
        raise ApiExecutionError(
            f"Arquivo design.md não encontrado.",
            hint="Crie um arquivo design.md com as diretrizes de cores e tipografia ou passe --file caminho/para/design.md"
        )

    with open(resolved_file, "r", encoding="utf-8") as f:
        md_content = f.read()

    runner_candidates = [
        os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "client", "stitch_client.mjs")),
        os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "stitch_client.mjs")),
    ]
    runner_path = next((p for p in runner_candidates if os.path.exists(p)), None)

    payload = {
        "projectId": resolved_project_id,
        "designMd": md_content
    }

    log("STITCH-DS", f"Sincronizando {resolved_file} com o projeto Stitch {resolved_project_id}...", Colors.CYAN)

    proc = subprocess.run(
        ["node", runner_path, "create_design_system_from_design_md", json.dumps(payload)],
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
        raise ApiExecutionError(f"Falha ao sincronizar Design System no Stitch: {err_msg}")

    return json.loads(proc.stdout.strip())


def main():
    parser = argparse.ArgumentParser(description="Sincroniza um arquivo design.md com o Design System do Stitch.")
    parser.add_argument("--file", "-f", help="Caminho para o arquivo design.md (padrão: busca automática).")
    parser.add_argument("--project-id", help="ID do projeto Stitch.")
    parser.add_argument("--json", action="store_true", help="Retorna saída JSON.")

    args = parser.parse_args()

    try:
        res = sync_design_system(design_md_path=args.file, project_id=args.project_id)
        if args.json:
            print(json.dumps(res, indent=2))
        else:
            log("STITCH-DS", "✅ Design System sincronizado com sucesso!", Colors.GREEN)
    except Exception as e:
        log_error("STITCH-DS", str(e))
        sys.exit(1)


if __name__ == "__main__":
    main()
