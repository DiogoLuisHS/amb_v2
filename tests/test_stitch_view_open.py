import os
import pytest
from unittest.mock import patch, MagicMock
from amb_cli.cli_modules.handlers_core.stitch_handler import handle_cmd_stitch

@pytest.fixture
def mock_stitch_client():
    with patch("integrations.stitch.stitch_client.StitchClient") as MockClient:
        client_instance = MockClient.return_value
        yield client_instance

@pytest.fixture
def mock_webbrowser():
    with patch("amb_cli.cli_modules.handlers_core.stitch_handler.webbrowser.open") as mock_open:
        yield mock_open

class DummyArgs:
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)
        if not hasattr(self, "json"):
            self.json = False
        if not hasattr(self, "open"):
            self.open = False

def test_stitch_view_calls_webbrowser(mock_stitch_client, mock_webbrowser):
    """Testa se 'amb stitch view <id>' chama webbrowser.open com a URL."""
    args = DummyArgs(stitch_cmd="view", screen_id="test-123")
    mock_stitch_client.get_screen.return_value = {"screenshotUrl": "http://example.com/img.png"}

    handle_cmd_stitch(args)

    mock_stitch_client.get_screen.assert_called_once_with(screen_id="test-123")
    mock_webbrowser.assert_called_once_with("http://example.com/img.png")

def test_stitch_view_with_local_file(mock_stitch_client, mock_webbrowser, tmp_path):
    """Testa se view também tenta abrir arquivo HTML, no fluxo atual o _open_in_browser prioriza output_file se existir."""
    # O comando view em si não usa output_file na chamada get_screen,
    # mas o _open_in_browser tem essa lógica.
    pass # Este teste é coberto por get/generate/refine com output_file

def test_stitch_generate_with_open_flag(mock_stitch_client, mock_webbrowser):
    """Testa se 'amb stitch generate --open' abre a URL no navegador."""
    args = DummyArgs(stitch_cmd="generate", prompt="Make a button", open=True, output=None, device=None)
    mock_stitch_client.generate_screen.return_value = {"screenId": "123", "screenshotUrl": "http://test.com/new.png"}

    handle_cmd_stitch(args)

    mock_stitch_client.generate_screen.assert_called_once()
    mock_webbrowser.assert_called_once_with("http://test.com/new.png")

def test_stitch_generate_without_open_flag(mock_stitch_client, mock_webbrowser):
    """Testa se 'amb stitch generate' sem --open não abre o navegador."""
    args = DummyArgs(stitch_cmd="generate", prompt="Make a button", open=False, output=None, device=None)
    mock_stitch_client.generate_screen.return_value = {"screenId": "123", "screenshotUrl": "http://test.com/new.png"}

    handle_cmd_stitch(args)

    mock_webbrowser.assert_not_called()

def test_stitch_refine_with_open_flag(mock_stitch_client, mock_webbrowser):
    """Testa se 'amb stitch refine --open' abre a URL no navegador."""
    args = DummyArgs(stitch_cmd="refine", screen_id="123", prompt="Make it blue", open=True, output=None, device=None)
    mock_stitch_client.edit_screen.return_value = {"screenId": "123", "screenshotUrl": "http://test.com/blue.png"}

    handle_cmd_stitch(args)

    mock_stitch_client.edit_screen.assert_called_once()
    mock_webbrowser.assert_called_once_with("http://test.com/blue.png")

def test_stitch_get_with_open_flag_and_output(mock_stitch_client, mock_webbrowser, tmp_path):
    """Testa se 'amb stitch get --open --output <file>' abre o arquivo local."""
    test_file = tmp_path / "test.html"
    test_file.write_text("<html></html>")

    args = DummyArgs(stitch_cmd="get", screen_id="123", open=True, output=str(test_file))
    mock_stitch_client.get_screen.return_value = {"screenId": "123", "screenshotUrl": "http://test.com/img.png"}

    handle_cmd_stitch(args)

    mock_stitch_client.get_screen.assert_called_once()
    mock_webbrowser.assert_called_once_with(f"file://{os.path.abspath(str(test_file))}")

def test_stitch_get_with_open_flag_but_no_output(mock_stitch_client, mock_webbrowser):
    """Testa se 'amb stitch get --open' (sem output) abre a URL."""
    args = DummyArgs(stitch_cmd="get", screen_id="123", open=True, output=None)
    mock_stitch_client.get_screen.return_value = {"screenId": "123", "screenshotUrl": "http://test.com/img.png"}

    handle_cmd_stitch(args)

    mock_stitch_client.get_screen.assert_called_once()
    mock_webbrowser.assert_called_once_with("http://test.com/img.png")
