import os
import pytest
from pathlib import Path
from workspace.workflow_generator import WorkflowGenerator
from core.exceptions import AmbError

def test_generate_scheduled_workflow_default(tmp_path):
    """Testa geração do workflow com parâmetros padrão."""
    output_path = tmp_path / ".github" / "workflows" / "amb-scheduled-tasks.yml"

    returned_path = WorkflowGenerator.generate_scheduled_workflow(output_path=output_path)

    assert returned_path == output_path
    assert returned_path.exists()

    content = returned_path.read_text(encoding="utf-8")
    assert "name: AMB Scheduled Maintenance" in content
    assert "cron: '0 3 * * *'" in content
    assert "run: python -m amb_cli.cli validate" in content
    assert "role" not in content

def test_generate_scheduled_workflow_custom(tmp_path):
    """Testa geração do workflow com cron e roles customizados."""
    output_path = tmp_path / "custom.yml"

    returned_path = WorkflowGenerator.generate_scheduled_workflow(
        cron_expression="*/5 * * * *",
        roles=["engineer", "qa"],
        output_path=output_path
    )

    assert returned_path == output_path
    assert returned_path.exists()

    content = returned_path.read_text(encoding="utf-8")
    assert "cron: '*/5 * * * *'" in content
    assert "Run AMB Agent (engineer)" in content
    assert "python -m amb_cli.cli agent --role engineer" in content
    assert "Run AMB Agent (qa)" in content
    assert "python -m amb_cli.cli agent --role qa" in content

def test_generate_scheduled_workflow_invalid_cron(tmp_path):
    """Testa se a validação de cron lança AmbError."""
    output_path = tmp_path / "custom.yml"

    with pytest.raises(AmbError) as exc_info:
        WorkflowGenerator.generate_scheduled_workflow(
            cron_expression="0 3 * *", # Apenas 4 campos
            output_path=output_path
        )

    assert "Expressão cron inválida" in str(exc_info.value)

    with pytest.raises(AmbError):
        WorkflowGenerator.generate_scheduled_workflow(
            cron_expression="0 3 * * * *", # 6 campos
            output_path=output_path
        )

def test_workflow_handler_cli(capsys, monkeypatch, tmp_path):
    """Testa o handler via chamada de função simulando a CLI."""
    from cli_modules.handlers_core.workflow_handler import handle_cmd_workflow

    class DummyArgs:
        command = "workflow"
        workflow_cmd = "schedule"
        cron = "0 0 * * *"
        role = ["qa"]
        output = str(tmp_path / "test_handler.yml")

    args = DummyArgs()

    handle_cmd_workflow(args)

    captured = capsys.readouterr()
    assert "Workflow agendado gerado com sucesso" in captured.out

    assert Path(args.output).exists()
    content = Path(args.output).read_text(encoding="utf-8")
    assert "cron: '0 0 * * *'" in content
    assert "role qa" in content
