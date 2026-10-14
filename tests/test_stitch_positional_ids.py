import pytest
from unittest.mock import MagicMock, patch
from amb_cli.cli_modules.cli_parsers import create_parser

@pytest.fixture
def parser():
    return create_parser()

@patch("integrations.stitch.stitch_client.StitchClient")
@patch("core.log_error")
@patch("core.log")
def test_stitch_get_positional(mock_log, mock_log_error, mock_stitch_client, parser):
    """Testa 'amb stitch get <id>' com ID passado diretamente posicional."""
    args = parser.parse_args(["stitch", "get", "SCREEN_123"])

    # Simula a instância do client mockado
    instance = mock_stitch_client.return_value
    instance.get_screen.return_value = {"title": "Test Screen", "htmlCode": "<html>"}

    # Chama o handler (precisamos importá-lo aqui)
    from amb_cli.cli_modules.handlers_core.stitch_handler import handle_cmd_stitch
    handle_cmd_stitch(args)

    instance.get_screen.assert_called_once_with(screen_id="SCREEN_123", output_file=None)
    mock_log.assert_called_with("STITCH", "Detalhes da tela SCREEN_123 obtidos com sucesso.", "\033[92m")
    mock_log_error.assert_not_called()

@patch("integrations.stitch.stitch_client.StitchClient")
@patch("core.log_error")
def test_stitch_get_missing_id(mock_log_error, mock_stitch_client, parser):
    """Testa 'amb stitch get' sem argumentos para validar mensagem amigável."""
    args = parser.parse_args(["stitch", "get"])

    from amb_cli.cli_modules.handlers_core.stitch_handler import handle_cmd_stitch
    handle_cmd_stitch(args)

    mock_log_error.assert_called_once_with("O ID da tela é obrigatório. Ex: amb stitch get <id>")
    mock_stitch_client.return_value.get_screen.assert_not_called()

@patch("integrations.stitch.stitch_client.StitchClient")
@patch("core.log_error")
@patch("core.log")
def test_stitch_refine_positional(mock_log, mock_log_error, mock_stitch_client, parser):
    """Testa 'amb stitch refine <id> "<prompt>"' com ambos os argumentos posicionais."""
    args = parser.parse_args(["stitch", "refine", "SCREEN_123", "Ajustar contraste dos botões"])

    instance = mock_stitch_client.return_value
    instance.edit_screen.return_value = {"screenshotUrl": "http://example.com/img.png"}

    from amb_cli.cli_modules.handlers_core.stitch_handler import handle_cmd_stitch
    handle_cmd_stitch(args)

    instance.edit_screen.assert_called_once_with(
        screen_id="SCREEN_123",
        prompt="Ajustar contraste dos botões",
        device_type=None,
        output_file=None
    )
    mock_log.assert_called_with("STITCH", "Tela SCREEN_123 refinada com sucesso!", "\033[92m")
    mock_log_error.assert_not_called()

@patch("integrations.stitch.stitch_client.StitchClient")
@patch("core.log_error")
def test_stitch_refine_missing_args(mock_log_error, mock_stitch_client, parser):
    """Testa 'amb stitch refine' sem argumentos para validar mensagem amigável."""
    args = parser.parse_args(["stitch", "refine"])

    from amb_cli.cli_modules.handlers_core.stitch_handler import handle_cmd_stitch
    handle_cmd_stitch(args)

    mock_log_error.assert_called_once_with("O ID da tela e o prompt são obrigatórios para refinamento. Ex: amb stitch refine <id> \"<prompt>\"")
    mock_stitch_client.return_value.edit_screen.assert_not_called()

@patch("integrations.stitch.stitch_client.StitchClient")
@patch("core.log_error")
@patch("core.log")
def test_stitch_refine_missing_prompt(mock_log, mock_log_error, mock_stitch_client, parser):
    """Testa 'amb stitch refine <id>' sem o prompt para validar mensagem amigável."""
    args = parser.parse_args(["stitch", "refine", "SCREEN_123"])

    from amb_cli.cli_modules.handlers_core.stitch_handler import handle_cmd_stitch
    handle_cmd_stitch(args)

    mock_log_error.assert_called_once_with("O ID da tela e o prompt são obrigatórios para refinamento. Ex: amb stitch refine <id> \"<prompt>\"")
    mock_stitch_client.return_value.edit_screen.assert_not_called()
