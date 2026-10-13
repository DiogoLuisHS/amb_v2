import pytest
from unittest.mock import patch, MagicMock

from cli_modules.cli_handlers import cmd_prompt
from cli_modules.handlers_core.antigravity_handler import handle_cmd_antigravity

class MockArgs:
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)


@patch("integrations.antigravity.tools.synthesize_prompt.run_synthesize_prompt")
def test_cmd_prompt_invokes_direct_run_synthesize_prompt(mock_run):
    """Test cmd_prompt calls run_synthesize_prompt directly without modifying the args object."""
    args = MockArgs(idea="Test Idea", role="engineer", output="out.md", image="mock.png", queue=False)

    cmd_prompt(args)

    mock_run.assert_called_once_with(
        raw_idea="Test Idea",
        role="engineer",
        output_file="out.md",
        image_path="mock.png",
        queue=False
    )

    # Assert args wasn't mutated with spurious keys
    assert not hasattr(args, "agy_cmd")


@patch("integrations.antigravity.tools.synthesize_prompt.run_synthesize_prompt")
def test_handle_cmd_antigravity_with_image_and_idea(mock_run):
    """Test handle_cmd_antigravity correctly handles image and idea parameters."""
    args = MockArgs(
        agy_cmd="prompt",
        idea="Antigravity Idea",
        role="architect",
        output="out2.md",
        image="mock2.png",
        queue=True
    )

    handle_cmd_antigravity(args)

    mock_run.assert_called_once_with(
        raw_idea="Antigravity Idea",
        role="architect",
        output_file="out2.md",
        image_path="mock2.png",
        queue=True
    )


@patch("integrations.antigravity.tools.synthesize_prompt.run_synthesize_prompt")
def test_no_spurious_keys_injected(mock_run):
    """Ensure that no spurious keys (like agy_cmd) are injected into args during cmd_prompt execution."""
    args = MockArgs(synthesize="Synth Idea", role="general")

    cmd_prompt(args)

    mock_run.assert_called_once_with(
        raw_idea="Synth Idea",
        role="general",
        output_file=None,
        image_path=None,
        queue=False
    )

    # Check that agy_cmd was not added to args
    assert not hasattr(args, "agy_cmd")
