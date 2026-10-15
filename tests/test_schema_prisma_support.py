import pytest
import json
from pathlib import Path
from unittest.mock import patch, MagicMock
from typing import Dict, Any, List

from amb_cli.architecture.db_schema_reader import DbSchemaReader, show_schema


@pytest.fixture
def mock_prisma_schema_content():
    return """
// This is a comment
model User {
  id    Int     @id @default(autoincrement())
  email String  @unique
  name  String?
  @@map("users")
}

model Post {
  id        Int      @id @default(autoincrement())
  title     String
  content   String?
  published Boolean  @default(false)
  authorId  Int
}
"""

@pytest.fixture
def mock_prisma_schema_file(tmp_path):
    d = tmp_path / "prisma"
    d.mkdir()
    p = d / "schema.prisma"
    p.write_text("""
model User {
  id    Int     @id @default(autoincrement())
  email String  @unique
  name  String?
}
""")
    return p


def test_find_schema_dirs_with_prisma(tmp_path):
    # Setup mock structure
    (tmp_path / "prisma").mkdir()
    (tmp_path / "src" / "prisma").mkdir(parents=True)

    dirs = DbSchemaReader.find_schema_dirs(str(tmp_path))

    assert tmp_path in dirs
    assert tmp_path / "prisma" in dirs
    assert tmp_path / "src" / "prisma" in dirs


def test_list_schema_files_prisma(tmp_path):
    (tmp_path / "prisma").mkdir()
    p = tmp_path / "prisma" / "schema.prisma"
    p.touch()

    files = DbSchemaReader.list_schema_files(str(tmp_path))
    assert p in files


def test_parse_prisma_schema(tmp_path, mock_prisma_schema_content):
    p = tmp_path / "schema.prisma"
    p.write_text(mock_prisma_schema_content)

    tables = DbSchemaReader.parse_prisma_schema(p)

    assert len(tables) == 2

    user_table = tables[0]
    assert user_table["variable"] == "User"
    assert user_table["table_name"] == "user"
    assert user_table["file"] == "schema.prisma"
    assert len(user_table["columns"]) == 3

    assert user_table["columns"][0]["name"] == "id"
    assert user_table["columns"][0]["type"] == "Int"
    assert user_table["columns"][0]["options"] == "@id @default(autoincrement())"

    assert user_table["columns"][1]["name"] == "email"
    assert user_table["columns"][1]["type"] == "String"
    assert user_table["columns"][1]["options"] == "@unique"

    assert user_table["columns"][2]["name"] == "name"
    assert user_table["columns"][2]["type"] == "String?"
    assert user_table["columns"][2]["options"] == ""

    post_table = tables[1]
    assert post_table["variable"] == "Post"
    assert post_table["table_name"] == "post"
    assert len(post_table["columns"]) == 5


@patch('amb_cli.architecture.db_schema_reader.find_repo_root')
@patch('amb_cli.architecture.db_schema_reader.DbSchemaReader.list_schema_files')
def test_show_schema_json(mock_list, mock_root, tmp_path, mock_prisma_schema_file, capsys):
    mock_root.return_value = str(tmp_path)
    mock_list.return_value = [mock_prisma_schema_file]

    show_schema(as_json=True)

    captured = capsys.readouterr()
    output_json = json.loads(captured.out)

    assert output_json["total_tables"] == 1
    assert output_json["tables"][0]["variable"] == "User"
    assert output_json["tables"][0]["columns"][0]["name"] == "id"


@patch('amb_cli.architecture.db_schema_reader.find_repo_root')
@patch('amb_cli.architecture.db_schema_reader.DbSchemaReader.list_schema_files')
def test_show_schema_terminal(mock_list, mock_root, tmp_path, mock_prisma_schema_file, capsys):
    mock_root.return_value = str(tmp_path)
    mock_list.return_value = [mock_prisma_schema_file]

    show_schema()

    captured = capsys.readouterr()
    output = captured.out

    assert "CATÁLOGO DE SCHEMAS DO BANCO DE DADOS" in output
    assert "User" in output
    assert "schema.prisma" in output
    assert "id" in output
    assert "@id @default(autoincrement())" in output
