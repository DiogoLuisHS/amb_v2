import os
import argparse
import pytest
from unittest.mock import patch, MagicMock
from amb_cli.cli_modules.handlers_core.jules_handler import handle_cmd_jules
from amb_cli.integrations.jules.tools.create_session import run_create_session

@patch("integrations.jules.tools.create_session.run_create_session")
def test_jules_create_with_positional_prompt(mock_run_create_session):
    """Testa criação passando prompt direto posicional (`amb jules create "texto"`)."""
    args = argparse.Namespace(
        jules_cmd="create",
        prompt_pos="Meu prompt direto",
        prompt=None,
        title=None,
        branch=None,
        source=None,
        json=False,
        no_auto_pr=False,
        require_approval=False,
        no_repo=False,
        skip_branch_check=False
    )
    handle_cmd_jules(args)

    mock_run_create_session.assert_called_once_with(
        prompt="Meu prompt direto",
        title=None,
        base_branch=None,
        source_name=None,
        as_json=False,
        auto_pr=True,
        require_plan_approval=None,
        repoless=False,
        skip_branch_check=False
    )


@patch("integrations.jules.tools.create_session.run_create_session")
def test_jules_create_retrocompatibility_with_prompt_flag(mock_run_create_session):
    """Testa preservação da retrocompatibilidade com `--prompt` / `-p`."""
    args = argparse.Namespace(
        jules_cmd="create",
        prompt_pos=None,
        prompt="Prompt via flag",
        title=None,
        branch=None,
        source=None,
        json=False,
        no_auto_pr=False,
        require_approval=False,
        no_repo=False,
        skip_branch_check=False
    )
    handle_cmd_jules(args)

    mock_run_create_session.assert_called_once_with(
        prompt="Prompt via flag",
        title=None,
        base_branch=None,
        source_name=None,
        as_json=False,
        auto_pr=True,
        require_plan_approval=None,
        repoless=False,
        skip_branch_check=False
    )


@patch("amb_cli.cli_modules.handlers_core.jules_handler.log_error")
@patch("integrations.jules.tools.create_session.run_create_session")
def test_jules_create_graceful_handling_missing_prompt(mock_run_create_session, mock_log_error):
    """Testa tratamento gracioso quando nenhum prompt é fornecido."""
    args = argparse.Namespace(
        jules_cmd="create",
        prompt_pos=None,
        prompt=None,
        title=None,
        branch=None,
        source=None,
        json=False,
        no_auto_pr=False,
        require_approval=False,
        no_repo=False,
        skip_branch_check=False
    )
    handle_cmd_jules(args)

    mock_log_error.assert_called_once_with("JULES", "É necessário fornecer um prompt (posicional ou via -p).")
    mock_run_create_session.assert_not_called()


@patch("amb_cli.integrations.jules.tools.create_session.JulesClient")
def test_jules_create_with_markdown_file_and_auto_title(MockClient, tmp_path):
    """
    Testa criação passando caminho de arquivo `.md` existente com leitura
    automática do conteúdo e auto-inferência de título.
    """
    mock_client = MockClient.return_value
    mock_client.create_session.return_value = {"id": "123", "name": "sessions/123"}

    # Cria o arquivo fake
    md_file = tmp_path / "01_tarefa.md"
    file_content = "# Refatorar Componente X\n\nDetalhes sobre a refatoração..."
    md_file.write_text(file_content, encoding="utf-8")

    # Executa passando o arquivo no parâmetro prompt
    res = run_create_session(
        prompt=str(md_file),
        title=None,  # Título não fornecido, deve inferir
        client=mock_client,
        skip_branch_check=True
    )

    # Deve chamar client.create_session com o prompt contendo o conteúdo
    # e title inferido
    mock_client.create_session.assert_called_once_with(
        prompt=file_content,
        title="Refatorar Componente X",
        source_name=None,
        base_branch=None,
        automation_mode="AUTO_CREATE_PR",
        require_plan_approval=None,
        repoless=False
    )

@patch("amb_cli.integrations.jules.tools.create_session.JulesClient")
def test_jules_create_with_markdown_file_and_explicit_title(MockClient, tmp_path):
    """
    Testa criação passando caminho de arquivo com leitura do conteúdo, mas com
    título explicitamente fornecido.
    """
    mock_client = MockClient.return_value
    mock_client.create_session.return_value = {"id": "123", "name": "sessions/123"}

    md_file = tmp_path / "02_bugfix.md"
    file_content = "Corrige bug no login..."
    md_file.write_text(file_content, encoding="utf-8")

    res = run_create_session(
        prompt=str(md_file),
        title="Meu Título Customizado",
        client=mock_client,
        skip_branch_check=True
    )

    mock_client.create_session.assert_called_once_with(
        prompt=file_content,
        title="Meu Título Customizado",
        source_name=None,
        base_branch=None,
        automation_mode="AUTO_CREATE_PR",
        require_plan_approval=None,
        repoless=False
    )