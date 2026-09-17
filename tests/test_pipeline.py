import unittest
from unittest.mock import patch, MagicMock

from amb_cli.pipeline.pipeline_core.prompt_builder import (
    parse_single_prompt,
    clean_html_for_summary,
    build_executive_prompt
)
from amb_cli.pipeline.pipeline import PipelineOrchestrator

class TestPipelineCore(unittest.TestCase):

    def test_parse_single_prompt(self):
        markdown = """# Especificação Visual
Conteúdo Visual
# Especificação de Engenharia
Conteúdo Dev"""
        vis, dev = parse_single_prompt(markdown)
        self.assertEqual(vis, "Conteúdo Visual")
        self.assertEqual(dev, "Conteúdo Dev")

    def test_clean_html_for_summary(self):
        html = """
        <div>
            <script>alert('xss');</script>
            <style>body { color: red; }</style>
            <svg path="giant"></svg>
            <img src="data:image/png;base64,xxxxxxxxxx">
            <p>Hello   World</p>
        </div>
        """
        cleaned = clean_html_for_summary(html)
        self.assertNotIn("<script>", cleaned)
        self.assertNotIn("<style>", cleaned)
        self.assertIn("[Ícone SVG]", cleaned)
        self.assertIn("[Imagem Base64]", cleaned)
        self.assertIn("Hello World", cleaned)

    def test_build_executive_prompt(self):
        prompt = build_executive_prompt(
            repo_name="my_repo",
            starting_branch="main",
            file_label="task.md",
            jules_prompt="Make an API",
            stitch_prompt="Make a UI",
            current_screen_id="screen_123",
            screen_title="Dashboard",
            screenshot_url="http://screenshot",
            stitch_summary="Summary of UI",
            rules_summary="No circular imports",
            skip_stitch=False
        )
        self.assertIn("my_repo", prompt)
        self.assertIn("Make an API", prompt)
        self.assertIn("Make a UI", prompt)
        self.assertIn("screen_123", prompt)
        self.assertIn("Dashboard", prompt)
        self.assertIn("No circular imports", prompt)
        self.assertIn("http://screenshot", prompt)
        self.assertIn("Summary of UI", prompt)


class TestPipelineOrchestrator(unittest.TestCase):

    @patch("amb_cli.pipeline.pipeline.process_design_stage")
    @patch("amb_cli.pipeline.pipeline.build_executive_prompt")
    @patch("amb_cli.pipeline.pipeline.JulesClient")
    @patch("amb_cli.pipeline.pipeline.PipelineOrchestrator._synthesize_stitch_ui")
    @patch("amb_cli.pipeline.pipeline.PipelineOrchestrator._extract_clean_rules")
    @patch("amb_cli.pipeline.pipeline.GitService")
    @patch("amb_cli.pipeline.pipeline.find_repo_root", return_value="/tmp/repo")
    @patch("amb_cli.pipeline.pipeline.get_repo_name", return_value="test_repo")
    @patch("amb_cli.pipeline.pipeline.QualityGatekeeper.run_qa")
    @patch("amb_cli.pipeline.pipeline.PipelineOrchestrator._monitor_jules_session")
    def test_pipeline_orchestrator_run(
        self,
        mock_monitor_session,
        mock_run_qa,
        mock_get_repo_name,
        mock_find_repo_root,
        mock_git_service,
        mock_extract_rules,
        mock_synth,
        mock_jules_client,
        mock_build_prompt,
        mock_process_design
    ):
        mock_git_instance = MagicMock()
        mock_git_instance.get_current_branch.return_value = "main"
        mock_git_service.return_value = mock_git_instance

        mock_process_design.return_value = {
            "current_screen_id": "scr_1",
            "stitch_html": "<html></html>",
            "screenshot_url": "url",
            "screen_title": "title",
            "cancelled": False
        }

        mock_jules_instance = MagicMock()
        mock_jules_instance.create_session.return_value = {"name": "session/123", "id": "123"}
        mock_jules_client.return_value = mock_jules_instance

        mock_build_prompt.return_value = "FINAL PROMPT"

        PipelineOrchestrator.run(
            prompt_file=None,
            stitch_prompt_file=None,
            jules_prompt_file=None,
            skip_stitch=False,
            auto_approve=True,
            no_qa=True,
        )

        mock_process_design.assert_called_once()
        mock_synth.assert_called_once()
        mock_build_prompt.assert_called_once()
        mock_jules_instance.create_session.assert_called_once()
        mock_monitor_session.assert_called_once_with("123", "/tmp/repo", True)
