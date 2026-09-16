#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🧪 Testes da Integração Google Antigravity & RulesManager (AMB_V2)
Localização: amb_v2/tests/test_antigravity_integration.py
"""

import os
import sys
import json
import tempfile
from unittest.mock import MagicMock, patch

import pytest

from config.rules_manager import RulesManager, get_rules_manager
from integrations.antigravity.antigravity_client import (
    AntigravityClient,
    synthesize_prompt,
    validate_code,
)
from integrations.antigravity.tools.synthesize_prompt import run_synthesize_prompt
from integrations.antigravity.tools.validate_architecture import run_validate_architecture
from cli_modules.cli_handlers import cmd_antigravity


# ---------------------------------------------------------------------------
# 1. Testes do RulesManager (F1-M6)
# ---------------------------------------------------------------------------

def test_rules_manager_clean_markdown_snippet_fences():
    """Valida fechamento seguro de fences markdown e sanitização."""
    text_with_frontmatter = """---
name: sample-rule
description: metadata
---
<!-- Comentário HTML ignorado -->
# Regra Principal
Aqui está um trecho de código:
```python
def foo():
    return 42
"""
    # Truncando no meio do bloco de código
    cleaned = RulesManager.clean_markdown_snippet(text_with_frontmatter, max_chars=80)
    # Deve remover frontmatter, comentários e fechar a fence aberta ```
    assert "---" not in cleaned
    assert "Comentário HTML" not in cleaned
    assert cleaned.count("```") % 2 == 0
    assert cleaned.endswith("```\n... [regras truncadas para concisão]")


def test_rules_manager_resolve_dir_hierarchy():
    """Valida hierarquia de descoberta de diretórios de regras."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Cria .gemini/rules e .antigravity/rules
        gemini_rules = os.path.join(tmpdir, ".gemini", "rules")
        antigravity_rules = os.path.join(tmpdir, ".antigravity", "rules")
        os.makedirs(gemini_rules, exist_ok=True)
        os.makedirs(antigravity_rules, exist_ok=True)

        mgr = RulesManager()
        # .antigravity/rules tem precedência sobre .gemini/rules
        resolved = mgr.resolve_rules_dir(root=tmpdir)
        assert resolved == os.path.abspath(antigravity_rules)

        # Se .antigravity/rules for removido, resolve .gemini/rules
        os.rmdir(antigravity_rules)
        resolved_fallback = mgr.resolve_rules_dir(root=tmpdir)
        assert resolved_fallback == os.path.abspath(gemini_rules)


def test_rules_manager_cache_and_invalidation():
    """Valida que load_rules aplica cache em memória e invalidate_cache limpa."""
    with tempfile.TemporaryDirectory() as tmpdir:
        rules_dir = os.path.join(tmpdir, "rules")
        os.makedirs(rules_dir, exist_ok=True)
        rule_file = os.path.join(rules_dir, "rule1.md")
        with open(rule_file, "w", encoding="utf-8") as f:
            f.write("# Regra Inicial\nManter SRP sempre.")

        mgr = RulesManager(custom_rules_dir=rules_dir)
        mgr.invalidate_cache()

        loaded1 = mgr.load_rules(rules_dir=rules_dir)
        assert "Regra Inicial" in loaded1

        # Modifica o arquivo no disco sem invalidar o cache
        with open(rule_file, "w", encoding="utf-8") as f:
            f.write("# Regra Modificada\nNova diretriz.")

        loaded2 = mgr.load_rules(rules_dir=rules_dir)
        # Deve retornar o valor do cache
        assert "Regra Inicial" in loaded2

        # Invalida o cache e lê novamente
        mgr.invalidate_cache()
        loaded3 = mgr.load_rules(rules_dir=rules_dir)
        assert "Regra Modificada" in loaded3


def test_rules_manager_filter_for_agent():
    """Valida ordenação contextual de regras baseada no papel do agente."""
    mgr = RulesManager()
    sample = """### 📋 Regra: frontend.md
Diretrizes de componentes visuais e acessibilidade.

### 📋 Regra: backend.md
Diretrizes de APIs REST, banco de dados e transações."""

    filtered_front = mgr.filter_rules_for_agent(rules_text=sample, role="frontend")
    # A regra de frontend deve vir antes
    idx_front = filtered_front.find("frontend.md")
    idx_back = filtered_front.find("backend.md")
    assert idx_front < idx_back


# ---------------------------------------------------------------------------
# 2. Testes do AntigravityClient & Model Resolution
# ---------------------------------------------------------------------------

def test_antigravity_client_model_resolution(monkeypatch):
    """Valida hierarquia dinâmica de resolução do modelo cognitivo."""
    # 1. Modelo explícito no construtor
    c1 = AntigravityClient(model="custom-gemini-test")
    assert c1.model == "custom-gemini-test"

    # 2. Variável de ambiente ANTIGRAVITY_MODEL
    monkeypatch.setenv("ANTIGRAVITY_MODEL", "gemini-3.7-flash")
    c2 = AntigravityClient()
    assert c2.model == "gemini-3.7-flash"
    monkeypatch.delenv("ANTIGRAVITY_MODEL", raising=False)

    # 3. Fallback padrão seguro
    c3 = AntigravityClient()
    assert c3.model == "gemini-3.8-flash"


def test_antigravity_client_get_status(monkeypatch):
    """Valida o dicionário estruturado retornado por get_status()."""
    monkeypatch.setenv("GEMINI_API_KEY", "test-api-key-123")
    client = AntigravityClient()
    st = client.get_status()
    assert st["status"] == "OK"
    assert st["gemini_api_key_configured"] is True
    assert "model" in st
    assert "rules_directory" in st
    assert "rules_count" in st
    assert isinstance(st["rules"], list)


def test_antigravity_client_generate_via_api_success(monkeypatch):
    """Valida chamada REST bem sucedida com BaseGoogleClient."""
    client = AntigravityClient(model="gemini-3.8-flash")
    client.api_key = "dummy-key"

    fake_resp = {
        "candidates": [
            {
                "content": {
                    "parts": [{"text": "Resposta gerada com sucesso pelo Gemini"}]
                }
            }
        ]
    }

    mock_execute = MagicMock(returncode=200, return_value=fake_resp)
    monkeypatch.setattr(client.google_client, "execute_request", mock_execute)

    res = client.generate_text("Olá Gemini", system_instruction="Você é um assistente")
    assert res == "Resposta gerada com sucesso pelo Gemini"
    assert mock_execute.call_count == 1
    call_kwargs = mock_execute.call_args[1]
    assert call_kwargs["method"] == "POST"
    assert "gemini-3.8-flash" in call_kwargs["path_or_url"]
    assert call_kwargs["data"]["contents"][0]["parts"][0]["text"] == "Olá Gemini"


def test_antigravity_client_generate_fallback_to_agy_cli(monkeypatch):
    """Valida fallback para o CLI agy quando a API REST falha."""
    client = AntigravityClient()
    client.api_key = "dummy-key"

    # Simula erro na chamada REST
    monkeypatch.setattr(client.google_client, "execute_request", MagicMock(side_effect=Exception("REST Timeout")))
    # Simula presença do CLI agy
    monkeypatch.setattr("shutil.which", lambda cmd: "/usr/bin/agy" if cmd == "agy" else None)

    mock_sub = MagicMock(returncode=0, stdout="Resposta gerada via CLI agy\n", stderr="")
    monkeypatch.setattr("subprocess.run", lambda *args, **kwargs: mock_sub)

    res = client.generate_text("Prompt de teste")
    assert res == "Resposta gerada via CLI agy"


def test_antigravity_client_synthesize_prompt_zero_a_priori(monkeypatch):
    """Valida que synthesize_prompt não contém pressupostos de linguagem/design a priori."""
    client = AntigravityClient()
    captured_prompt = {}

    def mock_generate(prompt, system_instruction=None, **kwargs):
        captured_prompt["prompt"] = prompt
        captured_prompt["system"] = system_instruction
        return "# 🎯 ESCOPO TÉCNICO\nCritérios aprovados."

    monkeypatch.setattr(client, "generate_text", mock_generate)

    res = client.synthesize_prompt(
        raw_idea="Criar endpoint de processamento de pagamentos em Go",
        role="backend"
    )
    assert "ESCOPO TÉCNICO" in res
    assert "Criar endpoint de processamento de pagamentos em Go" in captured_prompt["prompt"]
    # Não deve ter TypeScript hardcoded no prompt se a ideia é Go
    assert "TypeScript estrito" not in captured_prompt["prompt"]


def test_antigravity_client_validate_code_polyglot(monkeypatch):
    """Valida auditoria poliglota detectando linguagem pelo arquivo."""
    client = AntigravityClient()
    captured_call = {}

    def mock_generate(prompt, system_instruction=None, **kwargs):
        captured_call["prompt"] = prompt
        captured_call["system"] = system_instruction
        return "1. Conformidade Geral: Conforme\n2. Nenhum problema identificado."

    monkeypatch.setattr(client, "generate_text", mock_generate)

    with tempfile.NamedTemporaryFile(suffix=".go", mode="w", delete=False) as f:
        f.write("package main\n\nfunc ProcessPayment() bool { return true }\n")
        tmp_go = f.name

    try:
        res = client.validate_code(file_path=tmp_go)
        assert "Conforme" in res
        assert "Go" in captured_call["system"]
        assert "TypeScript" not in captured_call["system"]
    finally:
        if os.path.exists(tmp_go):
            os.remove(tmp_go)


# ---------------------------------------------------------------------------
# 3. Testes das Fachadas e CLI
# ---------------------------------------------------------------------------

def test_antigravity_facade_tools_callable(monkeypatch):
    """Valida funções de serviço run_synthesize_prompt e run_validate_architecture."""
    monkeypatch.setattr(
        "integrations.antigravity.antigravity_client.AntigravityClient.synthesize_prompt",
        lambda self, raw_idea, role, **kwargs: f"Sintetizado: {raw_idea} ({role})"
    )

    with tempfile.TemporaryDirectory() as tmpdir:
        out_file = os.path.join(tmpdir, "prompt.md")
        res = run_synthesize_prompt(raw_idea="Minha ideia", role="engineer", output_file=out_file)
        assert "Sintetizado: Minha ideia" in res
        assert os.path.exists(out_file)
        with open(out_file, "r", encoding="utf-8") as f:
            assert f.read() == res

    monkeypatch.setattr(
        "integrations.antigravity.antigravity_client.AntigravityClient.validate_code",
        lambda self, file_path, **kwargs: "Código auditado com sucesso"
    )
    val_res = run_validate_architecture("some_file.py")
    assert val_res == "Código auditado com sucesso"


def test_antigravity_cli_handlers(capsys, monkeypatch):
    """Valida execução dos subcomandos de amb agy via cmd_antigravity."""
    # 1. amb agy status --json
    args_status = MagicMock(agy_cmd="status", json=True)
    cmd_antigravity(args_status)
    out_st = capsys.readouterr().out
    data_st = json.loads(out_st)
    assert "status" in data_st
    assert "model" in data_st

    # 2. amb agy rules --json
    args_rules = MagicMock(agy_cmd="rules", json=True, content=False)
    cmd_antigravity(args_rules)
    out_rl = capsys.readouterr().out
    data_rl = json.loads(out_rl)
    assert "rules" in data_rl
