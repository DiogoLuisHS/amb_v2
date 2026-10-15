import pytest
from unittest.mock import patch, MagicMock
from amb_cli.cli_modules.cli_parsers import create_parser
from amb_cli.cli_modules.handlers_core.loop_handler import handle_cmd_loop
from amb_cli.cli_modules.handlers_core.persona_handler import cmd_persona

def test_parser_no_dispatch_jules():
    """Verifica se a flag --dispatch-jules foi removida do parser do agente."""
    parser = create_parser()

    # Simula o parsing para garantir que nâo existe
    # argparse should raise SystemExit on invalid argument
    with pytest.raises(SystemExit):
        parser.parse_args(["agent", "--dispatch-jules"])

    with pytest.raises(SystemExit):
        parser.parse_args(["agent", "-j"])

def test_parser_concurrency_and_loop():
    """Verifica o parsing inequívoco de --concurrency e --loop."""
    parser = create_parser()
    args = parser.parse_args(["agent", "test", "--concurrency", "3", "--loop"])

    assert args.concurrency == 3
    assert args.loop is True

    args = parser.parse_args(["agent", "test", "-c", "5", "--continuous"])
    assert args.concurrency == 5
    assert args.loop is True

@patch("amb_cli.cli_modules.handlers_core.loop_handler.LoopStateMachine")
@patch("builtins.print")
def test_loop_default_status(mock_print, mock_machine):
    """Verifica se 'amb loop' sem subcomando chama status."""
    class Args:
        loop_cmd = None

    mock_instance = mock_machine.return_value
    mock_instance.get_current_state.return_value = {"state": "idle"}

    handle_cmd_loop(Args())

    mock_instance.get_current_state.assert_called_once()
    assert any("=== AMB Loop Status ===" in call.args[0] for call in mock_print.call_args_list)


@patch("amb_cli.cli_modules.handlers_core.persona_handler.PersonaEngine")
@patch("builtins.print")
def test_persona_default_list(mock_print, mock_engine, tmp_path):
    """Verifica se 'amb persona' sem subcomando chama list."""
    class Args:
        persona_cmd = None

    mock_instance = mock_engine.return_value
    mock_instance.personas_dir = str(tmp_path)

    # Criar algumas personas fake
    (tmp_path / "valida.md").touch()
    (tmp_path / "incompleta.md").touch()

    # Simular a validação
    def mock_validate(filepath):
        if "incompleta" in filepath:
            return ["Erro falso"]
        return []

    mock_instance.validate_persona_file.side_effect = mock_validate

    cmd_persona(Args())

    calls_str = [call.args[0] for call in mock_print.call_args_list]
    assert any("valida" in s and "✅ Válida" in s for s in calls_str)
    assert any("incompleta" in s and "⚠️ Incompleta" in s for s in calls_str)
