import os
import tempfile
from unittest.mock import patch, MagicMock

import pytest

from amb_cli.cli_modules.handlers_core.hooks_handler import handle_cmd_hooks


@pytest.fixture
def mock_repo_root():
    """Cria um diretório temporário para simular a raiz do repositório com uma pasta .git."""
    with tempfile.TemporaryDirectory() as temp_dir:
        git_dir = os.path.join(temp_dir, ".git")
        os.makedirs(git_dir)
        yield temp_dir


def test_hooks_install_creates_file_and_permissions(mock_repo_root):
    """Verifica se 'amb git hooks install' gera o arquivo pre-commit com as permissões corretas."""
    args = MagicMock()
    args.hooks_action = "install"
    args.hooks_cmd = None

    with patch("amb_cli.cli_modules.handlers_core.hooks_handler.find_repo_root", return_value=mock_repo_root):
        handle_cmd_hooks(args)

    pre_commit_path = os.path.join(mock_repo_root, ".git", "hooks", "pre-commit")
    assert os.path.exists(pre_commit_path), "Hook pre-commit não foi criado."

    with open(pre_commit_path, "r") as f:
        content = f.read()
    assert "amb_cli.cli validate --staged" in content, "Conteúdo do hook está incorreto."

    if os.name != "nt":
        assert os.access(pre_commit_path, os.X_OK), "Hook não tem permissão de execução."


def test_hooks_status_detects_installed(mock_repo_root, capsys):
    """Verifica se 'amb git hooks status' detecta o hook instalado corretamente."""
    # Instala primeiro
    args_install = MagicMock()
    args_install.hooks_action = "install"
    args_install.hooks_cmd = None

    with patch("amb_cli.cli_modules.handlers_core.hooks_handler.find_repo_root", return_value=mock_repo_root):
        handle_cmd_hooks(args_install)

    # Verifica status
    args_status = MagicMock()
    args_status.hooks_action = "status"
    args_status.hooks_cmd = None

    with patch("amb_cli.cli_modules.handlers_core.hooks_handler.find_repo_root", return_value=mock_repo_root):
        handle_cmd_hooks(args_status)

    captured = capsys.readouterr()
    assert "Hook pre-commit: Ativo e configurado" in captured.out


def test_hooks_status_detects_missing(mock_repo_root, capsys):
    """Verifica se 'amb git hooks status' detecta a ausência do hook."""
    args = MagicMock()
    args.hooks_action = "status"
    args.hooks_cmd = None

    with patch("amb_cli.cli_modules.handlers_core.hooks_handler.find_repo_root", return_value=mock_repo_root):
        handle_cmd_hooks(args)

    captured = capsys.readouterr()
    assert "Hook pre-commit: Não instalado" in captured.out


def test_root_hooks_shortcut_delegation(mock_repo_root):
    """Verifica se 'amb hooks install' também delega corretamente para a instalação."""
    args = MagicMock()
    # Para o atalho na raiz, hooks_cmd é usado ao invés de hooks_action
    args.hooks_cmd = "install"
    args.hooks_action = None

    with patch("amb_cli.cli_modules.handlers_core.hooks_handler.find_repo_root", return_value=mock_repo_root):
        handle_cmd_hooks(args)

    pre_commit_path = os.path.join(mock_repo_root, ".git", "hooks", "pre-commit")
    assert os.path.exists(pre_commit_path), "Hook pre-commit não foi criado via atalho raiz."
