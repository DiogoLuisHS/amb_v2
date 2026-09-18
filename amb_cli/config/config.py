#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
⚙️ AMB_V2 - Utilitário Central de Configuração, Logging e Fail-Fast (SRP)
Responsabilidade Única: Carregar variáveis, validar requisitos estritos e fornecer
diagnósticos imediatos sem mascaramento de falhas.
"""

from typing import Dict, Any, Optional

from amb_cli.core import (
    Colors,
    AmbError,
    ConfigurationError,
    ApiExecutionError,
    log,
    log_error,
    load_env_file,
    get_env,
    require_env
)
from amb_cli.core.env import find_repo_root, load_project_json

def get_device_type(default: Optional[str] = None) -> Optional[str]:
    """Obtém o tipo de dispositivo alvo configurado pelo usuário para o Stitch."""
    dev = get_env("STITCH_DEVICE_TYPE") or get_env("DEVICE_TYPE")
    if dev and dev.strip():
        return dev.strip().upper()
    p_meta = load_project_json()
    stitch_cfg = p_meta.get("stitch", {})
    if isinstance(stitch_cfg, dict) and stitch_cfg.get("device"):
        return str(stitch_cfg["device"]).strip().upper()
    if "device_type" in p_meta and p_meta["device_type"]:
        return str(p_meta["device_type"]).strip().upper()
    return default


def get_repo_name() -> str:
    """Obtém o nome do repositório configurado no .env (GITHUB_REPOSITORY)."""
    repo = get_env("GITHUB_REPOSITORY")
    if repo:
        return repo
    p_meta = load_project_json()
    if "repository" in p_meta and p_meta["repository"]:
        return p_meta["repository"]
    raise ConfigurationError(
        "Variável GITHUB_REPOSITORY não configurada.",
        hint="Defina GITHUB_REPOSITORY=usuario/repo no seu arquivo .env"
    )

def parse_design_tokens_from_text(text: str) -> Dict[str, Any]:
    """Extrai tokens e diretrizes de design básicos de um texto Markdown (ex: design.md)."""
    from amb_cli.config.config_core.design_tokens import parse_design_tokens_from_text as _parse
    return _parse(text)

def get_design_system_config(default_file: Optional[str] = None) -> Dict[str, Any]:
    """Resolve as configurações de Design System estritamente a partir das orientações do projeto."""
    from amb_cli.config.config_core.design_tokens import get_design_system_config as _get
    return _get(default_file)

def main(as_json: bool = False):
    """Valida e exibe o checklist visual de configurações chamando a função core."""
    from amb_cli.config.config_core.env_diagnostics import run_environment_diagnostics
    return run_environment_diagnostics(as_json=as_json)

if __name__ == "__main__":
    main()
