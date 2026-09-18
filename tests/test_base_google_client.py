# -*- coding: utf-8 -*-
"""Unit tests for integrations/common/base_google_client.py."""

import json
import sys
import urllib.error
from io import BytesIO
from pathlib import Path
from unittest.mock import MagicMock, patch

_root = Path(__file__).resolve().parent.parent
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))
from core.bootstrap import ensure_amb_env
ensure_amb_env()

from core import ApiExecutionError
from integrations.common.base_google_client import BaseGoogleClient, mask_sensitive_data


def test_mask_sensitive_data():
    raw = "Key: AIzaSyD3x4mpl3K3y1234567890abcdef123 and url: https://api.google.com?key=AIzaSyD3x4mpl3K3y1234567890abcdef123"
    masked = mask_sensitive_data(raw)
    assert "AIzaSyD3x4mpl3K3y1234567890abcdef123" not in masked
    assert "key=****" in masked
    assert "AIzaSy" in masked  # prefix preserved

    header_test = "X-Goog-Api-Key: secret_key_value_999\nBearer token_secret_xyz"
    masked_header = mask_sensitive_data(header_test)
    assert "secret_key_value_999" not in masked_header
    assert "token_secret_xyz" not in masked_header


def test_backoff_delay_calculation():
    client = BaseGoogleClient(base_delay=1.0, max_delay=10.0)
    delay_1 = client._calculate_backoff_delay(1)
    # 1.0 * [0.8..1.2]
    assert 0.7 <= delay_1 <= 1.3

    delay_3 = client._calculate_backoff_delay(3)
    # 4.0 * [0.8..1.2]
    assert 3.0 <= delay_3 <= 5.0


def test_normalize_error_codes():
    client = BaseGoogleClient(service_name="TEST-API")
    
    # 403 Forbidden
    err_403 = client._normalize_error(Exception("Auth error"), status_code=403, error_body='{"error": {"message": "Invalid key"}}')
    assert isinstance(err_403, ApiExecutionError)
    assert "HTTP 403" in str(err_403)
    assert "Invalid key" in str(err_403)
    assert "permissões ativas" in err_403.hint

    # 429 Rate limit
    err_429 = client._normalize_error(Exception("Rate limit"), status_code=429, error_body="Quota exceeded")
    assert "Rate Limit" in err_429.hint


def test_execute_request_success():
    client = BaseGoogleClient(base_url="https://fake.googleapis.com", api_key="test-key")
    
    mock_response = MagicMock()
    mock_response.read.return_value = json.dumps({"status": "ok", "items": [1, 2]}).encode("utf-8")
    mock_response.__enter__.return_value = mock_response
    mock_response.__exit__.return_value = False

    with patch("urllib.request.urlopen", return_value=mock_response):
        res = client.execute_request("GET", "endpoint", params={"q": "search"})
        assert res == {"status": "ok", "items": [1, 2]}


def test_execute_request_retry_on_503_then_success():
    client = BaseGoogleClient(base_url="https://fake.googleapis.com", max_retries=3, base_delay=0.01)

    http_err_503 = urllib.error.HTTPError(
        url="https://fake.googleapis.com",
        code=503,
        msg="Unavailable",
        hdrs={},
        fp=BytesIO(b'{"error": "temporarily unavailable"}')
    )

    mock_ok_response = MagicMock()
    mock_ok_response.read.return_value = json.dumps({"result": "recovered"}).encode("utf-8")
    mock_ok_response.__enter__.return_value = mock_ok_response
    mock_ok_response.__exit__.return_value = False

    # Falha na 1ª tentativa com 503, tem sucesso na 2ª tentativa
    with patch("urllib.request.urlopen", side_effect=[http_err_503, mock_ok_response]), \
         patch("time.sleep") as mock_sleep:
        res = client.execute_request("POST", "action", data={"foo": "bar"})
        assert res == {"result": "recovered"}
        assert mock_sleep.called
