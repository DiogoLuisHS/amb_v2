import pytest
import json
from unittest.mock import MagicMock, patch
from amb_cli.integrations.stitch.stitch_client import StitchClient
from amb_cli.core import Colors

def test_stitch_status_diagnostic_all_configured(monkeypatch):
    monkeypatch.setattr("shutil.which", lambda bin_name: "node" if bin_name == "node" else None)
    mock_proc = MagicMock(returncode=0, stdout="v20.x")
    monkeypatch.setattr("subprocess.run", lambda *args, **kwargs: mock_proc)

    monkeypatch.setenv("STITCH_API_KEY", "mock-key")
    monkeypatch.setenv("STITCH_PROJECT_ID", "mock-project")

    client = StitchClient()
    # Mock list_screens to not hit the real API
    client.list_screens = MagicMock(return_value=[{}, {}])

    status = client.get_status()
    assert status["node_runtime"]["installed"] is True
    assert status["node_runtime"]["version"] == "v20.x"
    assert status["api_key"]["configured"] is True
    assert status["project_id"]["configured"] is True
    assert status["project_id"]["value"] == "mock-project"
    assert status["connectivity"]["connected"] is True
    assert "2 telas ativas" in status["connectivity"]["details"]

def test_stitch_status_diagnostic_missing_dependencies(monkeypatch):
    monkeypatch.setattr("shutil.which", lambda bin_name: None)
    monkeypatch.delenv("STITCH_API_KEY", raising=False)
    monkeypatch.delenv("STITCH_PROJECT_ID", raising=False)

    client = StitchClient()
    status = client.get_status()

    assert status["node_runtime"]["installed"] is False
    assert status["api_key"]["configured"] is False
    assert status["project_id"]["configured"] is False
    assert status["connectivity"]["connected"] is False

def test_stitch_handler_status_json(monkeypatch, capsys):
    from amb_cli.cli_modules.handlers_core.stitch_handler import handle_cmd_stitch
    class Args:
        stitch_cmd = "status"
        json = True

    monkeypatch.setattr("integrations.stitch.stitch_client.StitchClient.get_status", lambda self: {
        "node_runtime": {"installed": True, "version": "v18"},
        "api_key": {"configured": True},
        "runner": {"installed": True},
        "project_id": {"configured": True, "value": "test-id"},
        "connectivity": {"connected": True, "details": "1 tela ativa"}
    })

    handle_cmd_stitch(Args())
    captured = capsys.readouterr()
    output = json.loads(captured.out)
    assert output["node_runtime"]["version"] == "v18"

def test_stitch_handler_status_visual(monkeypatch, capsys):
    from amb_cli.cli_modules.handlers_core.stitch_handler import handle_cmd_stitch
    class Args:
        stitch_cmd = "status"
        json = False

    monkeypatch.setattr("integrations.stitch.stitch_client.StitchClient.get_status", lambda self: {
        "node_runtime": {"installed": True, "version": "v20.x"},
        "api_key": {"configured": True},
        "runner": {"installed": True},
        "project_id": {"configured": True, "value": "meu-projeto"},
        "connectivity": {"connected": True, "details": "2 telas ativas"}
    })

    handle_cmd_stitch(Args())
    captured = capsys.readouterr()
    assert "DIAGNÓSTICO GOOGLE STITCH SDK" in captured.out
    assert "Node.js Runtime:" in captured.out
    assert "Instalado (v20.x)" in captured.out
    assert "API Key:" in captured.out
    assert "Configurada" in captured.out
    assert "Projeto Ativo:" in captured.out
    assert "projects/meu-projeto" in captured.out
    assert "Conectividade:" in captured.out
    assert "Conectada (2 telas ativas)" in captured.out
