import pytest
from unittest.mock import MagicMock
from integrations.jules.tools.env_inspector import inspect_jules_env, run_inspect_env
from cli_modules.handlers_core.jules_handler import handle_cmd_jules


def test_inspect_jules_env(tmp_path):
    (tmp_path / "setup.py").write_text("from setuptools import setup\nsetup(name='test')\n", encoding="utf-8")
    (tmp_path / "tests").mkdir()

    data = inspect_jules_env(str(tmp_path))
    assert isinstance(data, dict)
    assert data["root"] == str(tmp_path)
    assert data["stack"]["type"] == "python"
    assert "pip install -e ." in data["setup_script"]
    assert "pytest" in data["setup_script"]
    assert "Ubuntu 24.04 LTS" in data["vm_base_os"]
    assert len(data["native_vm_tools"]) > 0


def test_run_inspect_env_json(tmp_path, capsys):
    (tmp_path / "requirements.txt").write_text("flask\n", encoding="utf-8")
    res = run_inspect_env(target_dir=str(tmp_path), as_json=True)
    assert isinstance(res, dict)
    captured = capsys.readouterr()
    assert '"vm_base_os"' in captured.out


def test_run_inspect_env_text(tmp_path, capsys):
    (tmp_path / "requirements.txt").write_text("flask\n", encoding="utf-8")
    res = run_inspect_env(target_dir=str(tmp_path), as_json=False)
    assert isinstance(res, dict)
    captured = capsys.readouterr()
    assert "DIAGNÓSTICO DE AMBIENTE: GOOGLE JULES VM" in captured.out
    assert "Run and Snapshot" in captured.out


def test_jules_handler_routes_env(tmp_path):
    args = MagicMock()
    args.jules_cmd = "env"
    args.dir = str(tmp_path)
    args.json = True

    # Call handle_cmd_jules and ensure it completes without exception
    handle_cmd_jules(args)
