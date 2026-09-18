"""Testes unitários completos para parsers e despacho de comandos da CLI do AMB_V2."""
import argparse
from unittest.mock import patch, MagicMock
import pytest

from amb_cli.cli_modules.cli_parsers import create_parser
from amb_cli.cli_modules.cli_handlers import (
    cmd_setup, cmd_prompt, cmd_check, cmd_monitor, cmd_advisor,
    cmd_config, cmd_agent, cmd_validate
)


@pytest.fixture
def parser():
    return create_parser()


def test_parser_setup_command(parser):
    args = parser.parse_args(["setup", "--auto", "--dry-run", "--path", "/tmp/test"])
    assert args.command == "setup"
    assert args.auto is True
    assert args.dry_run is True
    assert args.path == "/tmp/test"


def test_parser_prompt_command(parser):
    args = parser.parse_args(["prompt", "-s", "Criar login", "-r", "frontend", "-o", "prompt.md"])
    assert args.command == "prompt"
    assert args.synthesize == "Criar login"
    assert args.role == "frontend"
    assert args.output == "prompt.md"


def test_parser_check_and_config(parser):
    args = parser.parse_args(["check", "--json"])
    assert args.command == "check"
    assert args.json is True

    args_cfg = parser.parse_args(["config", "--gemini-confirm", "on"])
    assert args_cfg.command == "config"
    assert args_cfg.gemini_confirm == "on"


def test_parser_monitor_and_advisor(parser):
    args_mon = parser.parse_args(["monitor", "-y", "-1", "--interval", "20"])
    assert args_mon.command == "monitor"
    assert args_mon.auto_approve is True
    assert args_mon.check_once is True
    assert args_mon.interval == 20

    args_adv = parser.parse_args(["advisor", "-s", "12345", "-m", "mensagem", "-y"])
    assert args_adv.command == "advisor"
    assert args_adv.session_id_flag == "12345"
    assert args_adv.message == "mensagem"
    assert args_adv.auto_approve is True


def test_parser_agent_command(parser):
    args = parser.parse_args([
        "agent", "--role", "engineer", "--loop",
        "--max-cycles", "3", "--branch", "develop",
        "--modules", "api,web", "--no-auto-merge"
    ])
    assert args.command == "agent"
    assert args.role == "engineer"
    assert args.loop is True
    assert args.max_cycles == 3
    assert args.branch == "develop"
    assert args.modules == "api,web"
    assert args.no_auto_merge is True


def test_parser_jules_subcommands(parser):
    subcmds = [
        (["jules", "status", "--json"], "status"),
        (["jules", "sources", "--json"], "sources"),
        (["jules", "list", "--limit", "5", "--all"], "list"),
        (["jules", "get", "12345", "--watch"], "get"),
        (["jules", "create", "-p", "fazer algo", "-t", "titulo"], "create"),
        (["jules", "reply", "-s", "12345", "-m", "resposta"], "reply"),
        (["jules", "approve", "12345"], "approve"),
        (["jules", "merge", "12345", "--auto-latest"], "merge"),
        (["jules", "clean", "--failed", "--force"], "clean"),
    ]
    for argv, expected_sub in subcmds:
        args = parser.parse_args(argv)
        assert args.command == "jules"
        assert args.jules_cmd == expected_sub


def test_parser_stitch_subcommands(parser):
    subcmds = [
        (["stitch", "list"], "list"),
        (["stitch", "generate", "-p", "dashboard", "-o", "out.html"], "generate"),
        (["stitch", "refine", "-s", "sc1", "-p", "dark theme"], "refine"),
        (["stitch", "get", "-s", "sc1"], "get"),
        (["stitch", "variants", "-s", "sc1", "-p", "blue", "-c", "4"], "variants"),
        (["stitch", "download", "-o", "./assets"], "download"),
        (["stitch", "project"], "project"),
        (["stitch", "sync", "-f", "design.md"], "sync"),
        (["stitch", "call", "list_screens"], "call"),
    ]
    for argv, expected_sub in subcmds:
        args = parser.parse_args(argv)
        assert args.command == "stitch"
        assert args.stitch_cmd == expected_sub


def test_parser_antigravity_subcommands(parser):
    subcmds = [
        (["agy", "status", "--json"], "status"),
        (["agy", "prompt", "-i", "ideia", "-r", "qa", "-o", "prompt.md"], "prompt"),
        (["agy", "validate", "app.py", "--json"], "validate"),
        (["agy", "rules", "--json", "--content"], "rules"),
        (["agy", "run", "Olá IA", "--model", "gemini-3.8-flash"], "run"),
    ]
    for argv, expected_sub in subcmds:
        args = parser.parse_args(argv)
        assert args.command in ["antigravity", "agy"]
        assert args.agy_cmd == expected_sub


def test_parser_validate_and_pipeline(parser):
    args_val = parser.parse_args(["validate", "test.py", "--json"])
    assert args_val.command == "validate"
    assert args_val.file == "test.py"
    assert args_val.json is True

    args_pipe = parser.parse_args([
        "pipeline", "-s", "stitch.md", "-j", "jules.md",
        "-y", "--skip-stitch", "--resume-session", "999"
    ])
    assert args_pipe.command == "pipeline"
    assert args_pipe.stitch_prompt == "stitch.md"
    assert args_pipe.jules_prompt == "jules.md"
    assert args_pipe.auto_approve is True
    assert args_pipe.skip_stitch is True
    assert args_pipe.resume_session == "999"


def test_parser_git_subcommands(parser):
    subcmds = [
        (["git", "status", "--json"], "status", None),
        (["git", "sync", "-r", "origin", "-b", "main"], "sync", None),
        (["git", "diff", "--cached"], "diff", None),
        (["git", "pr", "list", "--no-drafts"], "pr", "list"),
        (["git", "pr", "get", "42"], "pr", "get"),
        (["git", "pr", "create", "-t", "feat: login", "-b", "detalhes"], "pr", "create"),
        (["git", "pr", "ready", "42"], "pr", "ready"),
        (["git", "pr", "approve", "42"], "pr", "approve"),
        (["git", "pr", "merge", "42"], "pr", "merge"),
        (["git", "pr", "close", "42", "--comment", "fechado"], "pr", "close"),
    ]
    for argv, expected_git, expected_pr in subcmds:
        args = parser.parse_args(argv)
        assert args.command == "git"
        assert args.git_cmd == expected_git
        if expected_pr:
            assert args.pr_cmd == expected_pr


# -------------------------------------------------------------
# Testes de Despacho (Handlers)
# -------------------------------------------------------------

def test_cmd_advisor_delegation():
    with patch("cli_modules.handlers_core.jules_handler.handle_cmd_jules") as mock_jules:
        args = argparse.Namespace(session_id="12345", auto_approve=True)
        cmd_advisor(args)
        assert args.jules_cmd == "reply"
        mock_jules.assert_called_once_with(args)


def test_cmd_validate_delegation():
    with patch("cli_modules.handlers_core.antigravity_handler.handle_cmd_antigravity") as mock_agy:
        args = argparse.Namespace(file="test.py", json=True)
        cmd_validate(args)
        assert args.agy_cmd == "validate"
        mock_agy.assert_called_once_with(args)


def test_cmd_prompt_synthesize_delegation():
    with patch("cli_modules.handlers_core.antigravity_handler.handle_cmd_antigravity") as mock_agy:
        args = argparse.Namespace(synthesize="ideia teste", role="dev")
        cmd_prompt(args)
        assert args.agy_cmd == "prompt"
        assert args.idea == "ideia teste"
        mock_agy.assert_called_once_with(args)


def test_cmd_agent_loop_parameters():
    with patch("agents.autonomous_loop.run_autonomous_loop") as mock_loop:
        args = argparse.Namespace(
            loop=True,
            role="engineer",
            prompt=None,
            task=None,
            max_cycles=2,
            branch="main",
            modules="api,gui",
            no_auto_merge=True
        )
        cmd_agent(args)
        mock_loop.assert_called_once_with(
            role="engineer",
            all_personas=False,
            prompt_file=None,
            modules=["api", "gui"],
            max_cycles=2,
            branch="main",
            no_auto_merge=True
        )
