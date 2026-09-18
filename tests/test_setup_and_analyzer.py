import os
import json
import pytest
import tempfile
from workspace.setup.project_analyzer import ProjectAnalyzer
from workspace.setup.amb_provisioner import AmbProvisioner
from workspace.setup.setup_project import run_setup
from core import run_environment_diagnostics as run_check


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

def test_setup_dry_run_dict_return(tmp_path):
    import json
    # Create a python project file
    req_file = tmp_path / "requirements.txt"
    req_file.write_text("fastapi\n")

    config = run_setup(interactive=False, target_dir=str(tmp_path), dry_run=True)
    assert isinstance(config, dict)
    assert config.get("stack", {}).get("type") == "python"

    # In dry run mode, .amb must NOT be created
    assert not (tmp_path / ".amb").exists()

    # Verify schema structure
    assert "$schema" in config
    assert "version" in config
    assert "name" in config
    assert "repository" in config
    assert "default_branch" in config
    assert "stitch_project_id" in config
    assert "stack" in config
    assert "qa" in config
    assert "personas" in config

def test_setup_force_provision(tmp_path):
    import json
    req_file = tmp_path / "requirements.txt"
    req_file.write_text("fastapi\n")

    config = run_setup(interactive=False, target_dir=str(tmp_path), force=True, dry_run=False)
    assert isinstance(config, dict)

    # In non-dry run mode, .amb must be created
    amb_dir = tmp_path / ".amb"
    assert amb_dir.exists()
    assert (amb_dir / "amb_project.json").exists()

    # Test if amb_project.json is valid JSON
    with open(amb_dir / "amb_project.json", "r") as f:
        project_data = json.load(f)

    assert project_data["$schema"] == "https://amb-v2.dev/schemas/amb_project.v2.json"
    assert project_data["stack"]["type"] == "python"
    assert project_data["personas"]["active"] == ["engineer"]
