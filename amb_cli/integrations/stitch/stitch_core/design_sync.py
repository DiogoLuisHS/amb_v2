import os
from typing import Dict, Any, List, Optional

from core import (
    Colors,
    log,
    require_env,
    ApiExecutionError,
)
from workspace import (
    find_repo_root,
    get_design_system_config,
    load_project_json,
)

def create_design_system_core(client: Any, design_system: Dict[str, Any], project_id: Optional[str] = None) -> Dict[str, Any]:
    """Cria um novo Design System no Stitch através da tool oficial create_design_system."""
    proj_id = project_id or client.project_id or require_env("STITCH_PROJECT_ID")
    payload = {
        "projectId": proj_id,
        "designSystem": design_system
    }
    log("STITCH-DS", f"Criando Design System no projeto {proj_id}...", Colors.CYAN)
    return client._run_node_command("create_design_system", payload)

def update_design_system_core(client: Any, asset_name: str, design_system: Dict[str, Any], project_id: Optional[str] = None) -> Dict[str, Any]:
    """Atualiza um Design System existente no Stitch através da tool oficial update_design_system."""
    proj_id = project_id or client.project_id or require_env("STITCH_PROJECT_ID")
    canonical_name = asset_name if asset_name.startswith("assets/") else f"assets/{asset_name}"
    payload = {
        "name": canonical_name,
        "projectId": proj_id,
        "designSystem": design_system
    }
    log("STITCH-DS", f"Atualizando Design System {canonical_name} no projeto {proj_id}...", Colors.CYAN)
    return client._run_node_command("update_design_system", payload)

def list_design_systems_core(client: Any, project_id: Optional[str] = None) -> List[Dict[str, Any]]:
    """Lista todos os Design Systems associados ao projeto ativo."""
    proj_id = project_id or client.project_id or require_env("STITCH_PROJECT_ID")
    payload = {"projectId": proj_id}
    log("STITCH-DS", f"Consultando Design Systems do projeto {proj_id}...", Colors.CYAN)
    res = client._run_node_command("list_design_systems", payload)
    if isinstance(res, dict) and "designSystems" in res:
        return res["designSystems"]
    if isinstance(res, list):
        return res
    return []

def apply_design_system_core(
    client: Any,
    asset_id: str,
    selected_screen_instances: List[Dict[str, str]],
    project_id: Optional[str] = None
) -> Dict[str, Any]:
    """Aplica o Design System às instâncias de tela selecionadas via apply_design_system."""
    proj_id = project_id or client.project_id or require_env("STITCH_PROJECT_ID")
    clean_asset_id = asset_id.replace("assets/", "")
    payload = {
        "projectId": proj_id,
        "assetId": clean_asset_id,
        "selectedScreenInstances": selected_screen_instances
    }
    log("STITCH-DS", f"Aplicando Design System {clean_asset_id} a {len(selected_screen_instances)} tela(s)...", Colors.CYAN)
    return client._run_node_command("apply_design_system", payload)

def sync_design_system_core(
    client: Any,
    design_md_path: Optional[str] = None,
    design_system: Optional[Dict[str, Any]] = None,
    **overrides
) -> Dict[str, Any]:
    """Sincroniza arquivo design.md e tokens do projeto com o Design System oficial do Stitch."""
    project_id = client.project_id or require_env("STITCH_PROJECT_ID")
    root = find_repo_root()
    default_paths = [
        design_md_path,
        os.path.join(root, "design.md"),
        os.path.join(root, "docs", "design.md"),
        os.path.join(root, ".antigravity", "rules", "design.md"),
    ]
    resolved_file = next((p for p in default_paths if p and os.path.exists(p)), None)

    design_md_text = ""
    if resolved_file:
        with open(resolved_file, "r", encoding="utf-8", errors="replace") as f:
            design_md_text = f.read()
        log("STITCH-DS", f"Lendo especificações de design de {resolved_file}...", Colors.CYAN)
    elif not design_system:
        raise ApiExecutionError("Arquivo design.md ou especificação de Design System não encontrado no projeto.")

    # Carrega configuração e tokens definidos estritamente pelo projeto consumidor
    project_cfg = get_design_system_config(default_file=resolved_file)

    # Mescla com overrides explícitos fornecidos pelo chamador
    merged_cfg = {**project_cfg, **{k: v for k, v in overrides.items() if v is not None}}

    if design_system and isinstance(design_system, dict):
        design_system_spec = dict(design_system)
        if "theme" not in design_system_spec:
            design_system_spec["theme"] = {}
        if design_md_text and "designMd" not in design_system_spec["theme"]:
            design_system_spec["theme"]["designMd"] = design_md_text
    else:
        theme_dict: Dict[str, Any] = {}
        for k_target, k_sources in [
            ("colorMode", ["colorMode", "color_mode"]),
            ("headlineFont", ["headlineFont", "headline_font"]),
            ("bodyFont", ["bodyFont", "body_font"]),
            ("roundness", ["roundness"]),
            ("customColor", ["customColor", "custom_color", "primary_color"]),
        ]:
            val = next((merged_cfg[s] for s in k_sources if s in merged_cfg and merged_cfg[s]), None)
            if val:
                theme_dict[k_target] = val

        if design_md_text:
            theme_dict["designMd"] = design_md_text

        display_name = (
            merged_cfg.get("displayName")
            or merged_cfg.get("display_name")
            or load_project_json().get("name")
            or "Design System"
        )

        design_system_spec = {
            "displayName": display_name,
            "theme": theme_dict
        }

    log("STITCH-DS", f"Sincronizando Design System com o projeto Stitch {project_id}...", Colors.CYAN)

    try:
        existing_systems = client.list_design_systems(project_id=project_id)
    except Exception:
        existing_systems = []

    if existing_systems and len(existing_systems) > 0:
        first_asset = existing_systems[0]
        asset_name = first_asset.get("name") or f"assets/{first_asset.get('assetId', '')}"
        log("STITCH-DS", f"Atualizando Design System existente ({asset_name})...", Colors.CYAN)
        return update_design_system_core(client, asset_name, design_system_spec, project_id=project_id)
    else:
        log("STITCH-DS", "Criando novo Design System para o projeto...", Colors.CYAN)
        return create_design_system_core(client, design_system_spec, project_id=project_id)
