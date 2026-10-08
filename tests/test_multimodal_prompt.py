# -*- coding: utf-8 -*-
"""Unit tests for multimodal prompt synthesis with visual mockups (US-10)."""

import base64
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

_root = Path(__file__).resolve().parent.parent
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))
from core.bootstrap import ensure_amb_env
ensure_amb_env()

import pytest
import argparse
from integrations.antigravity.antigravity_core.gemini_backend import GeminiBackend
from integrations.antigravity.antigravity_client import AntigravityClient, synthesize_prompt
from integrations.antigravity.tools.synthesize_prompt import run_synthesize_prompt
from cli_modules.cli_handlers import cmd_prompt


@pytest.fixture
def sample_image(tmp_path):
    img = tmp_path / "mockup.png"
    img.write_bytes(b"\x89PNG\r\n\x1a\nfake_image_content")
    return str(img)


def test_gemini_backend_multimodal_payload(sample_image):
    mock_google = MagicMock()
    mock_google.execute_request.return_value = {
        "candidates": [{"content": {"parts": [{"text": "UI spec generated"}]}}]
    }
    backend = GeminiBackend(api_key="test_key", google_client=mock_google)
    res = backend._generate_via_gemini_api(
        prompt="Design this UI",
        model="gemini-3.8-flash",
        image_path=sample_image,
    )
    assert res == "UI spec generated"
    mock_google.execute_request.assert_called_once()
    payload = mock_google.execute_request.call_args.kwargs["data"]
    parts = payload["contents"][0]["parts"]

    assert len(parts) == 2
    assert parts[0]["text"] == "Design this UI"
    assert "inlineData" in parts[1]
    assert parts[1]["inlineData"]["mimeType"] == "image/png"
    assert parts[1]["inlineData"]["data"] == base64.b64encode(b"\x89PNG\r\n\x1a\nfake_image_content").decode("utf-8")


def test_antigravity_client_synthesize_with_image(sample_image):
    client = AntigravityClient()
    with patch.object(client, "generate_text", return_value="# Spec de UI") as mock_gen:
        res = client.synthesize_prompt(
            raw_idea="Criar formulário de checkout",
            role="frontend",
            image_path=sample_image
        )
        assert res == "# Spec de UI"
        mock_gen.assert_called_once()
        prompt_arg = mock_gen.call_args.kwargs["prompt"]
        sys_arg = mock_gen.call_args.kwargs["system_instruction"]
        assert sample_image in prompt_arg
        assert "Especialista em UI/UX do Google Jules" in sys_arg


def test_synthesize_prompt_fallback_template_with_image(sample_image):
    client = AntigravityClient()
    with patch.object(client, "generate_text", side_effect=Exception("API indisponível")):
        res = client.synthesize_prompt(
            raw_idea="Tela de Configurações",
            image_path=sample_image
        )
        assert "# 🎯 ESCOPO TÉCNICO EXECUTIVO" in res
        assert "## 🖼️ Referência Visual" in res
        assert sample_image in res


def test_run_synthesize_prompt_tool_with_image(sample_image, tmp_path):
    out_file = tmp_path / "output_prompt.md"
    with patch("integrations.antigravity.tools.synthesize_prompt.synthesize_prompt", return_value="# Prompt Salvo"):
        res = run_synthesize_prompt(
            raw_idea="Header responsivo",
            role="ui",
            output_file=str(out_file),
            image_path=sample_image
        )
        assert res == "# Prompt Salvo"
        assert out_file.exists()
        assert out_file.read_text(encoding="utf-8") == "# Prompt Salvo"


def test_cmd_prompt_with_image(sample_image):
    args = argparse.Namespace(
        synthesize="Criar tela de login",
        image=sample_image,
        role="engineer",
        output=None
    )
    with patch("integrations.antigravity.tools.synthesize_prompt.run_synthesize_prompt", return_value="UI Spec") as mock_tool:
        cmd_prompt(args)
        mock_tool.assert_called_once_with(
            raw_idea="Criar tela de login",
            role="engineer",
            output_file=None,
            image_path=sample_image
        )
