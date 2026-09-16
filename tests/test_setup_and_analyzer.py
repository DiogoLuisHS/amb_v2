import os
import json
import pytest
import tempfile
from config.setup_modules.project_analyzer import ProjectAnalyzer
from config.setup_modules.amb_provisioner import AmbProvisioner
from config.setup_project import run_setup
from config.config import main as run_check


def test_project_analyzer_detect_python():
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create a requirements.txt file
        with open(os.path.join(tmpdir, "requirements.txt"), "w") as f:
            f.write("pytest>=7.0.0\n")

        stack = ProjectAnalyzer.detect_stack(tmpdir)

        assert stack["type"] == "python"
        assert stack["primary_language"] == "python"
        assert stack["package_manager"] == "pip"

        qa = ProjectAnalyzer.infer_qa_commands(stack, tmpdir)
        assert "test" in qa
        assert "pytest" in qa["test"]


def test_project_analyzer_detect_node():
    with tempfile.TemporaryDirectory() as tmpdir:
        pkg_json = {
            "name": "test-node",
            "scripts": {
                "test": "vitest run",
                "typecheck": "tsc --noEmit",
                "build": "vite build"
            }
        }
        with open(os.path.join(tmpdir, "package.json"), "w") as f:
            json.dump(pkg_json, f)

        stack = ProjectAnalyzer.detect_stack(tmpdir)

        assert stack["type"] == "node/typescript"
        assert stack["primary_language"] in ["typescript", "javascript"]

        qa = ProjectAnalyzer.infer_qa_commands(stack, tmpdir)
        assert qa["test"] in ["npm test", "npm run test"]
        assert qa["typecheck"] == "npm run typecheck"
        assert qa["build"] == "npm run build"


def test_project_analyzer_detect_go():
    with tempfile.TemporaryDirectory() as tmpdir:
        with open(os.path.join(tmpdir, "go.mod"), "w") as f:
            f.write("module example.com/test\n\ngo 1.21\n")

        stack = ProjectAnalyzer.detect_stack(tmpdir)

        assert stack["type"] == "go"
        assert stack["primary_language"] == "go"

        qa = ProjectAnalyzer.infer_qa_commands(stack, tmpdir)
        assert "go test ./..." in qa["test"]
        assert "go vet ./..." in qa["typecheck"]


def test_amb_provisioner_single_generic_persona():
    with tempfile.TemporaryDirectory() as tmpdir:
        stack = {"project_type": "python", "primary_language": "python"}
        AmbProvisioner.provision_structure(
            root=tmpdir,
            stack=stack,
            repo_name="org/my-project",
            qa_commands={"test": "pytest"}
        )

        personas_dir = os.path.join(tmpdir, ".amb", "personas")
        diarios_dir = os.path.join(tmpdir, ".amb", "diarios")

        # Must have ONLY engineer.md
        persona_files = os.listdir(personas_dir)
        assert persona_files == ["engineer.md"]

        diario_files = os.listdir(diarios_dir)
        assert diario_files == ["engineer.md"]

        # Prompts gitkeep and readme must exist
        assert os.path.exists(os.path.join(tmpdir, ".amb", "prompts", ".gitkeep"))
        assert os.path.exists(os.path.join(tmpdir, ".amb", "README.md"))
        assert os.path.exists(os.path.join(tmpdir, ".env.example"))

        # .gitignore must contain .env protection
        gitignore_path = os.path.join(tmpdir, ".gitignore")
        assert os.path.exists(gitignore_path)
        with open(gitignore_path, "r") as f:
            content = f.read()
            assert ".env" in content
            assert ".env.local" in content


def test_setup_dry_run():
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create a python project file
        with open(os.path.join(tmpdir, "requirements.txt"), "w") as f:
            f.write("fastapi\n")

        config = run_setup(interactive=False, target_dir=tmpdir, dry_run=True)
        assert isinstance(config, dict)
        assert config.get("stack", {}).get("type") == "python"

        # In dry run mode, .amb must NOT be created
        assert not os.path.exists(os.path.join(tmpdir, ".amb"))


def test_config_check_json():
    diag = run_check(as_json=True)
    assert isinstance(diag, dict)
    assert "root" in diag
    assert "keys" in diag
    assert "git" in diag
    assert "personas_count" in diag
    assert diag["personas_count"] == 1
