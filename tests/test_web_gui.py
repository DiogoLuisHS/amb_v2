import os
import pytest
from unittest.mock import patch, MagicMock
from amb_cli.gui.web.server import start_web_server

def test_web_gui_files_exist():
    """Verifica se os arquivos estáticos da interface web existem."""
    base_path = os.path.join(os.path.dirname(__file__), "..", "amb_cli", "gui", "web")
    assert os.path.exists(os.path.join(base_path, "index.html"))
    assert os.path.exists(os.path.join(base_path, "styles.css"))
    assert os.path.exists(os.path.join(base_path, "app.js"))
    assert os.path.exists(os.path.join(base_path, "server.py"))

@patch("amb_cli.gui.web.server.HTTPServer")
@patch("amb_cli.gui.web.server.webbrowser")
@patch("amb_cli.gui.web.server.threading")
def test_start_web_server(mock_threading, mock_webbrowser, mock_http_server):
    """Verifica se o servidor web inicializa corretamente sem bloquear."""
    # Mock do servidor para não travar num loop infinito
    mock_instance = MagicMock()
    mock_http_server.return_value = mock_instance

    # O mock de HTTPServer já resolve. Além disso mockamos serve_forever para retornar logo
    mock_instance.serve_forever.return_value = None

    # Executa a função
    start_web_server(port=8080, open_browser=True)

    # Verifica se HTTPServer foi instanciado
    mock_http_server.assert_called_once()
    mock_instance.serve_forever.assert_called_once()
    mock_threading.Timer.assert_called_once()
