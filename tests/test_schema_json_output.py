import json
import pytest
from unittest.mock import patch
from pathlib import Path
from amb_cli.architecture.db_schema_reader import show_schema


@pytest.fixture
def mock_schema_tables():
    return [
        {
            "variable": "users",
            "table_name": "users",
            "file": "schema.ts",
            "path": "/mock/repo/root/schema.ts",
            "columns": [
                {"name": "id", "type": "serial", "options": "'id').primaryKey()"}
            ]
        },
        {
            "variable": "kanban_boards",
            "table_name": "kanban_boards",
            "file": "kanban.ts",
            "path": "/mock/repo/root/kanban.ts",
            "columns": [
                {"name": "id", "type": "serial", "options": "'id').primaryKey()"}
            ]
        }
    ]


@patch("amb_cli.architecture.db_schema_reader.find_repo_root")
@patch("amb_cli.architecture.db_schema_reader.DbSchemaReader.list_schema_files")
@patch("amb_cli.architecture.db_schema_reader.DbSchemaReader.parse_drizzle_schema")
def test_schema_json_output_all(mock_parse, mock_list, mock_find, mock_schema_tables, capsys):
    mock_find.return_value = "/mock/repo/root"
    mock_list.return_value = [Path("/mock/repo/root/schema.ts"), Path("/mock/repo/root/kanban.ts")]

    # parse_drizzle_schema mock side_effect to return specific tables for files
    def parse_side_effect(filepath):
        if "schema.ts" in str(filepath):
            return [mock_schema_tables[0]]
        if "kanban.ts" in str(filepath):
            return [mock_schema_tables[1]]
        return []

    mock_parse.side_effect = parse_side_effect

    show_schema(as_json=True)
    captured = capsys.readouterr()

    # Verify it is valid JSON
    output_data = json.loads(captured.out)

    assert output_data["root"] == "/mock/repo/root"
    assert output_data["total_tables"] == 2
    assert len(output_data["tables"]) == 2

    table_names = [t["table_name"] for t in output_data["tables"]]
    assert "users" in table_names
    assert "kanban_boards" in table_names

    # Assert there is no terminal formatting/ANSI banners
    assert "CATÁLOGO DE SCHEMAS" not in captured.out


@patch("amb_cli.architecture.db_schema_reader.find_repo_root")
@patch("amb_cli.architecture.db_schema_reader.DbSchemaReader.list_schema_files")
@patch("amb_cli.architecture.db_schema_reader.DbSchemaReader.parse_drizzle_schema")
def test_schema_json_output_filtered(mock_parse, mock_list, mock_find, mock_schema_tables, capsys):
    mock_find.return_value = "/mock/repo/root"
    mock_list.return_value = [Path("/mock/repo/root/schema.ts"), Path("/mock/repo/root/kanban.ts")]

    def parse_side_effect(filepath):
        if "schema.ts" in str(filepath):
            return [mock_schema_tables[0]]
        if "kanban.ts" in str(filepath):
            return [mock_schema_tables[1]]
        return []

    mock_parse.side_effect = parse_side_effect

    show_schema(filter_term="kanban", as_json=True)
    captured = capsys.readouterr()

    # Verify it is valid JSON
    output_data = json.loads(captured.out)

    assert output_data["root"] == "/mock/repo/root"
    assert output_data["total_tables"] == 1
    assert len(output_data["tables"]) == 1

    assert output_data["tables"][0]["table_name"] == "kanban_boards"
    assert "CATÁLOGO DE SCHEMAS" not in captured.out


@patch("amb_cli.architecture.db_schema_reader.find_repo_root")
@patch("amb_cli.architecture.db_schema_reader.DbSchemaReader.list_schema_files")
@patch("amb_cli.architecture.db_schema_reader.DbSchemaReader.parse_drizzle_schema")
def test_schema_json_output_no_json_flag(mock_parse, mock_list, mock_find, mock_schema_tables, capsys):
    mock_find.return_value = "/mock/repo/root"
    mock_list.return_value = [Path("/mock/repo/root/schema.ts"), Path("/mock/repo/root/kanban.ts")]

    def parse_side_effect(filepath):
        if "schema.ts" in str(filepath):
            return [mock_schema_tables[0]]
        if "kanban.ts" in str(filepath):
            return [mock_schema_tables[1]]
        return []

    mock_parse.side_effect = parse_side_effect

    show_schema(filter_term="kanban", as_json=False)
    captured = capsys.readouterr()

    # Ensure it's not printing JSON
    try:
        json.loads(captured.out)
        is_json = True
    except json.JSONDecodeError:
        is_json = False

    assert not is_json

    # Ensure terminal formatting remains
    assert "CATÁLOGO DE SCHEMAS DO BANCO DE DADOS" in captured.out
    assert "TABELA: " in captured.out
    assert "kanban_boards" in captured.out
    assert "Total de tabelas listadas: " in captured.out
