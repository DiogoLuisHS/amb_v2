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

from config import (
    Colors,
    log,
    log_error,
    require_env,
    get_env,
    get_device_type,
    ApiExecutionError,
    ConfigurationError
)
from amb_cli.integrations.stitch.stitch_core.asset_manager import download_assets_core, upload_asset_core
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

    @staticmethod
    def save_screen_html(screen_data: Dict[str, Any], output_path: str) -> str:
        """Salva o DOM HTML extraído da tela em um arquivo local."""
        html_code = screen_data.get("htmlCode", "")
        if not html_code:
            for msg in screen_data.get("messages", []):
                if "<html" in msg or "<div" in msg:
                    html_code = msg
                    break

        out_abs = os.path.abspath(output_path)
        os.makedirs(os.path.dirname(out_abs), exist_ok=True)
        with open(out_abs, "w", encoding="utf-8") as f:
            f.write(html_code or "<!-- Nenhum código HTML extraído do Stitch -->\n")
        log("STITCH", f"Código HTML salvo em: {out_abs}", Colors.GREEN)
        return out_abs

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
        proj_id = project_id or self.project_id or require_env("STITCH_PROJECT_ID")
        payload = {"name": f"projects/{proj_id}", "projectId": proj_id}
        log("STITCH", f"Consultando metadados do projeto {proj_id}...", Colors.CYAN)
        return self._run_node_command("get_project", payload)

    def create_project(self, title: Optional[str] = None) -> Dict[str, Any]:
        """Cria um novo projeto/workspace no Stitch SDK."""
        payload = {}
        if title:
            payload["title"] = title
        log("STITCH", f"Criando novo projeto no Stitch{' (' + title + ')' if title else ''}...", Colors.CYAN)
        return self._run_node_command("create_project", payload)

    def list_projects(self, filter_view: Optional[str] = None) -> List[Dict[str, Any]]:
        """Lista todos os projetos Stitch acessíveis ao usuário."""
        payload = {}
        if filter_view:
            payload["filter"] = filter_view
        log("STITCH", "Listando projetos Stitch...", Colors.CYAN)
        res = self._run_node_command("list_projects", payload)
        if isinstance(res, dict) and "projects" in res:
            return res["projects"]
        if isinstance(res, list):
            return res
        return []

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
def generate_screen(prompt: str, **kwargs) -> Dict[str, Any]:
    return StitchClient().generate_screen(prompt, **kwargs)

def edit_screen(screen_id: str, prompt: str, **kwargs) -> Dict[str, Any]:
    return StitchClient().edit_screen(screen_id, prompt, **kwargs)

def get_screen(screen_id: str, **kwargs) -> Dict[str, Any]:
    return StitchClient().get_screen(screen_id, **kwargs)

def list_screens(project_id: Optional[str] = None) -> List[Dict[str, Any]]:
    return StitchClient().list_screens(project_id)

def get_project(project_id: Optional[str] = None) -> Dict[str, Any]:
    return StitchClient().get_project(project_id)

def create_project(title: Optional[str] = None) -> Dict[str, Any]:
    return StitchClient().create_project(title)

def list_projects(filter_view: Optional[str] = None) -> List[Dict[str, Any]]:
    return StitchClient().list_projects(filter_view)

def generate_variants(screen_id: str, prompt: str, count: int = 3, **kwargs) -> Dict[str, Any]:
    return StitchClient().generate_variants(screen_id, prompt, variant_count=count, **kwargs)

def download_assets(output_dir: str, project_id: Optional[str] = None) -> Dict[str, Any]:
    return StitchClient().download_assets(output_dir, project_id)

def upload_asset(file_path: str, project_id: Optional[str] = None) -> Dict[str, Any]:
    return StitchClient().upload_asset(file_path, project_id)

def create_design_system(design_system: Dict[str, Any], project_id: Optional[str] = None) -> Dict[str, Any]:
    return StitchClient().create_design_system(design_system, project_id)

def update_design_system(asset_name: str, design_system: Dict[str, Any], project_id: Optional[str] = None) -> Dict[str, Any]:
    return StitchClient().update_design_system(asset_name, design_system, project_id)

def list_design_systems(project_id: Optional[str] = None) -> List[Dict[str, Any]]:
    return StitchClient().list_design_systems(project_id)

def apply_design_system(asset_id: str, selected_screen_instances: List[Dict[str, str]], project_id: Optional[str] = None) -> Dict[str, Any]:
    return StitchClient().apply_design_system(asset_id, selected_screen_instances, project_id)

def sync_design_system(design_md_path: Optional[str] = None, **kwargs) -> Dict[str, Any]:
    return StitchClient().sync_design_system(design_md_path, **kwargs)

def call_tool(tool_name: str, payload: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    return StitchClient().call_tool(tool_name, payload)

