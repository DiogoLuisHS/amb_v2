import json
import os
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock
from amb_cli.architecture.ai_context_builder import generate_context, _save_to_file

@pytest.fixture
def mock_builder():
    with patch("amb_cli.architecture.ai_context_builder.AIContextBuilder") as mock:
        instance = mock.return_value
        instance.discover_modules.return_value = [{"name": "kanban", "files_count": 5}]
        instance.trace_module_chain.return_value = {"src/kanban/index.ts"}
        instance.classify_and_order_files.return_value = {
            "core": {"title": "Core", "icon": "⭐", "files": [{"path": "src/kanban/index.ts", "is_core": True, "in_count": 0, "out_count": 0}]}
        }
        instance.generate_markdown.return_value = "# ROTEIRO KANBAN\n- src/kanban/index.ts"
        yield instance

@pytest.fixture
def mock_find_repo_root():
    with patch("amb_cli.architecture.ai_context_builder.find_repo_root", return_value="/mock/root"):
        yield

def test_context_markdown_to_file(mock_builder, mock_find_repo_root, tmp_path, capsys):
    output_file = tmp_path / "docs" / "contexto_kanban.md"
    generate_context(target="kanban", output_json=False, output_file=str(output_file))

    # Assert file is created and contains correct content
    assert output_file.exists()
    content = output_file.read_text(encoding="utf-8")
    assert content == "# ROTEIRO KANBAN\n- src/kanban/index.ts"

    # Assert correct success message is printed
    captured = capsys.readouterr()
    assert f"✔ Roteiro arquitetural salvo com sucesso em: {output_file}" in captured.out

def test_context_json_to_file(mock_builder, mock_find_repo_root, tmp_path, capsys):
    output_file = tmp_path / "docs" / "contexto_kanban.json"
    generate_context(target="kanban", output_json=True, output_file=str(output_file))

    # Assert file is created and contains correct valid JSON
    assert output_file.exists()
    content = output_file.read_text(encoding="utf-8")
    data = json.loads(content)
    assert data["query"] == "kanban"
    assert "layers" in data

    # Assert correct success message is printed
    captured = capsys.readouterr()
    assert f"✔ Roteiro arquitetural salvo com sucesso em: {output_file}" in captured.out

def test_context_no_target_markdown_to_file(mock_builder, mock_find_repo_root, tmp_path, capsys):
    output_file = tmp_path / "docs" / "modules.txt"
    generate_context(target=None, output_json=False, output_file=str(output_file))

    assert output_file.exists()
    content = output_file.read_text(encoding="utf-8")
    assert "=== 🧩 MÓDULOS ENCONTRADOS NO PROJETO ===" in content
    assert "kanban" in content

    captured = capsys.readouterr()
    assert f"✔ Roteiro arquitetural salvo com sucesso em: {output_file}" in captured.out

def test_context_no_target_json_to_file(mock_builder, mock_find_repo_root, tmp_path, capsys):
    output_file = tmp_path / "docs" / "modules.json"
    generate_context(target=None, output_json=True, output_file=str(output_file))

    assert output_file.exists()
    content = output_file.read_text(encoding="utf-8")
    data = json.loads(content)
    assert "modules" in data
    assert data["modules"][0]["name"] == "kanban"

    captured = capsys.readouterr()
    assert f"✔ Roteiro arquitetural salvo com sucesso em: {output_file}" in captured.out

def test_context_terminal_output_preserved(mock_builder, mock_find_repo_root, capsys):
    generate_context(target="kanban", output_json=False)
    captured = capsys.readouterr()
    assert "# ROTEIRO KANBAN\n- src/kanban/index.ts" in captured.out
    assert "✔ Roteiro arquitetural salvo com sucesso em:" not in captured.out

def test_context_save_to_file_creates_directories(tmp_path):
    filepath = str(tmp_path / "nested" / "dir" / "file.txt")
    _save_to_file(filepath, "content")
    assert os.path.exists(filepath)
    with open(filepath, "r", encoding="utf-8") as f:
        assert f.read() == "content"
