import pytest
from unittest.mock import patch, MagicMock
from amb_cli.integrations.stitch.stitch_client import StitchClient
from amb_cli.cli_modules.handlers_core.stitch_handler import handle_cmd_stitch

def test_stitch_generate_screen_with_title():
    client = StitchClient()
    client.project_id = "test-project"

    with patch.object(client, '_run_node_command') as mock_run:
        mock_run.return_value = {
            "screenId": "123",
            "htmlCode": "<html><head><title>Old Title</title></head><body></body></html>"
        }

        with patch.object(client, 'save_screen_html') as mock_save:
            res = client.generate_screen(prompt="Create a login form", title="Login Page", output_file="output.html")

            # Check prompt payload
            args, kwargs = mock_run.call_args
            assert args[0] == "generate_screen_from_text"
            assert "Title: Login Page" in args[1]["prompt"]
            assert "Specification: Create a login form" in args[1]["prompt"]
            assert args[1]["title"] == "Login Page"

            # Check HTML code title replacement
            assert "<title>Login Page</title>" in res["htmlCode"]
            assert "<title>Old Title</title>" not in res["htmlCode"]

            mock_save.assert_called_once_with(res, "output.html")

@patch('integrations.stitch.stitch_client.StitchClient')
def test_stitch_handler_generate_with_title_and_no_output(mock_stitch_cls):
    args = MagicMock()
    args.stitch_cmd = "generate"
    args.prompt = "Create a dashboard"
    args.prompt_flag = None
    args.device = "DESKTOP"
    args.title = "Main Dashboard!"
    args.output = None
    args.json = True

    mock_inst = mock_stitch_cls.return_value
    mock_inst.generate_screen.return_value = {"screenId": "123"}

    with patch('amb_cli.integrations.stitch.stitch_client.StitchClient', mock_stitch_cls):
        handle_cmd_stitch(args)

        mock_inst.generate_screen.assert_called_once()
        called_kwargs = mock_inst.generate_screen.call_args.kwargs

        assert called_kwargs["prompt"] == "Create a dashboard"
        assert called_kwargs["title"] == "Main Dashboard!"
        assert called_kwargs["device_type"] == "DESKTOP"
        assert called_kwargs["output_file"] == "./public/main-dashboard.html"
