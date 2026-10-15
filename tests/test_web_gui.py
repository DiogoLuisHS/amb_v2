import pytest
import os
import threading
import time
import urllib.request
import urllib.error
from unittest.mock import patch, MagicMock

from amb_cli.gui.web.server import start_web_gui, MockAPIHandler
from amb_cli.cli_modules.cli_parsers import create_parser

def test_web_gui_files_exist():
    base_path = os.path.join(os.path.dirname(__file__), "..", "amb_cli", "gui", "web")
    assert os.path.exists(os.path.join(base_path, "index.html"))
    assert os.path.exists(os.path.join(base_path, "styles.css"))
    assert os.path.exists(os.path.join(base_path, "app.js"))
    assert os.path.exists(os.path.join(base_path, "server.py"))


@patch("amb_cli.gui.web.server.socketserver.TCPServer")
@patch("amb_cli.gui.web.server.webbrowser.open")
def test_start_web_gui_initializes(mock_open, mock_tcpserver):
    # Setup mock
    mock_server_instance = MagicMock()
    mock_tcpserver.return_value = mock_server_instance

    # We need to simulate KeyboardInterrupt to break the serve_forever loop
    mock_server_instance.serve_forever.side_effect = KeyboardInterrupt

    # Execute
    start_web_gui()

    # Assert
    mock_tcpserver.assert_called()
    mock_server_instance.serve_forever.assert_called_once()
    mock_server_instance.server_close.assert_called_once()


def test_cli_gui_web_argument():
    parser = create_parser()
    args = parser.parse_args(["gui", "--web"])
    assert getattr(args, "web") is True

    args = parser.parse_args(["gui", "-w"])
    assert getattr(args, "web") is True

    args = parser.parse_args(["gui"])
    assert getattr(args, "web") is False


def test_mock_api_handler_exec(monkeypatch):
    """Test MockAPIHandler GET route handling"""
    mock_request = MagicMock()
    mock_client_address = ("127.0.0.1", 12345)
    mock_server = MagicMock()

    with patch("socketserver.BaseRequestHandler.__init__") as mock_init:
        mock_init.return_value = None
        handler = MockAPIHandler(mock_request, mock_client_address, mock_server)
        handler.path = "/api/exec?cmd=echo test"
        handler.send_response = MagicMock()
        handler.send_header = MagicMock()
        handler.end_headers = MagicMock()
        handler.wfile = MagicMock()

        handler.do_GET()

        handler.send_response.assert_called_with(200)
        handler.wfile.write.assert_called_once()
        assert b"Mock execution of 'echo test' completed." in handler.wfile.write.call_args[0][0]


def test_mock_api_handler_default(monkeypatch):
    """Test MockAPIHandler GET route default fall through"""
    mock_request = MagicMock()
    mock_client_address = ("127.0.0.1", 12345)
    mock_server = MagicMock()

    with patch("http.server.SimpleHTTPRequestHandler.do_GET") as mock_super_get:
        with patch("socketserver.BaseRequestHandler.__init__") as mock_init:
            mock_init.return_value = None
            handler = MockAPIHandler(mock_request, mock_client_address, mock_server)
            handler.path = "/index.html"

            handler.do_GET()

            mock_super_get.assert_called_once()
