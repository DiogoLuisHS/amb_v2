import os
import pytest
from unittest.mock import patch
from amb_cli.core.diagnostics import run_environment_diagnostics

def mock_find_repo_root(tmp_path):
    return str(tmp_path)

def mock_load_project_json():
    return {}

@patch("amb_cli.core.diagnostics.find_repo_root")
@patch("amb_cli.core.diagnostics.load_project_json", return_value={})
def test_check_without_fix_does_not_modify_files(mock_load, mock_find, tmp_path):
    mock_find.return_value = str(tmp_path)
    env_file = tmp_path / ".env"
    env_file.write_text("DUMMY=1")

    run_environment_diagnostics(fix=False)

    # Should not create .env.example
    assert not (tmp_path / ".env.example").exists()

    # Should not modify or create .gitignore
    assert not (tmp_path / ".gitignore").exists()

@patch("amb_cli.core.diagnostics.find_repo_root")
@patch("amb_cli.core.diagnostics.load_project_json", return_value={})
def test_check_with_fix_adds_gitignore(mock_load, mock_find, tmp_path):
    mock_find.return_value = str(tmp_path)
    env_file = tmp_path / ".env"
    env_file.write_text("DUMMY=1")

    run_environment_diagnostics(fix=True)

    # Gitignore should be created and contain .env
    gitignore_path = tmp_path / ".gitignore"
    assert gitignore_path.exists()
    content = gitignore_path.read_text()
    assert ".env" in content

@patch("amb_cli.core.diagnostics.find_repo_root")
@patch("amb_cli.core.diagnostics.load_project_json", return_value={})
def test_check_with_fix_creates_env_example(mock_load, mock_find, tmp_path):
    mock_find.return_value = str(tmp_path)

    # No .env.example exists initially
    run_environment_diagnostics(fix=True)

    env_example_path = tmp_path / ".env.example"
    assert env_example_path.exists()
    content = env_example_path.read_text()
    assert "GITHUB_REPOSITORY=" in content
    assert "JULES_API_KEY=" in content

@patch("amb_cli.core.diagnostics.find_repo_root")
@patch("amb_cli.core.diagnostics.load_project_json", return_value={})
def test_check_with_fix_idempotency(mock_load, mock_find, tmp_path):
    mock_find.return_value = str(tmp_path)
    env_file = tmp_path / ".env"
    env_file.write_text("DUMMY=1")

    # Run first time
    run_environment_diagnostics(fix=True)
    gitignore_path = tmp_path / ".gitignore"
    assert gitignore_path.exists()

    # Count occurrences of .env in .gitignore
    content1 = gitignore_path.read_text()
    occurrences_before = content1.split().count(".env")

    # Run second time
    run_environment_diagnostics(fix=True)

    content2 = gitignore_path.read_text()
    occurrences_after = content2.split().count(".env")

    assert occurrences_before == 1
    assert occurrences_after == 1
