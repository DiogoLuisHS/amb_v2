import os
import json
import pytest
from unittest.mock import patch, MagicMock

from amb_cli.core.console_presenter import ConsolePresenter
from amb_cli.pipeline.pipeline_core.qa_sandbox import LocalQASandbox

# === Testes do ConsolePresenter ===

def test_console_presenter_normal_mode(capsys):
    presenter = ConsolePresenter(json_mode=False, quiet_mode=False)

    # Test print_message
    presenter.print_message("Hello World")
    captured = capsys.readouterr()
    assert "Hello World" in captured.out

    # Test present_data
    presenter.present_data({"key": "value"})
    captured = capsys.readouterr()
    assert "Data: {'key': 'value'}" in captured.out

    # Test print_error
    presenter.print_error("A bad error")
    captured = capsys.readouterr()
    assert "ERRO" in captured.err
    assert "A bad error" in captured.err


def test_console_presenter_json_mode(capsys):
    presenter = ConsolePresenter(json_mode=True, quiet_mode=False)

    # Message should be suppressed
    presenter.print_message("Hello World")
    captured = capsys.readouterr()
    assert captured.out == ""

    # Error should be printed as JSON to stdout
    presenter.print_error("A JSON error", hint="Fix it")
    captured = capsys.readouterr()
    out_dict = json.loads(captured.out)
    assert out_dict["status"] == "error"
    assert out_dict["message"] == "A JSON error"
    assert out_dict["hint"] == "Fix it"

    # Data should be printed as JSON
    presenter.present_data({"key": "value"})
    captured = capsys.readouterr()
    out_dict = json.loads(captured.out)
    assert out_dict["key"] == "value"


def test_console_presenter_quiet_mode(capsys):
    presenter = ConsolePresenter(json_mode=False, quiet_mode=True)

    # Message should be suppressed
    presenter.print_message("Hello World")
    captured = capsys.readouterr()
    assert captured.out == ""

    # Data should be suppressed
    presenter.present_data({"key": "value"})
    captured = capsys.readouterr()
    assert captured.out == ""

    # Error is still printed to stderr
    presenter.print_error("A quiet error")
    captured = capsys.readouterr()
    assert "A quiet error" in captured.err


# === Testes do LocalQASandbox ===

def test_sandbox_save_run_log(tmp_path):
    repo_root = str(tmp_path)
    command = "pytest tests/"
    output = "Test Output"

    filepath = LocalQASandbox.save_run_log(command, output, True, repo_root=repo_root)

    assert os.path.exists(filepath)
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
        assert "Command: pytest tests/" in content
        assert "Status: SUCCESS" in content
        assert "Test Output" in content

def test_sandbox_extract_sanitized_failure_short():
    output = "Line 1\nLine 2\nLine 3"
    sanitized = LocalQASandbox.extract_sanitized_failure(output, max_lines=10)
    assert sanitized == output

def test_sandbox_extract_sanitized_failure_pytest():
    pytest_log = """============================= test session starts ==============================
collected 1 item

tests/test_example.py F                                                  [100%]

=================================== FAILURES ===================================
_________________________________ test_example _________________________________

    def test_example():
>       assert False
E       assert False

tests/test_example.py:3: AssertionError
=========================== short test summary info ============================
FAILED tests/test_example.py::test_example - assert False
============================== 1 failed in 0.12s ===============================
"""
    # Create artificial noise
    noise = "\n".join([f"noise line {i}" for i in range(50)])
    full_log = noise + "\n" + pytest_log

    sanitized = LocalQASandbox.extract_sanitized_failure(full_log, max_lines=20)

    # The noise should be mostly gone
    assert "noise line 10" not in sanitized
    assert "FAILED tests/test_example.py::test_example" in sanitized
    assert "assert False" in sanitized

def test_sandbox_extract_sanitized_failure_npm():
    npm_log = """
> my-project@1.0.0 build
> tsc

src/index.ts(5,1): error TS2304: Cannot find name 'foo'.
src/utils.ts(10,5): error TS2322: Type 'number' is not assignable to type 'string'.
"""
    noise = "\n".join([f"noise line {i}" for i in range(50)])
    full_log = noise + "\n" + npm_log

    sanitized = LocalQASandbox.extract_sanitized_failure(full_log, max_lines=20)

    assert "error TS2304: Cannot find name 'foo'." in sanitized
    assert "error TS2322: Type 'number' is not assignable to type 'string'." in sanitized
    assert "noise line 10" not in sanitized
