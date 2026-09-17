# -*- coding: utf-8 -*-
"""
Gerenciamento de projetos no Stitch SDK.
"""

from typing import Dict, Any, List, Optional
from config import Colors, log, require_env


def get_project_core(client: Any, project_id: Optional[str] = None) -> Dict[str, Any]:
    """Obtém metadados do projeto e do Design System no Stitch."""
    proj_id = project_id or client.project_id or require_env("STITCH_PROJECT_ID")
    payload = {"name": f"projects/{proj_id}", "projectId": proj_id}
    log("STITCH", f"Consultando metadados do projeto {proj_id}...", Colors.CYAN)
    return client._run_node_command("get_project", payload)


def create_project_core(client: Any, title: Optional[str] = None) -> Dict[str, Any]:
    """Cria um novo projeto/workspace no Stitch SDK."""
    payload = {}
    if title:
        payload["title"] = title
    log("STITCH", f"Criando novo projeto no Stitch{' (' + title + ')' if title else ''}...", Colors.CYAN)
    return client._run_node_command("create_project", payload)


def list_projects_core(client: Any, filter_view: Optional[str] = None) -> List[Dict[str, Any]]:
    """Lista todos os projetos Stitch acessíveis ao usuário."""
    payload = {}
    if filter_view:
        payload["filter"] = filter_view
    log("STITCH", "Listando projetos Stitch...", Colors.CYAN)
    res = client._run_node_command("list_projects", payload)
    if isinstance(res, dict) and "projects" in res:
        return res["projects"]
    if isinstance(res, list):
        return res
    return []
