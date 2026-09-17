# -*- coding: utf-8 -*-
"""
Funções utilitárias avulsas para import direto do ecossistema Stitch.
"""

from typing import Dict, Any, List, Optional


def generate_screen(prompt: str, **kwargs) -> Dict[str, Any]:
    from ..stitch_client import StitchClient
    return StitchClient().generate_screen(prompt, **kwargs)


def edit_screen(screen_id: str, prompt: str, **kwargs) -> Dict[str, Any]:
    from ..stitch_client import StitchClient
    return StitchClient().edit_screen(screen_id, prompt, **kwargs)


def get_screen(screen_id: str, **kwargs) -> Dict[str, Any]:
    from ..stitch_client import StitchClient
    return StitchClient().get_screen(screen_id, **kwargs)


def list_screens(project_id: Optional[str] = None) -> List[Dict[str, Any]]:
    from ..stitch_client import StitchClient
    return StitchClient().list_screens(project_id)


def get_project(project_id: Optional[str] = None) -> Dict[str, Any]:
    from ..stitch_client import StitchClient
    return StitchClient().get_project(project_id)


def create_project(title: Optional[str] = None) -> Dict[str, Any]:
    from ..stitch_client import StitchClient
    return StitchClient().create_project(title)


def list_projects(filter_view: Optional[str] = None) -> List[Dict[str, Any]]:
    from ..stitch_client import StitchClient
    return StitchClient().list_projects(filter_view)


def generate_variants(screen_id: str, prompt: str, count: int = 3, **kwargs) -> Dict[str, Any]:
    from ..stitch_client import StitchClient
    return StitchClient().generate_variants(screen_id, prompt, variant_count=count, **kwargs)


def download_assets(output_dir: str, project_id: Optional[str] = None) -> Dict[str, Any]:
    from ..stitch_client import StitchClient
    return StitchClient().download_assets(output_dir, project_id)


def upload_asset(file_path: str, project_id: Optional[str] = None) -> Dict[str, Any]:
    from ..stitch_client import StitchClient
    return StitchClient().upload_asset(file_path, project_id)


def create_design_system(design_system: Dict[str, Any], project_id: Optional[str] = None) -> Dict[str, Any]:
    from ..stitch_client import StitchClient
    return StitchClient().create_design_system(design_system, project_id)


def update_design_system(asset_name: str, design_system: Dict[str, Any], project_id: Optional[str] = None) -> Dict[str, Any]:
    from ..stitch_client import StitchClient
    return StitchClient().update_design_system(asset_name, design_system, project_id)


def list_design_systems(project_id: Optional[str] = None) -> List[Dict[str, Any]]:
    from ..stitch_client import StitchClient
    return StitchClient().list_design_systems(project_id)


def apply_design_system(asset_id: str, selected_screen_instances: List[Dict[str, str]], project_id: Optional[str] = None) -> Dict[str, Any]:
    from ..stitch_client import StitchClient
    return StitchClient().apply_design_system(asset_id, selected_screen_instances, project_id)


def sync_design_system(design_md_path: Optional[str] = None, **kwargs) -> Dict[str, Any]:
    from ..stitch_client import StitchClient
    return StitchClient().sync_design_system(design_md_path, **kwargs)


def call_tool(tool_name: str, payload: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    from ..stitch_client import StitchClient
    return StitchClient().call_tool(tool_name, payload)
