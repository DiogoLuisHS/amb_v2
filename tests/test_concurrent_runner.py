import pytest
from unittest.mock import patch, MagicMock

from agents.loop_core.concurrent_runner import ConcurrentLoopRunner

@pytest.fixture
def mock_dependencies():
    with patch("agents.loop_core.concurrent_runner.dispatch_jules_session") as mock_dispatch, \
         patch("agents.loop_core.concurrent_runner.monitor_and_assist_session") as mock_monitor, \
         patch("agents.loop_core.concurrent_runner.handle_pr_merge") as mock_merge:

        mock_dispatch.return_value = "mock_session_id"
        mock_monitor.return_value = "COMPLETED"
        mock_merge.return_value = True

        yield mock_dispatch, mock_monitor, mock_merge


def test_concurrent_runner_execution_and_merge_sequence(mock_dependencies):
    mock_dispatch, mock_monitor, mock_merge = mock_dependencies

    mock_client = MagicMock()
    mock_syncer = MagicMock()

    items = [
        {"name": "prompt_1", "type": "prompt", "_full_prompt": "content_1", "_session_title": "title_1"},
        {"name": "prompt_2", "type": "prompt", "_full_prompt": "content_2", "_session_title": "title_2"},
        {"name": "issue_3", "type": "issue", "issue_number": 3, "title": "Issue 3", "_full_prompt": "content_3", "_session_title": "title_3"},
    ]

    runner = ConcurrentLoopRunner(
        items=items,
        max_concurrency=2,
        client=mock_client,
        branch="main",
        repo_root="/test/repo",
        source_name="sources/github/test/repo",
        completed_cycles=1,
        syncer=mock_syncer,
        no_auto_merge=False
    )

    result = runner.run()

    assert result is True

    # 3 itens na fila = 3 chamadas para dispatch e monitor
    assert mock_dispatch.call_count == 3
    assert mock_monitor.call_count == 3

    # Se todos completaram com sucesso e merge = True, deve haver 3 chamadas de merge
    assert mock_merge.call_count == 3

    # Verifica que issue closure foi chamado para o item de issue
    mock_syncer.close_issue.assert_called_once_with(
        3,
        comment="✅ Concluído e integrado com sucesso pelo AMB_V2 (Sessão Jules: mock_session_id, Ciclo #1)."
    )

def test_concurrent_runner_with_failures(mock_dependencies):
    mock_dispatch, mock_monitor, mock_merge = mock_dependencies

    # Faz com que a primeira chamada de monitor retorne falha e a segunda sucesso
    mock_monitor.side_effect = ["FAILED", "COMPLETED"]

    mock_client = MagicMock()

    items = [
        {"name": "prompt_1", "type": "prompt", "_full_prompt": "content_1", "_session_title": "title_1"},
        {"name": "prompt_2", "type": "prompt", "_full_prompt": "content_2", "_session_title": "title_2"},
    ]

    runner = ConcurrentLoopRunner(
        items=items,
        max_concurrency=2,
        client=mock_client,
        branch="main",
        repo_root="/test/repo",
        source_name="sources/github/test/repo",
        completed_cycles=1,
        syncer=None,
        no_auto_merge=False
    )

    result = runner.run()

    # Deveria retornar false, já que um item falhou
    assert result is False

    assert mock_dispatch.call_count == 2
    assert mock_monitor.call_count == 2

    # O item com falha não deve gerar um PR merge call, apenas o de sucesso
    assert mock_merge.call_count == 1
