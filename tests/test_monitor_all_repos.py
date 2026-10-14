import pytest
from unittest.mock import MagicMock, patch

from integrations.jules.jules_watcher import JulesWatcher
from integrations.jules.jules_core.session_state import SessionState
from cli_modules.cli_parsers import create_parser

def test_jules_watcher_all_repos_true():
    """Testa se JulesWatcher(all_repos=True) chama list_sessions com repo_filter=None."""
    mock_client = MagicMock()
    # Retorna uma lista vazia para evitar erro no loop
    mock_client.list_sessions.return_value = []

    watcher = JulesWatcher(client=mock_client, all_repos=True)
    watcher.check()

    # Deve chamar list_sessions com repo_filter=None
    mock_client.list_sessions.assert_called_once_with(page_size=50, repo_filter=None)

@patch("integrations.jules.jules_watcher.get_repo_name")
def test_jules_watcher_all_repos_false(mock_get_repo_name):
    """Testa se JulesWatcher(all_repos=False) preserva o filtro pelo repositório local."""
    mock_repo_name = "test_owner/test_repo"
    mock_get_repo_name.return_value = mock_repo_name

    mock_client = MagicMock()
    mock_client.list_sessions.return_value = []

    watcher = JulesWatcher(client=mock_client, all_repos=False)
    watcher.check()

    # Deve chamar list_sessions com repo_filter=test_owner/test_repo
    mock_client.list_sessions.assert_called_once_with(page_size=50, repo_filter=mock_repo_name)


@patch("integrations.jules.jules_watcher.notify_attention")
def test_jules_watcher_alert_formatting_multi_repo(mock_notify_attention):
    """Testa se a formatação de alertas inclui o nome do repositório no modo multi-repo."""
    mock_client = MagicMock()

    # Configura uma sessão mock aguardando feedback
    mock_session = {
        "name": "sessions/123",
        "id": "123",
        "state": "AWAITING_USER_FEEDBACK",
        "title": "Fix bug",
        "sourceContext": {
            "source": "sources/github/owner/repo"
        }
    }

    mock_client.list_sessions.return_value = [mock_session]

    # Simula atividade do agente aguardando usuário
    mock_activity = {
        "id": "act_1",
        "createTime": "2023-10-14T00:00:00Z",
        "activityType": "MESSAGE",
        "message": {
            "role": "AGENT",
            "content": "Please review"
        }
    }

    # Vamos mockar o get_last_conversation_turn para simular que o agente está esperando
    with patch("integrations.jules.jules_watcher.get_repo_name", return_value="current/repo"), \
         patch("auto_reply.get_last_conversation_turn") as mock_turn:

        mock_turn.return_value = {
            "is_awaiting_user_action": True,
            "last_agent_msg_id": "act_1",
            "last_agent_msg": "Please review"
        }

        watcher = JulesWatcher(client=mock_client, all_repos=True)
        alerts = watcher.check()

        assert len(alerts) == 1
        assert alerts[0]["type"] == "awaiting_feedback"

        # Verifica se o título formatado na notificação tem o prefixo "[owner/repo]"
        mock_notify_attention.assert_called_once()
        called_kwargs = mock_notify_attention.call_args.kwargs
        assert "[owner/repo]" in called_kwargs["title"]
        assert "Fix bug" in called_kwargs["title"]


def test_monitor_all_repos_cli_parsing():
    """Testa o parsing da flag --all / --all-repos no subparser de amb monitor."""
    parser = create_parser()

    # Testa sem flag (all_repos deve ser False)
    args_none = parser.parse_args(["monitor"])
    assert getattr(args_none, "all_repos", False) is False

    # Testa com --all
    args_all = parser.parse_args(["monitor", "--all"])
    assert getattr(args_all, "all_repos", False) is True

    # Testa com --all-repos
    args_all_repos = parser.parse_args(["monitor", "--all-repos"])
    assert getattr(args_all_repos, "all_repos", False) is True
