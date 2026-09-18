"""
Fachada de retrocompatibilidade para design tokens.
O gerenciamento de design tokens foi realocado para o Workspace do Consumidor (F1-M6 - SRP).
"""

from amb_cli.workspace.design_tokens import (
    parse_design_tokens_from_text,
    get_design_system_config,
)

__all__ = [
    "parse_design_tokens_from_text",
    "get_design_system_config",
]
