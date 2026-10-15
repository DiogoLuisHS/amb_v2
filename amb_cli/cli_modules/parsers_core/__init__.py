"""Parsers modulares para a CLI do AMB_V2."""
from cli_modules.parsers_core.git_parser import register_git_parser
from cli_modules.parsers_core.jules_parser import register_jules_parser

__all__ = ["register_git_parser", "register_jules_parser"]
