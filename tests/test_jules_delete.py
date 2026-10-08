import pytest
import io
import sys
from unittest.mock import patch, MagicMock

from cli_modules.cli_parsers import create_parser
from cli_modules.handlers_core.jules_handler import handle_cmd_jules

def test_jules_delete_success(capsys):
    parser = create_parser()
    args = parser.parse_args(["jules", "delete", "test_session_123", "--force"])

    with patch("integrations.jules.jules_client.JulesClient") as mock_client_cls:
        mock_client = MagicMock()
        mock_client_cls.return_value = mock_client
        mock_client.delete_session.return_value = {"success": True}

        handle_cmd_jules(args)

        mock_client.delete_session.assert_called_once_with("test_session_123")

        captured = capsys.readouterr()
        assert "Sessão test_session_123 excluída com sucesso" in captured.out


def test_jules_delete_404_not_found(capsys):
    parser = create_parser()
    args = parser.parse_args(["jules", "delete", "test_session_404", "--force"])

    with patch("integrations.jules.jules_client.JulesClient") as mock_client_cls:
        mock_client = MagicMock()
        mock_client_cls.return_value = mock_client
        # Simula erro de sessão já deletada/não encontrada
        mock_client.delete_session.side_effect = Exception("404 NOT_FOUND: Session not found")

        handle_cmd_jules(args)

        mock_client.delete_session.assert_called_once_with("test_session_404")

        captured = capsys.readouterr()
        # Verifica se o tratamento amigável de 404 foi acionado
        assert "Aviso: A sessão test_session_404 já foi excluída ou não existe" in captured.out
        # Deve ter tratado o erro sem imprimir log_error padrão de stack trace com fail
        assert "Erro ao deletar sessão" not in captured.out
