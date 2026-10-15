import pytest
from unittest.mock import patch, MagicMock
import os
import argparse
from amb_cli.cli_modules.cli_handlers import cmd_agent, cmd_pipeline
import sys

@patch("amb_cli.cli_modules.cli_handlers.sys.exit")
def test_cmd_agent_positional_role_simple(mock_exit, monkeypatch):
    args = argparse.Namespace(
        target="engineer",
        role=None,
        prompt=None,
        loop=False,
        sync_issues=False,
        all=False,
        list=False,
        agy=False,
        task=None,
        personas_dir=None,
        modules=None,
        max_cycles=None,
        branch=None,
        no_auto_merge=False,
        concurrency=1
    )

    # Mock os.path.exists specifically inside cli_handlers
    def mock_exists(path):
        return False
    monkeypatch.setattr("amb_cli.cli_modules.cli_handlers.os.path.exists", mock_exists)

    # Just mock the agents.local_agent_runner module in sys.modules
    mock_runner = MagicMock()
    mock_runner.get_personas_directory.return_value = "/fake/dir"
    mock_runner.discover_personas.return_value = {"engineer": {"title": "Engineer"}}

    mock_agents = MagicMock()
    mock_agents.local_agent_runner = mock_runner
    monkeypatch.setitem(sys.modules, 'agents', mock_agents)
    monkeypatch.setitem(sys.modules, 'agents.local_agent_runner', mock_runner)

    cmd_agent(args)
    assert args.role == "engineer"
    mock_runner.execute_single_persona.assert_called_once_with({"title": "Engineer"}, task=None, dispatch_jules=True)

def test_cmd_agent_positional_prompt(monkeypatch):
    args = argparse.Namespace(
        target=".amb/prompts/",
        role=None,
        prompt=None,
        loop=False,
        sync_issues=False,
        all=False,
        list=False,
        agy=False,
        task=None,
        personas_dir=None,
        modules=None,
        max_cycles=None,
        branch=None,
        no_auto_merge=False,
        concurrency=1
    )

    def mock_exists(path):
        return True
    monkeypatch.setattr("amb_cli.cli_modules.cli_handlers.os.path.exists", mock_exists)

    mock_loop = MagicMock()
    mock_agents_loop = MagicMock()
    mock_agents_loop.run_autonomous_loop = mock_loop
    monkeypatch.setitem(sys.modules, 'agents.autonomous_loop', mock_agents_loop)

    cmd_agent(args)
    assert args.prompt == ".amb/prompts/"
    mock_loop.assert_called_once()
    assert mock_loop.call_args[1]["prompt_file"] == ".amb/prompts/"

@patch("pipeline.pipeline.PipelineOrchestrator.run")
def test_cmd_pipeline_positional_spec_file(mock_run, monkeypatch):
    args = argparse.Namespace(
        spec="specs/login.md",
        stitch_prompt=None,
        jules_prompt=None,
        prompt_file=None,
        auto_approve=False,
        skip_stitch=False,
        no_qa=False,
        resume_session=None,
        device=None,
        device_type=None,
        edit_screen_id=None,
        screen_id=None,
        sync_ds=False,
        branch=None,
        auto_merge=False
    )

    def mock_exists(path):
        return True
    monkeypatch.setattr("amb_cli.cli_modules.cli_handlers.os.path.exists", mock_exists)

    cmd_pipeline(args)
    assert args.prompt_file == "specs/login.md"
    mock_run.assert_called_once()

@patch("pipeline.pipeline.PipelineOrchestrator.run")
def test_cmd_pipeline_positional_spec_text(mock_run, monkeypatch):
    args = argparse.Namespace(
        spec="Dashboard de Vendas",
        stitch_prompt=None,
        jules_prompt=None,
        prompt_file=None,
        auto_approve=False,
        skip_stitch=False,
        no_qa=False,
        resume_session=None,
        device=None,
        device_type=None,
        edit_screen_id=None,
        screen_id=None,
        sync_ds=False,
        branch=None,
        auto_merge=False
    )

    def mock_exists(path):
        return False
    monkeypatch.setattr("amb_cli.cli_modules.cli_handlers.os.path.exists", mock_exists)

    cmd_pipeline(args)
    assert args.stitch_prompt == "Dashboard de Vendas"
    assert args.jules_prompt == "Dashboard de Vendas"
    mock_run.assert_called_once()
