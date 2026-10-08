import pytest
from amb_cli.workspace.setup.setup_sanitizer import SetupSanitizer
from amb_cli.integrations.jules.tools.env_inspector import inspect_jules_env

def test_sanitize_script_removes_blocked_commands():
    script = "npm install\nnpm run dev\npip install -e .\nflask run\npytest -q"
    sanitized, removed = SetupSanitizer.sanitize_script(script)

    assert "npm run dev" not in sanitized
    assert "flask run" not in sanitized
    assert "npm install" in sanitized
    assert "pip install -e ." in sanitized
    assert "pytest -q" in sanitized

    assert len(removed) == 2
    assert "npm run dev" in removed
    assert "flask run" in removed

def test_has_blocking_commands():
    assert SetupSanitizer.has_blocking_commands("npm start") == True
    assert SetupSanitizer.has_blocking_commands("uvicorn main:app") == True
    assert SetupSanitizer.has_blocking_commands("npm install\npytest") == False

def test_integration_with_env_inspector(tmp_path, capsys):
    # Mocking a python setup to include a blocking command manually
    # to test if integration handles it. Usually `infer_setup_script`
    # doesn't return `flask run`, so we mock it.
    from unittest.mock import patch

    (tmp_path / "setup.py").write_text("from setuptools import setup\nsetup(name='test')\n", encoding="utf-8")

    with patch("workspace.setup.project_analyzer.ProjectAnalyzer.infer_setup_script") as mock_infer:
        mock_infer.return_value = "pip install -e .\nflask run\npytest"

        data = inspect_jules_env(str(tmp_path))

        assert "flask run" not in data["setup_script"]
        assert "pip install -e ." in data["setup_script"]
        assert "pytest" in data["setup_script"]
