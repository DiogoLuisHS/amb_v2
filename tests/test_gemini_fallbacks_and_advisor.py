# -*- coding: utf-8 -*-
"""
🧪 Testes de Otimização e Fallbacks do Gemini / Antigravity e Cognitive Advisor
Localização: tests/test_gemini_fallbacks_and_advisor.py
"""

from unittest.mock import MagicMock
import pytest

from core import ApiExecutionError
from integrations.antigravity.antigravity_client import AntigravityClient
from integrations.antigravity.antigravity_core.gemini_backend import (
    GeminiBackend,
    CANONICAL_FALLBACK_MODELS,
)
from agents.auto_reply_core.turn_extractor import TurnHistoryExtractor
from agents.auto_reply_core.cognitive_advisor import CognitiveAdvisor


def test_canonical_fallback_models_without_deprecated():
    """Garante que modelos descontinuados (3.6 e 3.5 legados) não constam nos fallbacks."""
    for m in CANONICAL_FALLBACK_MODELS:
        assert "3.6" not in m, f"Modelo descontinuado 3.6 encontrado: {m}"
        assert "3.5-flash" != m, f"Modelo descontinuado 3.5-flash encontrado: {m}"
    assert "gemini-3.8-flash" in CANONICAL_FALLBACK_MODELS
    assert "gemini-2.5-flash" in CANONICAL_FALLBACK_MODELS


def test_resolve_deprecated_models_upgrade():
    """Valida upgrade automático de modelos descontinuados para o padrão gemini-3.8-flash."""
    assert AntigravityClient._resolve_model("gemini-3.6-flash") == "gemini-3.8-flash"
    assert AntigravityClient._resolve_model("gemini-3.5-flash") == "gemini-3.8-flash"
    assert AntigravityClient._resolve_model("gemini-1.5-flash") == "gemini-3.8-flash"
    # Modelo customizado ou válido deve ser mantido
    assert AntigravityClient._resolve_model("gemini-3.7-flash") == "gemini-3.7-flash"
    assert AntigravityClient._resolve_model("custom-experimental") == "custom-experimental"


def test_gemini_backend_fallback_on_404_discontinued():
    """Valida que erro 404 (modelo não encontrado/descontinuado) avança para o próximo fallback."""
    mock_google = MagicMock()
    # Primeiro modelo (3.8) responde 404 (not found); segundo modelo (3.7) responde sucesso
    calls = []

    def mock_execute(*args, **kwargs):
        model_url = kwargs.get("path_or_url", "")
        calls.append(model_url)
        if "gemini-3.8-flash" in model_url:
            raise ApiExecutionError("HTTP 404: models/gemini-3.8-flash is not found")
        return {
            "candidates": [
                {"content": {"parts": [{"text": "Resposta via modelo de fallback"}]}}
            ]
        }

    mock_google.execute_request.side_effect = mock_execute
    backend = GeminiBackend(api_key="fake-key", google_client=mock_google)

    result = backend._generate_via_gemini_api(
        prompt="Pergunta de teste", model="gemini-3.8-flash"
    )
    assert result == "Resposta via modelo de fallback"
    assert len(calls) == 2
    assert "gemini-3.8-flash" in calls[0]
    assert "gemini-3.7-flash" in calls[1]


def test_gemini_backend_fallback_on_429_quota():
    """Valida failover automático em caso de esgotamento de quota ou rate limit (429)."""
    mock_google = MagicMock()
    calls = []

    def mock_execute(*args, **kwargs):
        model_url = kwargs.get("path_or_url", "")
        calls.append(model_url)
        if "gemini-3.8-flash" in model_url:
            raise ApiExecutionError("HTTP 429: Resource has been exhausted (quota exceeded)")
        return {
            "candidates": [
                {"content": {"parts": [{"text": "Recuperado após 429 via fallback"}]}}
            ]
        }

    mock_google.execute_request.side_effect = mock_execute
    backend = GeminiBackend(api_key="fake-key", google_client=mock_google)

    result = backend._generate_via_gemini_api(
        prompt="Pergunta de teste", model="gemini-3.8-flash"
    )
    assert result == "Recuperado após 429 via fallback"
    assert len(calls) == 2


def test_turn_extractor_bash_compression():
    """Valida que comandos bash antigos são comprimidos e apenas os 3 mais recentes mantêm output."""
    mock_jules = MagicMock()
    mock_jules.get_session.return_value = {"title": "Task", "prompt": "Initial"}
    mock_jules.list_activities.return_value = [
        {"id": "b1", "createTime": "2026-10-15T01:00:00Z", "bashCommand": {"command": "ls -la", "output": "file1\nfile2"}},
        {"id": "b2", "createTime": "2026-10-15T01:01:00Z", "bashCommand": {"command": "cat package.json", "output": "{name: test}"}},
        {"id": "b3", "createTime": "2026-10-15T01:02:00Z", "bashCommand": {"command": "npm test", "output": "PASS 5 tests"}},
        {"id": "b4", "createTime": "2026-10-15T01:03:00Z", "bashCommand": {"command": "git status", "output": "clean working tree"}},
        {"id": "b5", "createTime": "2026-10-15T01:04:00Z", "bashCommand": {"command": "pytest", "output": "100% passed"}},
    ]

    _, _, history, _, _ = TurnHistoryExtractor.get_full_session_history(mock_jules, "s1")

    # b1 e b2 são antigos: devem ser comprimidos como (executado)
    assert "$ ls -la` (executado)" in history
    assert "$ cat package.json` (executado)" in history
    assert "file1" not in history
    assert "{name: test}" not in history

    # b3, b4 e b5 são os 3 mais recentes: devem conter output detalhado
    assert "PASS 5 tests" in history
    assert "clean working tree" in history
    assert "100% passed" in history


def test_cognitive_advisor_completeness_and_rigor():
    """Valida que CognitiveAdvisor prioriza completude técnica (4096 tokens, temp=0.2) e zero ambiguidade."""
    mock_client = MagicMock()
    mock_client.generate_text.return_value = "Plan approved. Proceed to PR."

    advisor = CognitiveAdvisor(antigravity_client=mock_client)
    res = advisor.generate_suggestion(
        session_title="Task Title",
        initial_prompt="Mission",
        full_chat_history="History",
        current_question="Should I create the PR?",
    )

    assert res == "Plan approved. Proceed to PR."
    mock_client.generate_text.assert_called_once()
    call_kwargs = mock_client.generate_text.call_args[1]
    assert call_kwargs["temperature"] == 0.2
    assert call_kwargs["max_output_tokens"] == 4096
    # Valida regra de rigor e ausência de ambiguidades no prompt
    assert "CLAREZA TOTAL E RIGOR TÉCNICO" in call_kwargs["prompt"]
    assert "ZERO AMBIGUIDADE" in call_kwargs["prompt"]
