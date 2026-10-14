import pytest
from unittest.mock import patch, MagicMock
from amb_cli.integrations.antigravity.antigravity_client import AntigravityClient

@patch("amb_cli.integrations.antigravity.antigravity_core.gemini_backend.BaseGoogleClient.execute_request")
def test_stream_yielding(mock_execute_request):
    mock_execute_request.return_value = iter([
        'data: {"candidates": [{"content": {"parts": [{"text": "Hello "}]}}]}\n',
        '\n',
        'data: {"candidates": [{"content": {"parts": [{"text": "world!"}]}}]}\n'
    ])

    with patch("amb_cli.integrations.antigravity.antigravity_core.gemini_backend.require_env") as mock_req:
        client = AntigravityClient()
        client.api_key = "FAKE_KEY"
        client.backend.api_key = "FAKE_KEY"

        chunks = list(client.generate_text_stream("Say hello"))
        assert chunks == ["Hello ", "world!"]

@patch("sys.stdout")
def test_cli_stream_stdout(mock_stdout):
    from amb_cli.cli_modules.handlers_core.antigravity_handler import handle_cmd_antigravity

    with patch("integrations.antigravity.antigravity_client.AntigravityClient") as mock_client_class:
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        mock_client.generate_text_stream.return_value = iter(["Streaming ", "is ", "fun!"])
        mock_client.model = "mock-model"

        class Args:
            agy_cmd = "run"
            prompt = "Hello"
            system = None
            model = None
            temperature = 0.2
            output = None
            stream = True

        handle_cmd_antigravity(Args())

        mock_client.generate_text_stream.assert_called_once_with(prompt="Hello", system_instruction=None, temperature=0.2)
        mock_stdout.write.assert_any_call("Streaming ")
        mock_stdout.write.assert_any_call("is ")
        mock_stdout.write.assert_any_call("fun!")
        assert mock_stdout.flush.call_count >= 3

def test_cli_stream_output_file(tmp_path):
    from amb_cli.cli_modules.handlers_core.antigravity_handler import handle_cmd_antigravity

    out_file = tmp_path / "output.txt"

    with patch("integrations.antigravity.antigravity_client.AntigravityClient") as mock_client_class:
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        mock_client.generate_text_stream.return_value = iter(["File ", "writing ", "test"])
        mock_client.model = "mock-model"

        class Args:
            agy_cmd = "run"
            prompt = "Hello"
            system = None
            model = None
            temperature = 0.2
            output = str(out_file)
            stream = True

        handle_cmd_antigravity(Args())

        mock_client.generate_text_stream.assert_called_once_with(prompt="Hello", system_instruction=None, temperature=0.2)
        assert out_file.read_text(encoding="utf-8") == "File writing test"

@patch("builtins.print")
def test_cli_sync_fallback(mock_print):
    from amb_cli.cli_modules.handlers_core.antigravity_handler import handle_cmd_antigravity

    with patch("integrations.antigravity.antigravity_client.AntigravityClient") as mock_client_class:
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        mock_client.generate_text.return_value = "Synchronous response"
        mock_client.model = "mock-model"

        class Args:
            agy_cmd = "run"
            prompt = "Sync hello"
            system = None
            model = None
            temperature = 0.2
            output = None
            stream = False

        # Also testing with no stream flag defined
        class ArgsNoStreamFlag:
            agy_cmd = "run"
            prompt = "Sync hello"
            system = None
            model = None
            temperature = 0.2
            output = None

        handle_cmd_antigravity(Args())
        mock_client.generate_text.assert_called_with(prompt="Sync hello", system_instruction=None, temperature=0.2)
        mock_print.assert_any_call("Synchronous response")

        handle_cmd_antigravity(ArgsNoStreamFlag())
        assert mock_client.generate_text.call_count == 2

def test_stream_yielding_fallback_midstream():
    from amb_cli.integrations.antigravity.antigravity_client import AntigravityClient

    class FakeBackend:
        def _generate_stream_via_gemini_api(self, *args, **kwargs):
            yield "First part"
            raise ValueError("Connection died")

    client = AntigravityClient()
    client.api_key = "FAKE_KEY"
    client.backend = FakeBackend()

    stream_gen = client.generate_text_stream("Say hello")
    assert next(stream_gen) == "First part"

    with pytest.raises(ValueError, match="Connection died"):
        next(stream_gen)
