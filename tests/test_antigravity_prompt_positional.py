import pytest
import os
import tempfile
import argparse
from unittest.mock import patch, MagicMock

from cli_modules.cli_parsers import create_parser
from cli_modules.handlers_core.antigravity_handler import handle_cmd_antigravity

@pytest.fixture
def parser():
    return create_parser()

@patch("integrations.antigravity.tools.synthesize_prompt.run_synthesize_prompt")
def test_antigravity_prompt_positional_string(mock_run, parser):
    """Testa argumento posicional direto de string."""
    mock_run.return_value = "Mocked Prompt"
    args = parser.parse_args(["agy", "prompt", "Minha ideia de app"])

    handle_cmd_antigravity(args)

    mock_run.assert_called_once_with(
        raw_idea="Minha ideia de app",
        role="general",
        output_file=None,
        image_path=None,
        queue=False
    )

@patch("integrations.antigravity.tools.synthesize_prompt.run_synthesize_prompt")
def test_antigravity_prompt_file_reading(mock_run, parser):
    """Testa a leitura automática de arquivo."""
    mock_run.return_value = "Mocked Prompt"

    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".md", encoding="utf-8") as f:
        f.write("Ideia vinda do arquivo MD.")
        temp_path = f.name

    try:
        args = parser.parse_args(["agy", "prompt", temp_path])
        handle_cmd_antigravity(args)

        mock_run.assert_called_once_with(
            raw_idea="Ideia vinda do arquivo MD.",
            role="general",
            output_file=None,
            image_path=None,
            queue=False
        )
    finally:
        os.remove(temp_path)

@patch("integrations.antigravity.tools.synthesize_prompt.run_synthesize_prompt")
def test_antigravity_prompt_harmonized_flags(mock_run, parser):
    """Testa o funcionamento da flag harmonizada de imagem/mockup (--image / -m) e flag legada -i."""
    mock_run.return_value = "Mocked Prompt"

    # Testa -i e -m
    args = parser.parse_args(["agy", "prompt", "-i", "Outra ideia", "-m", "mockup.png"])
    handle_cmd_antigravity(args)

    mock_run.assert_called_once_with(
        raw_idea="Outra ideia",
        role="general",
        output_file=None,
        image_path="mockup.png",
        queue=False
    )

    mock_run.reset_mock()

    # Testa fallback para posicional e --image
    args = parser.parse_args(["agy", "prompt", "Ideia posicional", "--image", "mockup.jpg"])
    handle_cmd_antigravity(args)

    mock_run.assert_called_once_with(
        raw_idea="Ideia posicional",
        role="general",
        output_file=None,
        image_path="mockup.jpg",
        queue=False
    )

@patch("core.logger.log_error")
@patch("integrations.antigravity.tools.synthesize_prompt.run_synthesize_prompt")
def test_antigravity_prompt_no_idea_provided(mock_run, mock_log_error, parser):
    """Testa tratamento gracioso quando nenhum texto de ideia é fornecido."""
    args = parser.parse_args(["agy", "prompt"])

    handle_cmd_antigravity(args)

    # run_synthesize_prompt não deve ser chamado
    mock_run.assert_not_called()

    # log_error deve ser chamado
    mock_log_error.assert_called_once()
    assert "Nenhuma ideia ou arquivo fornecido" in mock_log_error.call_args[0][1]
