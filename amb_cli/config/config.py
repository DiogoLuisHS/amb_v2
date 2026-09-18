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
from amb_cli.workspace.project_context import (
    find_repo_root,
    load_project_json,
    get_repo_name,
    get_device_type
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
