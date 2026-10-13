import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock
import os

from amb_cli.workspace.project_context import get_next_prompt_filepath
from amb_cli.integrations.antigravity.tools.synthesize_prompt import run_synthesize_prompt

def test_get_next_prompt_filepath_empty_dir(tmp_path):
    prompts_dir = tmp_path / ".amb" / "prompts"
    prompts_dir.mkdir(parents=True, exist_ok=True)

    result = get_next_prompt_filepath(prompts_dir, "Nova User Story")

    assert result == prompts_dir / "01_us1_nova-user-story.md"

def test_get_next_prompt_filepath_existing_files(tmp_path):
    prompts_dir = tmp_path / ".amb" / "prompts"
    prompts_dir.mkdir(parents=True, exist_ok=True)

    (prompts_dir / "15_us15_alguma-coisa.md").touch()
    (prompts_dir / "04_us4_outra-coisa.md").touch()

    result = get_next_prompt_filepath(prompts_dir, "My super feature")
    assert result == prompts_dir / "16_us16_my-super-feature.md"

def test_get_next_prompt_filepath_with_completed(tmp_path):
    prompts_dir = tmp_path / ".amb" / "prompts"
    completed_dir = prompts_dir / "_completed"
    prompts_dir.mkdir(parents=True, exist_ok=True)
    completed_dir.mkdir(parents=True, exist_ok=True)

    (prompts_dir / "10_us10_active.md").touch()
    (completed_dir / "30_us30_done.md").touch()

    result = get_next_prompt_filepath(prompts_dir, "New Test")
    assert result == prompts_dir / "31_us31_new-test.md"

def test_get_next_prompt_filepath_slug_sanitization(tmp_path):
    prompts_dir = tmp_path / ".amb" / "prompts"
    prompts_dir.mkdir(parents=True, exist_ok=True)

    # Should sanitize properly
    result = get_next_prompt_filepath(prompts_dir, "  Feature (com acentos) & symbols! ")
    assert result == prompts_dir / "01_us1_feature-com-acentos-symbols.md"

    # Should fallback to "prompt" if empty after sanitization
    result2 = get_next_prompt_filepath(prompts_dir, "!!!@@@")
    assert result2 == prompts_dir / "01_us1_prompt.md"


@patch("amb_cli.integrations.antigravity.tools.synthesize_prompt.synthesize_prompt")
def test_run_synthesize_prompt_queue_enabled(mock_synthesize_prompt, tmp_path):
    mock_synthesize_prompt.return_value = "# Criando Login\n\nEste é o prompt..."

    prompts_dir = tmp_path / ".amb" / "prompts"
    prompts_dir.mkdir(parents=True, exist_ok=True)
    (prompts_dir / "05_us5_previous.md").touch()

    # The actual implementation calls find_repo_root(), which looks around the filesystem.
    # We mock os.getcwd inside find_repo_root to trick it into looking at tmp_path,
    # OR we use os.chdir(tmp_path) to just let it find it.
    # The simplest is to chdir to tmp_path and create an amb_project.json there.

    # Create marker so find_repo_root stops at tmp_path
    (tmp_path / "amb_project.json").touch()
    old_cwd = os.getcwd()
    os.chdir(str(tmp_path))

    try:
        res = run_synthesize_prompt(
            raw_idea="Criar tela de login",
            role="general",
            queue=True
        )

        assert res == "# Criando Login\n\nEste é o prompt..."

        expected_file = prompts_dir / "06_us6_criando-login.md"
        assert expected_file.exists()
        assert expected_file.read_text(encoding="utf-8") == res
    finally:
        os.chdir(old_cwd)


@patch("amb_cli.integrations.antigravity.tools.synthesize_prompt.synthesize_prompt")
def test_run_synthesize_prompt_queue_with_output_file(mock_synthesize_prompt, tmp_path):
    mock_synthesize_prompt.return_value = "# Nova Feature\n\n..."

    custom_output = tmp_path / "custom.md"

    (tmp_path / "amb_project.json").touch()
    old_cwd = os.getcwd()
    os.chdir(str(tmp_path))

    try:
        run_synthesize_prompt(
            raw_idea="Nova feature",
            output_file=str(custom_output),
            queue=True
        )

        assert custom_output.exists()
        prompts_dir = tmp_path / ".amb" / "prompts"
        assert not (prompts_dir / "01_us1_nova-feature.md").exists()
    finally:
        os.chdir(old_cwd)
