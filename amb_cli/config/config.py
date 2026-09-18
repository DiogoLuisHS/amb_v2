#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
⚙️ AMB_V2 - Fachada de Compatibilidade Reversa (Facade)
Responsabilidade Única: Ponto central de diagnóstico do ambiente (`amb check`)
e reexportação de símbolos das camadas core e workspace (F1-M6 - SRP).
"""

from typing import Dict, Any, Optional

# --- Importações da Camada Core ---
from amb_cli.core import (
    Colors,
    AmbError,
    ConfigurationError,
    ApiExecutionError,
    log,
    log_error,
    load_env_file,
    require_env
)
from amb_cli.core.env import get_env as core_get_env

# --- Importações da Camada Workspace ---
from amb_cli.workspace.project_context import (
    find_repo_root,
    load_project_json,
    get_repo_name,
    get_device_type
)
from amb_cli.workspace.design_tokens import (
    parse_design_tokens_from_text,
    get_design_system_config
)

def get_env(key: str, default: Optional[str] = None) -> Optional[str]:
    """Obtém variável de ambiente ou faz fallback para metadata de projeto."""
    val = core_get_env(key)
    if val is not None:
        return val

    p_meta = load_project_json()
    if p_meta and key in p_meta and str(p_meta[key]).strip():
        return str(p_meta[key]).strip()

    return default

def main(as_json: bool = False):
    """Valida e exibe o checklist visual de configurações chamando a função core."""
    from amb_cli.config.config_core.env_diagnostics import run_environment_diagnostics
    return run_environment_diagnostics(as_json=as_json)

if __name__ == "__main__":
    main()
