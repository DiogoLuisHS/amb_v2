"""
Fachada de retrocompatibilidade para RulesManager.
O gerenciamento de regras arquiteturais foi realocado para o Workspace do Consumidor (F1-M6 - SRP).
"""

from amb_cli.workspace.rules_manager import (
    RulesManager,
    get_rules_manager,
    load_project_rules,
)

__all__ = [
    "RulesManager",
    "get_rules_manager",
    "load_project_rules",
]
