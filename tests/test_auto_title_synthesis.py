import os
import pytest
from unittest.mock import patch, MagicMock

from amb_cli.integrations.jules.jules_core.title_synthesizer import synthesize_session_title
from amb_cli.integrations.jules.tools.create_session import run_create_session

def test_synthesize_from_short_string():
    prompt = "Criar nova funcionalidade de login"
    title = synthesize_session_title(prompt)
    assert title == "Criar nova funcionalidade de login"

def test_synthesize_from_long_string_truncates():
    prompt = "Esta é uma string muito longa que excede o limite de sessenta caracteres e portanto deverá ser truncada corretamente"
    title = synthesize_session_title(prompt, max_chars=60)
    assert len(title) == 60
    assert title.endswith("...")
    assert title == "Esta é uma string muito longa que excede o limite de sess..."

def test_synthesize_cleans_markdown():
    prompt = "#   Minha Tarefa \nConteúdo extra"
    title = synthesize_session_title(prompt)
    assert title == "Minha Tarefa"

    prompt2 = "   - *   >  Limpeza de caracteres "
    title2 = synthesize_session_title(prompt2)
    assert title2 == "Limpeza de caracteres"

def test_synthesize_empty_string_fallback():
    assert synthesize_session_title("") == "Sessão AMB_V2"
    assert synthesize_session_title("   ") == "Sessão AMB_V2"
    assert synthesize_session_title(None) == "Sessão AMB_V2"

def test_synthesize_from_markdown_file_with_header(tmp_path):
    md_file = tmp_path / "task.md"
    md_file.write_text("# Título do Arquivo\n\nDetalhes da tarefa", encoding="utf-8")
    title = synthesize_session_title(str(md_file))
    assert title == "Título do Arquivo"

def test_synthesize_from_markdown_file_with_plain_text(tmp_path):
    md_file = tmp_path / "task.md"
    md_file.write_text("\n\n   Apenas texto direto sem markdown\n", encoding="utf-8")
    title = synthesize_session_title(str(md_file))
    assert title == "Apenas texto direto sem markdown"

def test_synthesize_from_markdown_file_fallback_to_filename(tmp_path):
    # Arquivo vazio
    md_file = tmp_path / "16_us16_jules_create_approval.md"
    md_file.write_text("", encoding="utf-8")
    title = synthesize_session_title(str(md_file))
    assert title == "16 us16 jules create approval"

@patch("amb_cli.integrations.jules.tools.create_session.JulesClient")
def test_create_session_with_title_none(MockClient):
    mock_client = MockClient.return_value
    mock_client.create_session.return_value = {"id": "123", "name": "sessions/123"}

    prompt = "# Criar testes unitários\nDetalhes"

    # Chama sem título (title=None)
    res = run_create_session(prompt=prompt, title=None, client=mock_client)

    # Verifica se o synthesize_session_title foi aplicado corretamente e enviado ao create_session do client
    mock_client.create_session.assert_called_once_with(
        prompt=prompt,
        title="Criar testes unitários",
        source_name=None,
        base_branch=None,
        automation_mode="AUTO_CREATE_PR",
        require_plan_approval=None
    )
    assert res == {"id": "123", "name": "sessions/123"}

@patch("amb_cli.integrations.jules.tools.create_session.JulesClient")
def test_create_session_with_explicit_title(MockClient):
    mock_client = MockClient.return_value
    mock_client.create_session.return_value = {"id": "123", "name": "sessions/123"}

    prompt = "# Criar testes unitários\nDetalhes"

    # Chama com título explícito (title="Título Manual")
    res = run_create_session(prompt=prompt, title="Título Manual", client=mock_client)

    # Verifica se o synthesize_session_title NÃO substituiu o título manual
    mock_client.create_session.assert_called_once_with(
        prompt=prompt,
        title="Título Manual",
        source_name=None,
        base_branch=None,
        automation_mode="AUTO_CREATE_PR",
        require_plan_approval=None
    )
    assert res == {"id": "123", "name": "sessions/123"}
