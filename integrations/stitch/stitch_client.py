#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🎨 AMB_V2 - Google Stitch SDK Client & Tooling (SRP)
Localização: amb_v2/integrations/stitch/stitch_client.py
Responsabilidade Única: Interface Python unificada para geração de telas, refinamentos,
variantes visuais e sincronização de Design Tokens via Stitch Runner Node.js.
"""

import os
import sys
import json
import subprocess
from typing import Dict, Any, Optional

from config import Colors, log, log_error, require_env, get_env, find_repo_root, ApiExecutionError


class StitchClient:
    """Client oficial para o Google Stitch SDK."""

    def __init__(self, project_id: Optional[str] = None):
        self.api_key = require_env("STITCH_API_KEY")
        self.project_id = project_id or get_env("STITCH_PROJECT_ID")
        self.runner_path = self._resolve_runner()

    def _resolve_runner(self) -> str:
        candidates = [
            os.path.abspath(os.path.join(os.path.dirname(__file__), "stitch_client.mjs")),
            os.path.abspath(os.path.join(os.path.dirname(__file__), "client", "stitch_client.mjs")),
        ]
        runner = next((p for p in candidates if os.path.exists(p)), None)
        if not runner:
            raise ApiExecutionError(f"Runner Stitch (stitch_client.mjs) não encontrado em {candidates[0]}")
        return runner

    def _run_node_command(self, action: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Executa comando no runner Node.js do Stitch SDK."""
        proc = subprocess.run(
            ["node", self.runner_path, action, json.dumps(payload)],
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
            raise ApiExecutionError(f"Falha na execução do Stitch SDK ({action}): {err_msg}")

        try:
            return json.loads(proc.stdout.strip())
        except json.JSONDecodeError:
            return {"output": proc.stdout.strip()}

    def generate_screen(
        self,
        prompt: str,
        device_type: str = "DESKTOP",
        model_id: str = "GEMINI_3_1_PRO",
        design_system: Optional[str] = None
    ) -> Dict[str, Any]:
        """Gera uma nova tela visual a partir de uma descrição textual."""
        project_id = self.project_id or require_env("STITCH_PROJECT_ID")
        payload = {
            "projectId": project_id,
            "prompt": prompt,
            "deviceType": device_type,
            "modelId": model_id,
        }
        if design_system:
            payload["designSystem"] = design_system

        log("STITCH", f"Disparando geração de nova tela visual ({device_type})...", Colors.CYAN)
        res = self._run_node_command("generate_screen", payload)
        return res

    def edit_screen(self, screen_id: str, prompt: str) -> Dict[str, Any]:
        """Refina e edita uma tela existente com novas instruções visuais."""
        project_id = self.project_id or require_env("STITCH_PROJECT_ID")
        payload = {
            "projectId": project_id,
            "screenId": screen_id,
            "prompt": prompt
        }
        log("STITCH", f"Refinando tela {screen_id}...", Colors.CYAN)
        res = self._run_node_command("edit_screen", payload)
        return res

    def get_screen(self, screen_id: str) -> Dict[str, Any]:
        """Obtém detalhes, DOM HTML e screenshot de uma tela."""
        project_id = self.project_id or require_env("STITCH_PROJECT_ID")
        payload = {
            "projectId": project_id,
            "screenId": screen_id
        }
        log("STITCH", f"Consultando detalhes da tela {screen_id}...", Colors.CYAN)
        res = self._run_node_command("get_screen", payload)
        return res

    def generate_variants(self, screen_id: str, prompt: str = "Explorar variações visuais", variant_count: int = 3) -> Dict[str, Any]:
        """Gera variantes visuais exploratórias a partir de uma tela."""
        project_id = self.project_id or require_env("STITCH_PROJECT_ID")
        payload = {
            "projectId": project_id,
            "selectedScreenIds": [screen_id],
            "prompt": prompt,
            "variantOptions": {
                "variantCount": variant_count,
                "creativeRange": "EXPLORE"
            }
        }
        log("STITCH", f"Gerando {variant_count} variantes para a tela {screen_id}...", Colors.CYAN)
        res = self._run_node_command("generate_variants", payload)
        return res

    def sync_design_system(self, design_md_path: Optional[str] = None) -> Dict[str, Any]:
        """Sincroniza arquivo design.md com o Design System do Stitch."""
        project_id = self.project_id or require_env("STITCH_PROJECT_ID")
        root = find_repo_root()
        default_paths = [
            os.path.join(root, "design.md"),
            os.path.join(root, "docs", "design.md"),
            os.path.join(root, ".antigravity", "rules", "design.md"),
        ]
        resolved_file = design_md_path or next((p for p in default_paths if os.path.exists(p)), None)
        if not resolved_file or not os.path.exists(resolved_file):
            raise ApiExecutionError("Arquivo design.md não encontrado para sincronização de Design Tokens.")

        with open(resolved_file, "r", encoding="utf-8") as f:
            md_content = f.read()

        payload = {
            "projectId": project_id,
            "designMd": md_content
        }
        log("STITCH-DS", f"Sincronizando {resolved_file} com o projeto {project_id}...", Colors.CYAN)
        res = self._run_node_command("create_design_system_from_design_md", payload)
        return res


# Funções utilitárias avulsas para import direto
def generate_screen(prompt: str, **kwargs) -> Dict[str, Any]:
    return StitchClient().generate_screen(prompt, **kwargs)

def edit_screen(screen_id: str, prompt: str) -> Dict[str, Any]:
    return StitchClient().edit_screen(screen_id, prompt)

def get_screen(screen_id: str) -> Dict[str, Any]:
    return StitchClient().get_screen(screen_id)

def generate_variants(screen_id: str, prompt: str = "Explorar variações", count: int = 3) -> Dict[str, Any]:
    return StitchClient().generate_variants(screen_id, prompt, variant_count=count)

def sync_design_system(design_md_path: Optional[str] = None) -> Dict[str, Any]:
    return StitchClient().sync_design_system(design_md_path)
