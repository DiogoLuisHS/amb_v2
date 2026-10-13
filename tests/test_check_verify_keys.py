import pytest
from unittest.mock import patch, MagicMock
import urllib.error
import io

from amb_cli.core.diagnostics import probe_jules_key, probe_gemini_key, run_environment_diagnostics

@pytest.fixture
def mock_env_vars(monkeypatch):
    monkeypatch.setenv("JULES_API_KEY", "jules_test_key_12345")
    monkeypatch.setenv("GEMINI_API_KEY", "gemini_test_key_12345")
    monkeypatch.setenv("STITCH_API_KEY", "stitch_test_key_12345")

class MockHTTPError(urllib.error.HTTPError):
    def __init__(self, code):
        super().__init__("http://test.com", code, "Error", {}, None)

def test_probe_jules_key_success():
    with patch('urllib.request.urlopen') as mock_urlopen:
        mock_urlopen.return_value = MagicMock()
        success, msg = probe_jules_key("test_key")
        assert success is True
        assert msg == "Conexão Verificada"

def test_probe_jules_key_invalid():
    with patch('urllib.request.urlopen') as mock_urlopen:
        mock_urlopen.side_effect = MockHTTPError(401)
        success, msg = probe_jules_key("test_key")
        assert success is False
        assert msg == "Chave inválida ou revogada"

def test_probe_jules_key_timeout():
    with patch('urllib.request.urlopen') as mock_urlopen:
        mock_urlopen.side_effect = Exception("Timeout")
        success, msg = probe_jules_key("test_key")
        assert success is False
        assert "Erro de conexão: Timeout" in msg

def test_probe_gemini_key_success():
    with patch('urllib.request.urlopen') as mock_urlopen:
        mock_urlopen.return_value = MagicMock()
        success, msg = probe_gemini_key("test_key")
        assert success is True
        assert msg == "Conexão Verificada"

def test_probe_gemini_key_invalid():
    with patch('urllib.request.urlopen') as mock_urlopen:
        mock_urlopen.side_effect = MockHTTPError(403)
        success, msg = probe_gemini_key("test_key")
        assert success is False
        assert msg == "Chave inválida ou revogada"

def test_run_diagnostics_without_verify(mock_env_vars):
    with patch('urllib.request.urlopen') as mock_urlopen:
        report = run_environment_diagnostics(as_json=True, verify=False)
        assert not mock_urlopen.called
        assert report["platform_keys"]["JULES_API_KEY"]["configured"] is True
        assert "verified" not in report["platform_keys"]["JULES_API_KEY"]

def test_run_diagnostics_with_verify_success(mock_env_vars):
    with patch('urllib.request.urlopen') as mock_urlopen:
        mock_urlopen.return_value = MagicMock()
        report = run_environment_diagnostics(as_json=True, verify=True)
        assert mock_urlopen.call_count == 2 # 1 for jules, 1 for gemini
        assert report["platform_keys"]["JULES_API_KEY"]["verified"] is True
        assert report["platform_keys"]["GEMINI_API_KEY"]["verified"] is True

def test_run_diagnostics_with_verify_invalid(mock_env_vars, capsys):
    with patch('urllib.request.urlopen') as mock_urlopen:
        mock_urlopen.side_effect = MockHTTPError(401)
        report = run_environment_diagnostics(as_json=False, verify=True)
        assert report["platform_keys"]["JULES_API_KEY"]["verified"] is False
        assert report["platform_keys"]["GEMINI_API_KEY"]["verified"] is False

        captured = capsys.readouterr()
        assert "❌ Google Jules SDK / API         (JULES_API_KEY): \x1b[91mjule...2345 [🚫 Erro: Chave inválida ou revogada]" in captured.out
        assert "❌ Google Antigravity / Gemini    (GEMINI_API_KEY): \x1b[91mgemi...2345 [🚫 Erro: Chave inválida ou revogada]" in captured.out

def test_run_diagnostics_with_verify_timeout(mock_env_vars):
    with patch('urllib.request.urlopen') as mock_urlopen:
        mock_urlopen.side_effect = Exception("Network Timeout")
        report = run_environment_diagnostics(as_json=True, verify=True)
        assert report["platform_keys"]["JULES_API_KEY"]["verified"] is False
        assert "Erro de conexão" in report["platform_keys"]["JULES_API_KEY"]["verify_message"]
