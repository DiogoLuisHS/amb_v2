import os
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

from amb_cli.architecture.db_schema_reader import DbSchemaReader, show_schema


@pytest.fixture
def mock_drizzle_schema_content():
    return """
// User schema
export const users = pgTable('users', {
    id: serial('id').primaryKey(),
    name: text('name').notNull(),
    email: text('email').notNull().unique(),
});

export const posts = pgTable('posts', {
    id: serial('id').primaryKey(),
    title: text('title').notNull(),
    content: text('content'),
    authorId: integer('author_id').references(() => users.id),
});
"""


@pytest.fixture
def repo_root(tmp_path):
    # Setup standard mocked directory structure
    (tmp_path / "apps" / "api" / "src" / "db" / "schema").mkdir(parents=True)
    (tmp_path / "src" / "db" / "schema").mkdir(parents=True)
    return tmp_path


def test_find_schema_dirs(repo_root):
    dirs = DbSchemaReader.find_schema_dirs(str(repo_root))

    assert len(dirs) == 2
    assert Path(repo_root) / "apps" / "api" / "src" / "db" / "schema" in dirs
    assert Path(repo_root) / "src" / "db" / "schema" in dirs


def test_list_schema_files(repo_root):
    d1 = repo_root / "apps" / "api" / "src" / "db" / "schema"
    (d1 / "users.ts").touch()
    (d1 / "posts.ts").touch()
    (d1 / "index.ts").touch()  # Should be ignored

    d2 = repo_root / "src" / "db" / "schema"
    (d2 / "config.js").touch()
    (d2 / "index.js").touch()  # Should be ignored
    (d2 / "README.md").touch() # Should be ignored

    files = DbSchemaReader.list_schema_files(str(repo_root))

    assert len(files) == 3

    names = [f.name for f in files]
    assert "users.ts" in names
    assert "posts.ts" in names
    assert "config.js" in names
    assert "index.ts" not in names
    assert "index.js" not in names
    assert "README.md" not in names


def test_parse_drizzle_schema_valid(tmp_path, mock_drizzle_schema_content):
    schema_file = tmp_path / "schema.ts"
    schema_file.write_text(mock_drizzle_schema_content)

    tables = DbSchemaReader.parse_drizzle_schema(schema_file)

    assert len(tables) == 2

    users_table = tables[0]
    assert users_table["variable"] == "users"
    assert users_table["table_name"] == "users"
    assert users_table["file"] == "schema.ts"
    assert len(users_table["columns"]) == 3
    assert users_table["columns"][0]["name"] == "id"
    assert users_table["columns"][0]["type"] == "serial"
    assert users_table["columns"][1]["name"] == "name"
    assert users_table["columns"][1]["type"] == "text"

    posts_table = tables[1]
    assert posts_table["variable"] == "posts"
    assert posts_table["table_name"] == "posts"
    assert len(posts_table["columns"]) == 4


def test_parse_drizzle_schema_empty(tmp_path):
    schema_file = tmp_path / "empty.ts"
    schema_file.touch()

    tables = DbSchemaReader.parse_drizzle_schema(schema_file)
    assert tables == []


def test_parse_drizzle_schema_malformed(tmp_path):
    schema_file = tmp_path / "malformed.ts"
    schema_file.write_text("export const x = { this is not a valid schema }")

    tables = DbSchemaReader.parse_drizzle_schema(schema_file)
    assert tables == []


def test_parse_drizzle_schema_missing(tmp_path):
    schema_file = tmp_path / "missing.ts"

    tables = DbSchemaReader.parse_drizzle_schema(schema_file)
    assert tables == []


@patch("amb_cli.architecture.db_schema_reader.find_repo_root")
@patch("amb_cli.architecture.db_schema_reader.DbSchemaReader.list_schema_files")
@patch("amb_cli.architecture.db_schema_reader.DbSchemaReader.parse_drizzle_schema")
def test_show_schema(mock_parse, mock_list, mock_find, capsys):
    mock_find.return_value = "/mock/repo/root"
    mock_list.return_value = [Path("/mock/repo/root/schema.ts")]

    mock_parse.return_value = [
        {
            "variable": "users",
            "table_name": "users",
            "file": "schema.ts",
            "path": "/mock/repo/root/schema.ts",
            "columns": [
                {"name": "id", "type": "serial", "options": "'id').primaryKey()"}
            ]
        }
    ]

    # Test with no filter
    show_schema()
    captured = capsys.readouterr()
    assert "CATÁLOGO DE SCHEMAS DO BANCO DE DADOS" in captured.out
    assert "TABELA: " in captured.out
    assert "users" in captured.out
    assert "schema.ts" in captured.out
    assert "serial" in captured.out
    assert "Total de tabelas listadas:" in captured.out

    # Test with filter (matching)
    show_schema("users")
    captured = capsys.readouterr()
    assert "TABELA: " in captured.out
    assert "Total de tabelas listadas:" in captured.out

    # Test with filter (not matching)
    show_schema("nonexistent")
    captured = capsys.readouterr()
    assert "Nenhuma tabela encontrada com o termo: 'nonexistent'" in captured.out
    assert "Tabelas disponíveis no projeto:" in captured.out

    # Test empty state
    mock_list.return_value = []
    show_schema()
    captured = capsys.readouterr()
    assert "Nenhum diretório de schema Drizzle/DB encontrado" in captured.out
