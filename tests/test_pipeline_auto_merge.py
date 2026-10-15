import unittest
from unittest.mock import patch, MagicMock

from amb_cli.pipeline.pipeline import PipelineOrchestrator
from amb_cli.cli_modules.cli_handlers import cmd_pipeline

class TestPipelineAutoMerge(unittest.TestCase):

    @patch("pipeline.pipeline.PipelineOrchestrator.run")
    def test_cmd_pipeline_flags(self, mock_run):
        """Garante que o parser propaga as novas flags pro Orquestrador."""
        args = MagicMock()
        args.spec = None
        args.stitch_prompt = None
        args.jules_prompt = None
        args.auto_approve = False
        args.skip_stitch = False
        args.no_qa = False
        args.resume_session = None
        args.device = None
        args.device_type = None
        args.edit_screen_id = None
        args.screen_id = None
        args.sync_ds = False
        args.branch = "main"
        args.auto_merge = True
        args.no_auto_merge = False

        cmd_pipeline(args)

        mock_run.assert_called_once_with(
            stitch_prompt_file=None,
            jules_prompt_file=None,
            auto_approve=False,
            skip_stitch=False,
            no_qa=False,
            resume_session=None,
            device_type=None,
            edit_screen_id=None,
            screen_id=None,
            sync_ds=False,
            starting_branch="main",
            auto_merge=True,
            no_auto_merge=False
        )


    @patch("amb_cli.pipeline.pipeline.JulesClient")
    @patch("amb_cli.pipeline.pipeline.GitService")
    @patch("amb_cli.pipeline.pipeline.find_repo_root", return_value="/tmp/repo")
    @patch("amb_cli.pipeline.pipeline.get_repo_name", return_value="my_repo")
    @patch("amb_cli.pipeline.pipeline.process_design_stage")
    @patch("amb_cli.pipeline.pipeline.PipelineOrchestrator._extract_clean_rules", return_value="")
    @patch("amb_cli.pipeline.pipeline.PipelineOrchestrator._monitor_jules_session")
    def test_run_auto_approve_sets_auto_merge(
        self, mock_monitor, mock_rules, mock_design, mock_repo_name, mock_repo_root, mock_git, mock_jules
    ):
        """Garante que auto_approve (-y) ativa auto_merge por default, se no_auto_merge for False."""
        mock_jules_instance = mock_jules.return_value
        mock_jules_instance.create_session.return_value = {"name": "sessions/123", "id": "123"}

        mock_design.return_value = {
            "cancelled": False,
            "current_screen_id": "screen1",
            "stitch_html": "",
            "screenshot_url": "",
            "screen_title": "Title"
        }

        PipelineOrchestrator.run(
            prompt_file="test.md",
            auto_approve=True,
            skip_stitch=True,
            no_auto_merge=False
        )

        mock_monitor.assert_called_once()
        args, kwargs = mock_monitor.call_args
        # kwargs deve ter auto_merge=True
        self.assertTrue(kwargs.get("auto_merge"))


    @patch("amb_cli.pipeline.pipeline.JulesClient")
    @patch("amb_cli.pipeline.pipeline.GitService")
    @patch("amb_cli.pipeline.pipeline.find_repo_root", return_value="/tmp/repo")
    @patch("amb_cli.pipeline.pipeline.get_repo_name", return_value="my_repo")
    @patch("amb_cli.pipeline.pipeline.process_design_stage")
    @patch("amb_cli.pipeline.pipeline.PipelineOrchestrator._extract_clean_rules", return_value="")
    @patch("amb_cli.pipeline.pipeline.PipelineOrchestrator._monitor_jules_session")
    def test_run_auto_approve_with_no_auto_merge(
        self, mock_monitor, mock_rules, mock_design, mock_repo_name, mock_repo_root, mock_git, mock_jules
    ):
        """Garante que --no-auto-merge desativa auto_merge mesmo com -y."""
        mock_jules_instance = mock_jules.return_value
        mock_jules_instance.create_session.return_value = {"name": "sessions/123", "id": "123"}

        mock_design.return_value = {
            "cancelled": False,
            "current_screen_id": "screen1",
            "stitch_html": "",
            "screenshot_url": "",
            "screen_title": "Title"
        }

        PipelineOrchestrator.run(
            prompt_file="test.md",
            auto_approve=True,
            skip_stitch=True,
            no_auto_merge=True
        )

        mock_monitor.assert_called_once()
        args, kwargs = mock_monitor.call_args
        self.assertFalse(kwargs.get("auto_merge"))


    @patch("amb_cli.pipeline.pipeline.QualityGatekeeper")
    @patch("amb_cli.pipeline.pipeline.JulesClient")
    @patch("amb_cli.pipeline.pipeline.log")
    @patch("amb_cli.pipeline.pipeline.log_error")
    def test_monitor_jules_session_merges_on_success(
        self, mock_log_error, mock_log, mock_jules, mock_qa
    ):
        """Garante que o merge roda se o QA passar e o estado for COMPLETED/SUCCEEDED."""
        mock_qa.run_qa.return_value = True

        mock_assist = MagicMock(return_value="COMPLETED")
        mock_merge = MagicMock()

        with patch.dict("sys.modules", {
            "agents.autonomous_loop": MagicMock(monitor_and_assist_session=mock_assist),
            "integrations.jules.tools.merge_session_pr": MagicMock(run_merge_session_pr=mock_merge)
        }):
            PipelineOrchestrator._monitor_jules_session(
                session_id="123",
                repo_root="/tmp",
                no_qa=False,
                auto_merge=True,
                starting_branch="feature-a"
            )

        mock_merge.assert_called_once_with(session_id="123", target_branch="feature-a")


    @patch("amb_cli.pipeline.pipeline.QualityGatekeeper")
    @patch("amb_cli.pipeline.pipeline.JulesClient")
    @patch("amb_cli.pipeline.pipeline.log")
    @patch("amb_cli.pipeline.pipeline.log_error")
    def test_monitor_jules_session_skips_merge_on_qa_fail(
        self, mock_log_error, mock_log, mock_jules, mock_qa
    ):
        """Garante que o merge não ocorre se a validação do QA falhar."""
        mock_qa.run_qa.return_value = False

        mock_assist = MagicMock(return_value="COMPLETED")
        mock_merge = MagicMock()

        with patch.dict("sys.modules", {
            "agents.autonomous_loop": MagicMock(monitor_and_assist_session=mock_assist),
            "integrations.jules.tools.merge_session_pr": MagicMock(run_merge_session_pr=mock_merge)
        }):
            PipelineOrchestrator._monitor_jules_session(
                session_id="123",
                repo_root="/tmp",
                no_qa=False,
                auto_merge=True,
                starting_branch="feature-a"
            )

        mock_merge.assert_not_called()


if __name__ == "__main__":
    unittest.main()
