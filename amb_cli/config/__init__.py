#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Pacote de configurações e utilitários centrais do AMB_V2.
"""

from .config import (
    Colors,
    AmbError,
    ConfigurationError,
    ApiExecutionError,
    log,
    log_error,
    find_repo_root,
    load_env_file,
    load_project_json,
    get_env,
    require_env,
    get_repo_name,
    get_device_type,
    parse_design_tokens_from_text,
    get_design_system_config,
    main,
)
from .bootstrap import (
    ensure_amb_env,
    get_amb_root,
    add_to_sys_path,
    CANONICAL_SUBMODULES,
)
from .rules_manager import (
    RulesManager,
    get_rules_manager,
    load_project_rules,
)

__all__ = [
    "Colors",
    "AmbError",
    "ConfigurationError",
    "ApiExecutionError",
    "log",
    "log_error",
    "find_repo_root",
    "load_env_file",
    "load_project_json",
    "get_env",
    "require_env",
    "get_repo_name",
    "get_device_type",
    "parse_design_tokens_from_text",
    "get_design_system_config",
    "RulesManager",
    "get_rules_manager",
    "load_project_rules",
    "main",
    "ensure_amb_env",
    "get_amb_root",
    "add_to_sys_path",
    "CANONICAL_SUBMODULES",
]
