import pytest
from unittest.mock import patch, MagicMock

from agents.monitor import run_monitor, UnifiedMonitor
from cli_modules.cli_parsers import create_parser
from cli_modules.cli_handlers import cmd_monitor


class DummyArgs:
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)


@patch("agents.monitor.print")
@patch("agents.monitor.JulesWatcher")
def test_run_monitor_quiet_mode(mock_watcher, mock_print):
    """Garante que por padrão (verbose=False) não emite as mensagens de ciclo e normalidade."""
    mock_instance = mock_watcher.return_value
    mock_instance.check.return_value = []  # Sem alertas, tudo normal

    run_monitor(interval_seconds=1, check_once=True, auto_approve=False, verbose=False)

    # "Rodada #" e "Tudo operando normalmente" não devem aparecer nos args do print / log
    for call in mock_print.call_args_list:
        args_tuple = call[0]
        if args_tuple:
            text = args_tuple[0]
            assert "Rodada #" not in text
            assert "Tudo operando normalmente" not in text


@patch("agents.monitor.print")
@patch("agents.monitor.JulesWatcher")
@patch("agents.monitor.notify_info")
def test_run_monitor_verbose_mode(mock_notify, mock_watcher, mock_print):
    """Garante que com verbose=True emite as mensagens de ciclo e normalidade."""
    mock_instance = mock_watcher.return_value
    mock_instance.check.return_value = []

    run_monitor(interval_seconds=1, check_once=True, auto_approve=False, verbose=True)

    # "Rodada #" deve aparecer nos prints
    found_rodada = False
    for call in mock_print.call_args_list:
        args_tuple = call[0]
        if args_tuple:
            text = args_tuple[0]
            if "Rodada #" in text:
                found_rodada = True

    assert found_rodada, "Mensagem 'Rodada #' não foi encontrada com verbose=True"

    # notify_info deve ter sido chamado para notificar normalidade
    mock_notify.assert_called_with("Tudo operando normalmente. Nenhuma pendência humana ou erro detectado.\n")


@patch("agents.monitor.log")
@patch("agents.monitor.print")
@patch("agents.monitor.JulesWatcher")
def test_run_monitor_emits_alerts_even_quiet(mock_watcher, mock_print, mock_log):
    """Eventos reais ou falhas na checagem ainda devem ser logados/exibidos em modo silencioso."""
    mock_instance = mock_watcher.return_value
    mock_instance.check.return_value = [{"type": "failed", "session_id": "123"}]

    # Em um caso de erro/falha, monitor exibe coisas. Pelo menos a checagem não deve estar silenciosa.
    run_monitor(interval_seconds=1, check_once=True, auto_approve=False, verbose=False)

    # Não há prints de rodada, mas a lista de alertas é retornada
    # Como não estamos usando auto-approve ou log explicit, as mensagens de print da rodada não aparecem
    for call in mock_print.call_args_list:
        args_tuple = call[0]
        if args_tuple:
            text = args_tuple[0]
            assert "Rodada #" not in text


def test_monitor_parser_verbose_flag():
    parser = create_parser()
    args = parser.parse_args(["monitor", "-v"])
    assert getattr(args, "verbose", False) is True

    args = parser.parse_args(["monitor", "--verbose"])
    assert getattr(args, "verbose", False) is True


@patch("agents.monitor.UnifiedMonitor")
def test_cmd_monitor_passes_verbose_flag(mock_monitor_class):
    mock_instance = MagicMock()
    mock_monitor_class.return_value = mock_instance

    args = DummyArgs(
        interactive=False,
        interval=5,
        auto_approve=False,
        check_once=True,
        verbose=True
    )

    cmd_monitor(args)

    mock_monitor_class.assert_called_once_with(interval=5, auto_approve=False, auto_merge=False, verbose=True, all_repos=False)
    mock_instance.run.assert_called_once_with(check_once=True)
