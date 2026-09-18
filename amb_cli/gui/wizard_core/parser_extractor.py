import argparse
import os
from typing import Dict, Any

try:
    from config import get_repo_name
except ImportError:
    from config.config import get_repo_name


def extract_commands(parser: argparse.ArgumentParser, prefix: str = "") -> Dict[str, Any]:
    """
    Extracts commands and subparsers from an argparse parser.
    """
    commands = {}
    for action in parser._actions:
        if isinstance(action, argparse._SubParsersAction):
            help_map = {choice.dest: choice.help for choice in action._choices_actions}
            for cmd_name, subparser in action.choices.items():
                full_cmd = f"{prefix} {cmd_name}".strip()
                help_text = help_map.get(cmd_name, "")
                commands[full_cmd] = {"parser": subparser, "help": help_text}
                commands.update(extract_commands(subparser, full_cmd))
    return commands


def clean_command_map(command_map: Dict[str, Any]) -> Dict[str, Any]:
    """
    Removes duplicated parsers (aliases) to keep the command list clean.
    """
    seen_parsers = set()
    cleaned_map = {}
    for cmd_name, data in command_map.items():
        sub_p = data["parser"]
        if sub_p not in seen_parsers:
            cleaned_map[cmd_name] = data
            seen_parsers.add(sub_p)
    return cleaned_map


def detect_repo_name(project_root: str, env_path: str) -> str:
    """
    Detects the repository/project name from .env or root.
    """
    if os.path.exists(env_path):
        try:
            with open(env_path, "r", encoding="utf-8", errors="replace") as f:
                for line in f:
                    line_s = line.strip()
                    if line_s.startswith("GITHUB_REPOSITORY=") and not line_s.startswith("#"):
                        val = line_s.split("=", 1)[1].strip()
                        if val:
                            return val
        except Exception:
            pass
    try:
        repo = get_repo_name()
        if repo:
            return repo
    except Exception:
        pass
    return os.path.basename(project_root)
