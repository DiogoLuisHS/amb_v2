import pytest
from unittest.mock import patch, MagicMock
from pathlib import Path
from amb_cli.agents.autonomous_loop import run_autonomous_loop

@pytest.fixture
def mock_dependencies():
    with patch("amb_cli.agents.autonomous_loop.get_repo_name", return_value="test_repo"), \
         patch("amb_cli.agents.autonomous_loop.find_repo_root", return_value=Path("/test_root")), \
         patch("amb_cli.agents.autonomous_loop.GitService") as mock_git_service, \
         patch("amb_cli.agents.autonomous_loop.JulesClient"), \
         patch("amb_cli.agents.autonomous_loop.PersonaEngine") as mock_persona_engine, \
         patch("amb_cli.agents.autonomous_loop.IssueSynchronizer") as mock_issue_sync, \
         patch("amb_cli.agents.autonomous_loop.PipelineOrchestrator") as mock_pipeline:

        mock_git_service.return_value.get_current_branch.return_value = "main"

        # Configure IssueSynchronizer
        mock_syncer = MagicMock()
        mock_issue_sync.return_value = mock_syncer

        # Configure PersonaEngine
        mock_engine = MagicMock()
        mock_engine.discover_personas.return_value = {}
        mock_persona_engine.return_value = mock_engine

        yield {
            "syncer": mock_syncer,
            "pipeline": mock_pipeline,
        }

def test_batch_execution_with_pipeline_flag(mock_dependencies):
    """Testa execução do lote amb agent -p <pasta> --pipeline acionando o pipeline de design."""

    mock_syncer = mock_dependencies["syncer"]
    mock_pipeline = mock_dependencies["pipeline"]

    mock_path = MagicMock()
    mock_path.exists.return_value = True
    mock_path.__str__.return_value = "prompt.md"
    mock_path.stem = "prompt"

    mock_syncer.resolve_items_queue.return_value = [
        {"type": "prompt", "name": "prompt", "path": mock_path, "content": "Just text.", "_full_prompt": "Just text."}
    ]

    run_autonomous_loop(
        prompt_file="test_dir",
        use_pipeline=True,
        max_cycles=1,
    )

    mock_pipeline.run.assert_called_once()
    assert mock_pipeline.run.call_args[1]["prompt_file"] == "prompt.md"

def test_auto_detection_stitch_section(mock_dependencies):
    """Testa auto-detecção de prompts contendo seções ## Stitch roteando para o pipeline mesmo sem a flag."""

    mock_syncer = mock_dependencies["syncer"]
    mock_pipeline = mock_dependencies["pipeline"]

    mock_path = MagicMock()
    mock_path.exists.return_value = True
    mock_path.__str__.return_value = "prompt.md"
    mock_path.stem = "prompt"

    mock_syncer.resolve_items_queue.return_value = [
        {"type": "prompt", "name": "prompt", "path": mock_path, "content": "## Stitch\nSome UI instructions.", "_full_prompt": "## Stitch\nSome UI instructions."}
    ]

    run_autonomous_loop(
        prompt_file="test_dir",
        use_pipeline=False,
        max_cycles=1,
    )

    mock_pipeline.run.assert_called_once()

def test_sequential_processing_multiple_prompts(mock_dependencies):
    """Testa processamento sequencial de múltiplos prompts visuais em lote."""

    mock_syncer = mock_dependencies["syncer"]
    mock_pipeline = mock_dependencies["pipeline"]

    mock_path1 = MagicMock()
    mock_path1.exists.return_value = True
    mock_path1.__str__.return_value = "prompt1.md"
    mock_path1.stem = "prompt1"

    mock_path2 = MagicMock()
    mock_path2.exists.return_value = True
    mock_path2.__str__.return_value = "prompt2.md"
    mock_path2.stem = "prompt2"

    mock_syncer.resolve_items_queue.return_value = [
        {"type": "prompt", "name": "prompt1", "path": mock_path1, "content": "## Stitch\nUI1.", "_full_prompt": "## Stitch\nUI1."},
        {"type": "prompt", "name": "prompt2", "path": mock_path2, "content": "## Stitch\nUI2.", "_full_prompt": "## Stitch\nUI2."}
    ]

    run_autonomous_loop(
        prompt_file="test_dir",
        use_pipeline=False,
        max_cycles=1,
    )

    assert mock_pipeline.run.call_count == 2
    assert mock_pipeline.run.call_args_list[0][1]["prompt_file"] == "prompt1.md"
    assert mock_pipeline.run.call_args_list[1][1]["prompt_file"] == "prompt2.md"
