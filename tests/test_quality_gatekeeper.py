import os
import json
import tempfile
import pytest
from pipeline.quality_gatekeeper import QualityGatekeeper


def test_quality_gatekeeper_detect_from_amb_project_json():
    with tempfile.TemporaryDirectory() as tmpdir:
        amb_dir = os.path.join(tmpdir, ".amb")
        os.makedirs(amb_dir, exist_ok=True)
        project_json_path = os.path.join(amb_dir, "amb_project.json")

        with open(project_json_path, "w", encoding="utf-8") as f:
            json.dump({
                "qa": {
                    "test": "pytest tests/unit",
                    "typecheck": "mypy ."
                }
            }, f)

        # Mock find_repo_root or pass repo_root
        qa = QualityGatekeeper.detect_qa_commands(repo_root=tmpdir)
        assert qa["test"] == "pytest tests/unit"
        assert qa["typecheck"] == "mypy ."


def test_quality_gatekeeper_detect_fallback_analyzer():
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create a python requirement file without .amb folder
        with open(os.path.join(tmpdir, "requirements.txt"), "w") as f:
            f.write("pytest\n")

        qa = QualityGatekeeper.detect_qa_commands(repo_root=tmpdir)
        assert "test" in qa
        assert "pytest" in qa["test"]


def test_quality_gatekeeper_execute_command():
    with tempfile.TemporaryDirectory() as tmpdir:
        # Command that succeeds
        assert QualityGatekeeper.execute_command("python -V", "version_check", cwd=tmpdir) is True

        # Command that fails
        assert QualityGatekeeper.execute_command("python -c \"import sys; sys.exit(1)\"", "fail_check", cwd=tmpdir) is False

        # Empty command
        assert QualityGatekeeper.execute_command("", "empty", cwd=tmpdir) is True


def test_quality_gatekeeper_run_qa():
    with tempfile.TemporaryDirectory() as tmpdir:
        amb_dir = os.path.join(tmpdir, ".amb")
        os.makedirs(amb_dir, exist_ok=True)
        project_json_path = os.path.join(amb_dir, "amb_project.json")

        with open(project_json_path, "w", encoding="utf-8") as f:
            json.dump({
                "qa": {
                    "syntax": "python -c \"print('OK')\""
                }
            }, f)

        success = QualityGatekeeper.run_qa(repo_root=tmpdir)
        assert success is True
