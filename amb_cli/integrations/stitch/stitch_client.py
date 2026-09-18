#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🎨 AMB_V2 - Google Stitch SDK Client & Tooling (SRP)
Localização: amb_v2/integrations/stitch/stitch_client.py
Responsabilidade Única: Interface Python unificada para geração de telas, refinamentos,
variantes visuais, listagem de telas e sincronização de Design Tokens via Stitch Runner Node.js.
"""

import os
import sys
import json
import shutil
import subprocess
from typing import Dict, Any, List, Optional

from core import (
    Colors,
    log,
    log_error,
    require_env,
    get_env,
    ApiExecutionError,
    ConfigurationError,
)
from workspace import get_device_type
from amb_cli.integrations.stitch.stitch_core.asset_manager import (
    download_assets_core,
    upload_asset_core,
    save_screen_html_core,
)
from amb_cli.integrations.stitch.stitch_core.project_manager import (
    get_project_core,
    create_project_core,
    list_projects_core,
)
from amb_cli.integrations.stitch.stitch_core.design_sync import (
    create_design_system_core,
    update_design_system_core,
    list_design_systems_core,
    apply_design_system_core,
    sync_design_system_core
)


class StitchClient:
    """Client oficial para o Google Stitch SDK (@google/stitch-sdk)."""

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
        """Executa comando no runner Node.js do Stitch SDK com diagnóstico preventivo de runtime."""
        node_bin = shutil.which("node")
        if not node_bin:
            raise ConfigurationError(
                "Runtime Node.js não foi encontrado no PATH do sistema.",
                hint="Instale o Node.js (v18+) para utilizar as funcionalidades do Stitch SDK."
            )

        proc = subprocess.run(
            [node_bin, self.runner_path, action, json.dumps(payload)],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace"
        )
        if proc.returncode != 0:
            err_msg = proc.stderr.strip() or proc.stdout.strip()
            if "MODULE_NOT_FOUND" in err_msg or "Cannot find module" in err_msg:
                raise ConfigurationError(
                    "Dependência @google/stitch-sdk não encontrada no módulo do Stitch.",
                    hint="Execute 'npm install' no diretório 'integrations/stitch/' para instalar o SDK oficial."
                )
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

    save_screen_html = staticmethod(save_screen_html_core)

    def generate_screen(
        self,
        prompt: str,
        device_type: Optional[str] = None,
        model_id: Optional[str] = None,
        design_system: Optional[str] = None,
        output_file: Optional[str] = None
    ) -> Dict[str, Any]:
        """Gera uma nova tela visual a partir de uma descrição textual respeitando a preferência de dispositivo."""
        project_id = self.project_id or require_env("STITCH_PROJECT_ID")
        resolved_device = (device_type or get_device_type())
        payload = {
            "projectId": project_id,
            "prompt": prompt
        }
        if model_id:
            payload["modelId"] = model_id
        if resolved_device:
            payload["deviceType"] = resolved_device
        if design_system:
            payload["designSystem"] = design_system

        dev_label = f" ({resolved_device})" if resolved_device else ""
        log("STITCH", f"Disparando geração de nova tela visual{dev_label}...", Colors.CYAN)
        res = self._run_node_command("generate_screen_from_text", payload)
        if output_file and res.get("htmlCode"):
            self.save_screen_html(res, output_file)
        return res

    def edit_screen(
        self,
        screen_id: str,
        prompt: str,
        device_type: Optional[str] = None,
        model_id: Optional[str] = None,
        output_file: Optional[str] = None
    ) -> Dict[str, Any]:
        """Refina e edita uma tela existente com novas instruções visuais."""
        project_id = self.project_id or require_env("STITCH_PROJECT_ID")
        resolved_device = (device_type or get_device_type())
        payload = {
            "projectId": project_id,
            "selectedScreenIds": [screen_id],
            "prompt": prompt
        }
        if resolved_device:
            payload["deviceType"] = resolved_device
        if model_id:
            payload["modelId"] = model_id

        log("STITCH", f"Refinando tela {screen_id}...", Colors.CYAN)
        res = self._run_node_command("edit_screens", payload)
        if output_file and res.get("htmlCode"):
            self.save_screen_html(res, output_file)
        return res

    def get_screen(self, screen_id: str, output_file: Optional[str] = None) -> Dict[str, Any]:
        """Obtém detalhes, DOM HTML e screenshot de uma tela."""
        project_id = self.project_id or require_env("STITCH_PROJECT_ID")
        payload = {
            "projectId": project_id,
            "screenId": screen_id,
            "name": f"projects/{project_id}/screens/{screen_id}"
        }
        log("STITCH", f"Consultando detalhes da tela {screen_id}...", Colors.CYAN)
        res = self._run_node_command("get_screen", payload)
        if output_file and res.get("htmlCode"):
            self.save_screen_html(res, output_file)
        return res

    def list_screens(self, project_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Lista todas as telas criadas no projeto Stitch ativo."""
        proj_id = project_id or self.project_id or require_env("STITCH_PROJECT_ID")
        payload = {"projectId": proj_id}
        log("STITCH", f"Listando telas do projeto {proj_id}...", Colors.CYAN)
        res = self._run_node_command("list_screens", payload)
        if isinstance(res, dict) and "screens" in res:
            return res["screens"]
        if isinstance(res, list):
            return res
        return []

    def get_project(self, project_id: Optional[str] = None) -> Dict[str, Any]:
        """Obtém metadados do projeto e do Design System no Stitch."""
        return get_project_core(self, project_id)

    def create_project(self, title: Optional[str] = None) -> Dict[str, Any]:
        """Cria um novo projeto/workspace no Stitch SDK."""
        return create_project_core(self, title)

    def list_projects(self, filter_view: Optional[str] = None) -> List[Dict[str, Any]]:
        """Lista todos os projetos Stitch acessíveis ao usuário."""
        return list_projects_core(self, filter_view)


    def generate_variants(
        self,
        screen_id: str,
        prompt: str,
        variant_count: int = 3,
        creative_range: str = "EXPLORE",
        aspects: Optional[List[str]] = None,
        device_type: Optional[str] = None,
        model_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Gera variantes visuais exploratórias a partir de uma tela."""
        project_id = self.project_id or require_env("STITCH_PROJECT_ID")
        resolved_device = (device_type or get_device_type())
        payload = {
            "projectId": project_id,
            "selectedScreenIds": [screen_id],
            "prompt": prompt,
            "variantOptions": {
                "variantCount": variant_count,
                "creativeRange": creative_range
            }
        }
        if aspects:
            payload["variantOptions"]["aspects"] = aspects
        if resolved_device:
            payload["deviceType"] = resolved_device
        if model_id:
            payload["modelId"] = model_id

        log("STITCH", f"Gerando {variant_count} variantes para a tela {screen_id}...", Colors.CYAN)
        return self._run_node_command("generate_variants", payload)

    def download_assets(self, output_dir: str, project_id: Optional[str] = None) -> Dict[str, Any]:
        """Baixa todas as telas e assets do projeto Stitch para um diretório local."""
        return download_assets_core(self, output_dir, project_id)

    def upload_asset(self, file_path: str, project_id: Optional[str] = None) -> Dict[str, Any]:
        """Faz upload de asset visual ou documento para o projeto Stitch."""
        return upload_asset_core(self, file_path, project_id)

    def create_design_system(self, design_system: Dict[str, Any], project_id: Optional[str] = None) -> Dict[str, Any]:
        """Cria um novo Design System no Stitch."""
        return create_design_system_core(self, design_system, project_id)

    def update_design_system(self, asset_name: str, design_system: Dict[str, Any], project_id: Optional[str] = None) -> Dict[str, Any]:
        """Atualiza um Design System existente no Stitch."""
        return update_design_system_core(self, asset_name, design_system, project_id)

    def list_design_systems(self, project_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Lista todos os Design Systems associados ao projeto ativo."""
        return list_design_systems_core(self, project_id)

    def apply_design_system(
        self,
        asset_id: str,
        selected_screen_instances: List[Dict[str, str]],
        project_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Aplica o Design System às instâncias de tela selecionadas."""
        return apply_design_system_core(self, asset_id, selected_screen_instances, project_id)

    def sync_design_system(
        self,
        design_md_path: Optional[str] = None,
        design_system: Optional[Dict[str, Any]] = None,
        **overrides
    ) -> Dict[str, Any]:
        """Sincroniza arquivo design.md e tokens do projeto com o Design System oficial do Stitch."""
        return sync_design_system_core(self, design_md_path, design_system, **overrides)

    def call_tool(self, tool_name: str, payload: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Executa uma chamada direta e genérica a qualquer ferramenta do Stitch SDK."""
        p = dict(payload or {})
        if "projectId" not in p and self.project_id:
            p["projectId"] = self.project_id
        log("STITCH", f"Invocando tool '{tool_name}' no Stitch SDK...", Colors.CYAN)
        return self._run_node_command(tool_name, p)


# Funções utilitárias avulsas para import direto e compatibilidade retroativa
from amb_cli.integrations.stitch.stitch_core.helpers import (
    generate_screen,
    edit_screen,
    get_screen,
    list_screens,
    get_project,
    create_project,
    list_projects,
    generate_variants,
    download_assets,
    upload_asset,
    create_design_system,
    update_design_system,
    list_design_systems,
    apply_design_system,
    sync_design_system,
    call_tool,
)



