import os
import pytest
from unittest.mock import patch, MagicMock
from pathlib import Path

from amb_cli.agents.autonomous_loop import run_autonomous_loop
from amb_cli.pipeline.pipeline import PipelineOrchestrator

def test_autonomous_loop_dry_run(tmp_path, capsys):
    # Setup temporary prompt file
    prompts_dir = tmp_path / ".amb" / "prompts"
    prompts_dir.mkdir(parents=True)
    prompt_file = prompts_dir / "test_prompt.md"
    prompt_file.write_text("Test prompt content")

    with patch("amb_cli.agents.autonomous_loop.JulesClient") as mock_jules_client, \
         patch("amb_cli.agents.autonomous_loop.find_repo_root", return_value=str(tmp_path)), \
         patch("amb_cli.agents.autonomous_loop.get_repo_name", return_value="test_repo"), \
         patch("amb_cli.agents.autonomous_loop.GitService") as mock_git:

        mock_git.return_value.get_current_branch.return_value = "main"

        run_autonomous_loop(
            prompt_file=str(prompts_dir),
            dry_run=True,
            branch="main"
        )

        # Verify output contains the DRY-RUN message
        captured = capsys.readouterr()
        assert "SIMULAÇÃO DE ORQUESTRAÇÃO EM LOTE [DRY-RUN]" in captured.out
        assert "[Prompt] test_prompt.md" in captured.out

        # Verify no external network requests were made
        # It instantiates `client = JulesClient()` before checking `dry_run`, which is fine.
        # But it should never call `create_session` or dispatch any API method.
        mock_jules_client.return_value.create_session.assert_not_called()

        # Another module to mock is `dispatch_jules_session` to be absolutely sure it's not called
        with patch("amb_cli.agents.autonomous_loop.dispatch_jules_session") as mock_dispatch:
            run_autonomous_loop(
                prompt_file=str(prompts_dir),
                dry_run=True,
                branch="main"
            )
            mock_dispatch.assert_not_called()

def test_pipeline_dry_run(tmp_path, capsys):
    # Setup temporary prompt file
    prompt_file = tmp_path / "test_spec.md"
    prompt_file.write_text("# Test\n## Jules\nJules spec\n## Stitch\nStitch spec")

    with patch("amb_cli.pipeline.pipeline.JulesClient") as mock_jules_client, \
         patch("amb_cli.pipeline.pipeline.AntigravityClient") as mock_agy_client, \
         patch("amb_cli.pipeline.pipeline.process_design_stage") as mock_process_design, \
         patch("amb_cli.pipeline.pipeline.find_repo_root", return_value=str(tmp_path)), \
         patch("amb_cli.pipeline.pipeline.get_repo_name", return_value="test_repo"):

        PipelineOrchestrator.run(
            prompt_file=str(prompt_file),
            dry_run=True,
            starting_branch="main"
        )

        # Verify output contains the DRY-RUN message
        captured = capsys.readouterr()
        assert "SIMULAÇÃO DE ORQUESTRAÇÃO DE PIPELINE [DRY-RUN]" in captured.out

        # Verify no external network requests were made
        mock_jules_client.assert_not_called()
        mock_agy_client.assert_not_called()
        mock_process_design.assert_not_called()
