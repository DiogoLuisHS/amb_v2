import os
import json
import pytest
from unittest.mock import patch, MagicMock
from pathlib import Path
from amb_cli.pipeline.pipeline import PipelineOrchestrator
from amb_cli.agents.loop_core.loop_state_machine import LoopState, LoopStateMachine

@pytest.fixture
def test_state_dir(tmp_path):
    with patch("amb_cli.pipeline.pipeline.find_repo_root", return_value=str(tmp_path)), \
         patch("amb_cli.agents.loop_core.loop_state_machine._get_amb_dir", return_value=tmp_path / ".amb"):
        yield tmp_path

@pytest.fixture
def mock_pipeline_dependencies(test_state_dir):
    with patch("amb_cli.pipeline.pipeline.get_repo_name", return_value="mock-repo"), \
         patch("amb_cli.pipeline.pipeline.GitService"), \
         patch("amb_cli.pipeline.pipeline.process_design_stage") as mock_process_design, \
         patch("amb_cli.pipeline.pipeline.AntigravityClient"), \
         patch("amb_cli.pipeline.pipeline.PipelineOrchestrator._synthesize_stitch_ui", return_value="mock_summary"), \
         patch("amb_cli.pipeline.pipeline.PipelineOrchestrator._extract_clean_rules", return_value="mock_rules"), \
         patch("amb_cli.pipeline.pipeline.build_executive_prompt", return_value="mock_prompt"), \
         patch("amb_cli.pipeline.pipeline.JulesClient") as mock_jules_client_cls, \
         patch("amb_cli.pipeline.pipeline.QualityGatekeeper") as mock_qa, \
         patch("agents.autonomous_loop.monitor_and_assist_session", return_value="COMPLETED") as mock_monitor, \
         patch("integrations.jules.tools.merge_session_pr.run_merge_session_pr") as mock_merge:

        # Configurar mock process_design_stage
        mock_process_design.return_value = {
            "current_screen_id": "screen_1",
            "stitch_html": "<html></html>",
            "screenshot_url": "http://mock.com/img.png",
            "screen_title": "Mock Screen"
        }

        # Configurar mock JulesClient
        mock_jules_client = MagicMock()
        mock_jules_client.create_session.return_value = {"name": "mock_session_123"}
        mock_jules_client_cls.return_value = mock_jules_client

        # Configurar mock QualityGatekeeper
        mock_qa.run_qa.return_value = True

        yield

def test_pipeline_state_machine_transitions(mock_pipeline_dependencies, test_state_dir):
    """Testa se as transições de estado ocorrem corretamente durante o pipeline."""
    # Executa o pipeline com mock
    from unittest.mock import mock_open
    mock_file = mock_open(read_data="mock_prompt_content")

    # Invés de mockar open() que causa stack overflow, podemos apenas criar o arquivo no dir temporário.
    import os
    amb_dir = test_state_dir / ".amb"
    amb_dir.mkdir(parents=True, exist_ok=True)

    test_prompt = test_state_dir / "test_prompt.md"
    with open(test_prompt, "w", encoding="utf-8") as f:
        f.write("mock_prompt_content")

    PipelineOrchestrator.run(prompt_file=str(test_prompt), auto_merge=True)

    # Verifica o estado no arquivo json persistido
    state_file = amb_dir / "loop_state.json"
    assert state_file.exists()

    with open(state_file, "r") as f:
        state_data = json.load(f)

    # Como o pipeline conclui até o fim (auto_merge=True), o estado final deve ser CYCLE_COMPLETED
    assert state_data["state"] == LoopState.CYCLE_COMPLETED.value
    # O session_id deve ter sido gravado
    assert state_data["session_id"] == "mock_session_123"


def test_pipeline_state_machine_resume_flag(mock_pipeline_dependencies, test_state_dir):
    """Testa se a flag --resume recupera corretamente o ID do estado."""
    # Preparar um estado prévio simulando o pipeline pausado ou interrompido
    amb_dir = test_state_dir / ".amb"
    amb_dir.mkdir(parents=True, exist_ok=True)
    state_file = amb_dir / "loop_state.json"

    initial_state = {
        "state": LoopState.SESSION_ACTIVE.value,
        "session_id": "resumed_session_456"
    }
    with open(state_file, "w") as f:
        json.dump(initial_state, f)

    # Executar pipeline apenas com resume=True
    with patch("amb_cli.pipeline.pipeline.PipelineOrchestrator._monitor_jules_session") as mock_monitor_method:
        PipelineOrchestrator.run(resume=True)

        # _monitor_jules_session deve ter sido chamado com o ID recuperado
        mock_monitor_method.assert_called_once()
        args, kwargs = mock_monitor_method.call_args
        assert args[0] == "resumed_session_456"
