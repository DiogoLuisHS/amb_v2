from unittest.mock import patch, MagicMock

from amb_cli.agents.monitor import run_monitor
from amb_cli.cli_modules.cli_parsers import create_parser
from amb_cli.cli_modules.cli_handlers import cmd_monitor


@patch("amb_cli.agents.monitor.time.sleep")
@patch("amb_cli.agents.monitor.JulesWatcher")
def test_run_monitor_auto_merge_invoked(mock_watcher_class, mock_sleep):
    fake_alerts = [
        {
            "type": "completed_needs_merge",
            "session_id": "session_123",
            "pr": {"number": 42},
        }
    ]

    mock_watcher = MagicMock()
    mock_watcher.check.return_value = fake_alerts
    mock_watcher_class.return_value = mock_watcher

    # Patch no coletor de alertas e no módulo de origem da função de merge:
    with patch("amb_cli.integrations.jules.tools.merge_session_pr.approve_and_merge_pr") as mock_merge:
        run_monitor(check_once=True, auto_merge=True)

        mock_merge.assert_called_once_with(session_id="session_123", target_branch="main")


@patch("amb_cli.agents.monitor.time.sleep")
@patch("amb_cli.agents.monitor.JulesWatcher")
def test_run_monitor_auto_merge_disabled(mock_watcher_class, mock_sleep):
    fake_alerts = [
        {
            "type": "completed_needs_merge",
            "session_id": "session_123",
            "pr": {"number": 42},
        }
    ]
    mock_watcher = MagicMock()
    mock_watcher.check.return_value = fake_alerts
    mock_watcher_class.return_value = mock_watcher

    with patch("amb_cli.integrations.jules.tools.merge_session_pr.approve_and_merge_pr") as mock_merge:
        run_monitor(check_once=True, auto_merge=False)

        mock_merge.assert_not_called()


@patch("amb_cli.agents.monitor.time.sleep")
@patch("amb_cli.agents.monitor.JulesWatcher")
def test_run_monitor_auto_merge_resilience(mock_watcher_class, mock_sleep):
    fake_alerts = [
        {
            "type": "completed_needs_merge",
            "session_id": "session_123",
            "pr": {"number": 42},
        }
    ]
    mock_watcher = MagicMock()
    mock_watcher.check.return_value = fake_alerts
    mock_watcher_class.return_value = mock_watcher

    # Simula falha/exceção no merge para garantir que o monitor captura e não quebra o loop
    with patch("amb_cli.integrations.jules.tools.merge_session_pr.approve_and_merge_pr", side_effect=Exception("Merge conflict")):
        with patch("amb_cli.agents.monitor.log_error") as mock_log_error:
            # Não deve levantar exceção
            run_monitor(check_once=True, auto_merge=True)
            mock_log_error.assert_called()


def test_cmd_monitor_passes_auto_merge_flag():
    args = MagicMock()
    args.auto_merge = True
    args.interval = 15
    args.check_once = True
    args.auto_approve = False
    args.verbose = False
    args.interactive = False

    with patch("amb_cli.cli_modules.cli_handlers.UnifiedMonitor", create=True) as mock_monitor_cls:
        instance = mock_monitor_cls.return_value

        # A importação acontece localmente no cmd_monitor, então temos que patchear lá também.
        import builtins
        original_import = builtins.__import__
        def mock_import(name, *args, **kwargs):
            if name == "agents.monitor":
                mock_module = MagicMock()
                mock_module.UnifiedMonitor = mock_monitor_cls
                return mock_module
            return original_import(name, *args, **kwargs)

        with patch("builtins.__import__", side_effect=mock_import):
            cmd_monitor(args)

        mock_monitor_cls.assert_called_once()
        _, kwargs = mock_monitor_cls.call_args
        assert kwargs.get("auto_merge") is True
        instance.run.assert_called_once_with(check_once=True)


def test_cli_parser_auto_merge():
    parser = create_parser()
    parsed = parser.parse_args(["monitor", "--auto-merge"])
    assert parsed.auto_merge is True

    parsed_default = parser.parse_args(["monitor"])
    assert parsed_default.auto_merge is False
