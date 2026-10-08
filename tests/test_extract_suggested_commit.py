import pytest
from unittest.mock import patch, MagicMock

from integrations.jules.jules_core.session_extractor import SessionExtractor
from integrations.jules.tools.extract_session import run_extract_session

def test_extract_commit_message_present():
    payload = {
        "outputs": [
            {
                "changeSet": {
                    "gitPatch": {
                        "suggestedCommitMessage": "Add authentication tests"
                    }
                }
            }
        ]
    }
    msg = SessionExtractor.extract_commit_message(payload)
    assert msg == "Add authentication tests"

def test_extract_commit_message_missing():
    payload = {
        "outputs": [
            {
                "changeSet": {
                    "gitPatch": {
                        "unidiffPatch": "patch content"
                    }
                }
            }
        ]
    }
    msg = SessionExtractor.extract_commit_message(payload)
    assert msg is None

def test_extract_commit_message_no_outputs():
    payload = {"outputs": []}
    msg = SessionExtractor.extract_commit_message(payload)
    assert msg is None

def test_extract_commit_message_empty():
    payload = {
        "outputs": [
            {
                "changeSet": {
                    "gitPatch": {
                        "suggestedCommitMessage": ""
                    }
                }
            }
        ]
    }
    msg = SessionExtractor.extract_commit_message(payload)
    assert msg is None

@patch("builtins.print")
@patch("integrations.jules.tools.extract_session.JulesClient")
@patch("integrations.jules.tools.extract_session.SessionExtractor.extract_patch")
@patch("integrations.jules.tools.extract_session.SessionExtractor.save_patch")
def test_run_extract_session_displays_suggested_commit(mock_save, mock_extract, mock_client_cls, mock_print, tmp_path):
    mock_client = MagicMock()
    mock_client_cls.return_value = mock_client
    mock_client.normalize_session_id.return_value = "123"
    mock_client.get_session.return_value = {
        "outputs": [
            {
                "changeSet": {
                    "gitPatch": {
                        "unidiffPatch": "patch",
                        "suggestedCommitMessage": "Test commit message"
                    }
                }
            }
        ]
    }
    mock_extract.return_value = "patch"

    dest = tmp_path / "dest.patch"

    run_extract_session("session/123", dest=str(dest), apply=False)

    # Check if the suggested commit message was printed
    mock_print.assert_any_call('  • Commit sugerido: "Test commit message"')

@patch("builtins.print")
@patch("integrations.jules.tools.extract_session.JulesClient")
@patch("integrations.jules.tools.extract_session.SessionExtractor.extract_patch")
@patch("integrations.jules.tools.extract_session.SessionExtractor.save_patch")
def test_run_extract_session_no_suggested_commit(mock_save, mock_extract, mock_client_cls, mock_print, tmp_path):
    mock_client = MagicMock()
    mock_client_cls.return_value = mock_client
    mock_client.normalize_session_id.return_value = "123"
    mock_client.get_session.return_value = {
        "outputs": [
            {
                "changeSet": {
                    "gitPatch": {
                        "unidiffPatch": "patch"
                    }
                }
            }
        ]
    }
    mock_extract.return_value = "patch"

    dest = tmp_path / "dest.patch"

    run_extract_session("session/123", dest=str(dest), apply=False)

    # Verify that the suggested commit message wasn't printed (it shouldn't be in the mock calls)
    for call in mock_print.call_args_list:
        assert '  • Commit sugerido:' not in call.args[0]
