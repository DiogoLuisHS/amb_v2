import pytest
import os
import urllib.request
import urllib.error
import threading
import time
from pathlib import Path
from amb_cli.gui.web.server import start_web_gui, get_free_port

def test_web_gui_static_files():
    """Garante que os arquivos estáticos necessários para o web GUI existem e não estão vazios."""
    web_dir = Path(__file__).parent.parent / "amb_cli" / "gui" / "web"

    assert (web_dir / "index.html").exists()
    assert (web_dir / "index.html").stat().st_size > 0

    assert (web_dir / "styles.css").exists()
    assert (web_dir / "styles.css").stat().st_size > 0

    assert (web_dir / "app.js").exists()
    assert (web_dir / "app.js").stat().st_size > 0

    assert (web_dir / "server.py").exists()

def test_web_gui_server_headless():
    """Testa a inicialização do servidor em uma porta local de forma headless,
    fazendo uma requisição GET para index.html para verificar o conteúdo."""
    port = get_free_port(9000)

    def run_server():
        try:
            start_web_gui(headless=True, port=port, run_forever=False)
        except Exception:
            pass

    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()

    # Dá um pequeno tempo para o servidor iniciar e estar pronto para receber requests
    time.sleep(0.5)

    response = urllib.request.urlopen(f"http://localhost:{port}/index.html", timeout=2)
    html_content = response.read().decode('utf-8')
    assert response.status == 200
    assert "AMB_V2 Web Console" in html_content

    # Wait for the single-request server thread to close
    server_thread.join(timeout=1)

def test_web_gui_cli_flag_integration(monkeypatch):
    """Garante que o argumento da CLI repassa para o handler web."""
    import amb_cli.cli_modules.cli_handlers as cli_handlers
    import sys
    sys.path.insert(0, str(Path(__file__).parent.parent / "amb_cli"))

    class DummyArgs:
        web = True

    web_called = False

    def mock_start_web_gui(*args, **kwargs):
        nonlocal web_called
        web_called = True

    # Mock at the expected sys.path root inside the handler
    from unittest.mock import patch
    with patch('gui.web.server.start_web_gui', mock_start_web_gui):
        cli_handlers.cmd_gui(DummyArgs())

    assert web_called, "start_web_gui deveria ter sido chamado quando --web é passado."

def test_web_gui_api_exec():
    """Garante que a rota /api/exec responde com JSON estruturado."""
    port = get_free_port(9100)

    def run_server():
        try:
            start_web_gui(headless=True, port=port, run_forever=False)
        except Exception:
            pass

    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()
    time.sleep(0.5)

    response = urllib.request.urlopen(f"http://localhost:{port}/api/exec?cmd=amb%20check", timeout=2)
    assert response.status == 200
    data = response.read().decode('utf-8')
    assert "Mock execution of 'amb check' completed." in data
    server_thread.join(timeout=1)
