# -*- coding: utf-8 -*-
"""Unit tests for error enrichment in integrations/common/base_google_client.py."""

import json
import sys
from pathlib import Path
from unittest.mock import MagicMock

_root = Path(__file__).resolve().parent.parent
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))
from core.bootstrap import ensure_amb_env
ensure_amb_env()

from core import ApiExecutionError
from integrations.common.base_google_client import BaseGoogleClient


def test_normalize_error_with_status_canonical():
    """Testa erro HTTP com payload JSON contendo code, message e status."""
    client = BaseGoogleClient(service_name="TEST-API")
    error_body = json.dumps({
        "error": {
            "code": 400,
            "message": "Invalid session ID format",
            "status": "INVALID_ARGUMENT"
        }
    })

    err = client._normalize_error(Exception("Bad request"), status_code=400, error_body=error_body)

    assert isinstance(err, ApiExecutionError)
    err_str = str(err)
    assert "HTTP 400" in err_str
    assert "[INVALID_ARGUMENT]" in err_str
    assert "na API TEST-API" in err_str
    assert "Invalid session ID format" in err_str
    assert "Requisição malformada" in err.hint


def test_normalize_error_without_status_canonical():
    """Testa erro HTTP com payload JSON contendo apenas message (sem status), verificando retrocompatibilidade."""
    client = BaseGoogleClient(service_name="TEST-API")
    error_body = json.dumps({
        "error": {
            "code": 404,
            "message": "Resource not found"
        }
    })

    err = client._normalize_error(Exception("Not found"), status_code=404, error_body=error_body)

    assert isinstance(err, ApiExecutionError)
    err_str = str(err)
    assert "HTTP 404" in err_str
    assert "[" not in err_str
    assert "]" not in err_str
    assert "na API TEST-API" in err_str
    assert "Resource not found" in err_str
    assert "Recurso não encontrado" in err.hint


def test_normalize_error_with_non_json_body():
    """Testa erro HTTP com corpo não JSON (texto puro ou vazio)."""
    client = BaseGoogleClient(service_name="TEST-API")
    error_body = "Internal Server Error Occurred"

    err = client._normalize_error(Exception("Server error"), status_code=500, error_body=error_body)

    assert isinstance(err, ApiExecutionError)
    err_str = str(err)
    assert "HTTP 500" in err_str
    assert "[" not in err_str
    assert "]" not in err_str
    assert "na API TEST-API" in err_str
    assert "Internal Server Error Occurred" in err_str
    assert "Instabilidade temporária nos servidores do Google" in err.hint


def test_normalize_error_with_empty_body():
    """Testa erro HTTP com corpo vazio."""
    client = BaseGoogleClient(service_name="TEST-API")

    err = client._normalize_error(Exception("Empty error"), status_code=429, error_body="")

    assert isinstance(err, ApiExecutionError)
    err_str = str(err)
    assert "HTTP 429 na API TEST-API" in err_str
    assert "Limite de quota excedido (Rate Limit)" in err.hint
