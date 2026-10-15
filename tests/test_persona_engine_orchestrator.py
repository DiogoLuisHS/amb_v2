import pytest
import os
from unittest.mock import patch, MagicMock

from amb_cli.agents.persona_engine import PersonaEngine
from amb_cli.agents.autonomous_loop import run_autonomous_loop
from amb_cli.agents.local_agent_runner import execute_single_persona

@patch("amb_cli.agents.persona_engine.find_repo_root", return_value="/fake/repo")
def test_persona_engine_methods(mock_repo_root):
    engine = PersonaEngine()

    # ensure it uses custom dir
    custom_dir = engine.get_personas_directory(custom_dir="/tmp/fake/custom")
    assert custom_dir == "/tmp/fake/custom"

@patch("amb_cli.agents.autonomous_loop.get_repo_name", return_value="fake_repo")
@patch("amb_cli.agents.autonomous_loop.find_repo_root", return_value="/fake/repo")
@patch("amb_cli.agents.autonomous_loop.GitService")
@patch("amb_cli.agents.autonomous_loop.JulesClient")
@patch("amb_cli.agents.autonomous_loop.IssueSynchronizer")
@patch("amb_cli.agents.autonomous_loop.PersonaEngine")
@patch("amb_cli.agents.autonomous_loop.dispatch_jules_session")
@patch("amb_cli.agents.autonomous_loop.monitor_and_assist_session", return_value="COMPLETED")
def test_autonomous_loop_uses_engine(mock_monitor, mock_dispatch, mock_engine_cls, mock_syncer_cls, mock_jules_cls, mock_git_cls, mock_root, mock_repo_name):
    # Setup mocks
    mock_engine = mock_engine_cls.return_value
    mock_engine.discover_personas.return_value = {"engineer": {"title": "Test Title"}}
    mock_engine.load_persona.return_value = "raw persona {repo_name}"
    mock_engine.render_persona_template.return_value = "rendered persona fake_repo"

    mock_syncer = mock_syncer_cls.return_value
    mock_syncer.resolve_items_queue.return_value = [{"type": "persona", "name": "engineer"}]

    run_autonomous_loop(role="engineer", max_cycles=1, delay_between_cycles=0)

    # Assertions
    mock_engine.discover_personas.assert_called_once()
    mock_engine.load_persona.assert_called_with("engineer")
    mock_engine.render_persona_template.assert_called_with("raw persona {repo_name}")
    mock_dispatch.assert_called_once()

    # The rendered prompt should have been passed to Jules session via context builder, we assume build_ai_context returns the wrapped version.
    prompt_used = mock_dispatch.call_args[0][1]
    assert "rendered persona fake_repo" in prompt_used

@patch("amb_cli.agents.local_agent_runner.find_repo_root", return_value="/fake/repo")
@patch("amb_cli.agents.local_agent_runner.run_local_agent")
@patch("amb_cli.agents.local_agent_runner.PersonaEngine")
def test_local_agent_runner_uses_engine(mock_engine_cls, mock_run_local, mock_root):
    mock_engine = mock_engine_cls.return_value
    mock_engine.render_persona_template.return_value = "rendered local persona"

    persona_data = {
        "title": "Local Persona",
        "content": "raw content {stack}",
        "filename": "local.md",
        "path": "/fake/path/local.md"
    }

    execute_single_persona(persona_data, dispatch_jules=False)

    mock_engine.render_persona_template.assert_called_with("raw content {stack}")
    mock_run_local.assert_called_once()
    assert "rendered local persona" in mock_run_local.call_args[0][0]
