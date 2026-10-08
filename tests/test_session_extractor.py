import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

from core.exceptions import AmbError
from integrations.jules.jules_core.session_extractor import SessionExtractor
from integrations.jules.tools.extract_session import run_extract_session

def test_extract_patch_success():
    payload = {
        "outputs": [
            {
                "changeSet": {
                    "gitPatch": {
                        "unidiffPatch": "--- a/test.py\n+++ b/test.py\n@@ -1,1 +1,2 @@\n-print('hello')\n+print('hello')\n+print('world')"
                    }
                }
            }
        ]
    }
    patch_str = SessionExtractor.extract_patch(payload)
    assert "print('world')" in patch_str

def test_extract_patch_no_outputs():
    payload = {"outputs": []}
    with pytest.raises(AmbError, match="A sessão não contém outputs."):
        SessionExtractor.extract_patch(payload)

def test_extract_patch_no_unidiff():
    payload = {
        "outputs": [
            {"otherField": "value"}
        ]
    }
    with pytest.raises(AmbError, match="Nenhum patch de código"):
        SessionExtractor.extract_patch(payload)

def test_save_patch(tmp_path):
    dest = tmp_path / "test.patch"
    SessionExtractor.save_patch("mock patch", dest)
    assert dest.exists()
    assert dest.read_text() == "mock patch"

@patch("subprocess.run")
def test_apply_patch_success(mock_run, tmp_path):
    mock_run.return_value = MagicMock(returncode=0)
    success, msg = SessionExtractor.apply_patch("patch content", tmp_path)
    assert success is True
    assert "sucesso" in msg
    mock_run.assert_called_once()

@patch("subprocess.run")
def test_apply_patch_failure(mock_run, tmp_path):
    mock_run.return_value = MagicMock(returncode=1, stderr="error message")
    success, msg = SessionExtractor.apply_patch("patch content", tmp_path)
    assert success is False
    assert "error message" in msg

@patch("integrations.jules.tools.extract_session.JulesClient")
@patch("integrations.jules.tools.extract_session.SessionExtractor.apply_patch")
def test_run_extract_session_cli_apply(mock_apply, mock_client_cls, tmp_path):
    mock_client = MagicMock()
    mock_client_cls.return_value = mock_client
    mock_client.normalize_session_id.return_value = "123"
    mock_client.get_session.return_value = {
        "outputs": [{"changeSet": {"gitPatch": {"unidiffPatch": "patch"}}}]
    }
    mock_apply.return_value = (True, "applied")

    dest = tmp_path / "dest.patch"

    # We pass str(dest) because the CLI will provide strings
    run_extract_session("session/123", dest=str(dest), apply=True)

    mock_client.get_session.assert_called_once_with("123")
    assert dest.exists()
    mock_apply.assert_called_once()
