import pytest
import json
from unittest.mock import patch, MagicMock
from pathlib import Path
from amb_cli.architecture.ai_context_builder import AIContextBuilder, generate_context

@pytest.fixture
def mock_builder():
    builder = AIContextBuilder(Path("/dummy/repo"))
    builder.file_map = {
        "apps/kanban/src/index.ts",
        "apps/kanban/src/util.ts",
        "src/modules/users/controller.ts",
        "src/modules/users/service.ts",
        "src/modules/billing/index.ts"
    }
    return builder

def test_discover_modules(mock_builder):
    modules = mock_builder.discover_modules()
    assert len(modules) == 3
    # Módulos ordenados por nome: billing, kanban, users
    assert modules[0]["name"] == "billing"
    assert modules[0]["files_count"] == 1
    assert modules[1]["name"] == "kanban"
    assert modules[1]["files_count"] == 2
    assert modules[2]["name"] == "users"
    assert modules[2]["files_count"] == 2

@patch("amb_cli.architecture.ai_context_builder.AIContextBuilder")
@patch("amb_cli.architecture.ai_context_builder.find_repo_root", return_value="/dummy")
def test_generate_context_no_target_modules_found(mock_find_repo, mock_builder_class, capsys):
    mock_builder = MagicMock()
    mock_builder.discover_modules.return_value = [
        {"name": "kanban", "files_count": 18},
        {"name": "users", "files_count": 12},
    ]
    mock_builder_class.return_value = mock_builder

    generate_context(target=None, output_json=False)

    captured = capsys.readouterr().out
    assert "=== 🧩 MÓDULOS ENCONTRADOS NO PROJETO ===" in captured
    assert "kanban" in captured
    assert "users" in captured
    assert "amb context kanban" in captured

@patch("amb_cli.architecture.ai_context_builder.AIContextBuilder")
@patch("amb_cli.architecture.ai_context_builder.find_repo_root", return_value="/dummy")
def test_generate_context_no_target_modules_found_json(mock_find_repo, mock_builder_class, capsys):
    mock_builder = MagicMock()
    mock_builder.discover_modules.return_value = [
        {"name": "kanban", "files_count": 18}
    ]
    mock_builder_class.return_value = mock_builder

    generate_context(target=None, output_json=True)

    captured = capsys.readouterr().out
    data = json.loads(captured)
    assert "modules" in data
    assert len(data["modules"]) == 1
    assert data["modules"][0]["name"] == "kanban"

@patch("amb_cli.architecture.ai_context_builder.AIContextBuilder")
@patch("amb_cli.architecture.ai_context_builder.find_repo_root", return_value="/dummy")
def test_generate_context_no_target_no_modules(mock_find_repo, mock_builder_class, capsys):
    mock_builder = MagicMock()
    mock_builder.discover_modules.return_value = []
    mock_builder.trace_module_chain.return_value = {"file1.ts"}
    mock_builder.classify_and_order_files.return_value = {}
    mock_builder.generate_markdown.return_value = "MARKDOWN PROJETO"
    mock_builder_class.return_value = mock_builder

    generate_context(target=None, output_json=False)

    # Verifica se usou 'PROJETO' como query
    mock_builder.trace_module_chain.assert_called_with("PROJETO")
    mock_builder.classify_and_order_files.assert_called_with({"file1.ts"}, "PROJETO")
    captured = capsys.readouterr().out
    assert "MARKDOWN PROJETO" in captured

@patch("amb_cli.architecture.ai_context_builder.AIContextBuilder")
@patch("amb_cli.architecture.ai_context_builder.find_repo_root", return_value="/dummy")
def test_generate_context_with_target(mock_find_repo, mock_builder_class, capsys):
    mock_builder = MagicMock()
    mock_builder.trace_module_chain.return_value = {"file1.ts"}
    mock_builder.classify_and_order_files.return_value = {}
    mock_builder.generate_markdown.return_value = "MARKDOWN AGENDA"
    mock_builder_class.return_value = mock_builder

    generate_context(target="agenda", output_json=False)

    mock_builder.discover_modules.assert_not_called()
    mock_builder.trace_module_chain.assert_called_with("agenda")
    captured = capsys.readouterr().out
    assert "MARKDOWN AGENDA" in captured
