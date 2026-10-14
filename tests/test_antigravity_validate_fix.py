import os
import tempfile
import pytest
from unittest.mock import patch

from amb_cli.cli_modules.cli_parsers import create_parser
from amb_cli.cli_modules.handlers_core.antigravity_handler import handle_cmd_antigravity

@pytest.fixture
def temp_file():
    fd, path = tempfile.mkstemp(suffix=".py")
    with os.fdopen(fd, "w") as f:
        f.write("def old_function():\n    pass\n")
    yield path
    if os.path.exists(path):
        os.remove(path)

def test_cli_parser_fix_flag():
    parser = create_parser()

    args = parser.parse_args(["validate", "some_file.py", "--fix"])
    assert getattr(args, "fix", False) is True

    args = parser.parse_args(["agy", "validate", "some_file.py", "--fix"])
    assert getattr(args, "fix", False) is True

    args = parser.parse_args(["validate", "some_file.py"])
    assert getattr(args, "fix", False) is False

def test_validate_without_fix(temp_file):
    parser = create_parser()
    args = parser.parse_args(["agy", "validate", temp_file])
    args.agy_cmd = "validate"

    with patch("integrations.antigravity.tools.validate_architecture.run_validate_architecture", return_value="Erro: violação de regra"):
        with patch("builtins.print"):
            try:
                handle_cmd_antigravity(args)
            except SystemExit:
                pass

    with open(temp_file, "r") as f:
        content = f.read()

    assert content == "def old_function():\n    pass\n"

def test_validate_with_fix_applied(temp_file):
    parser = create_parser()
    args = parser.parse_args(["agy", "validate", temp_file, "--fix"])
    args.agy_cmd = "validate"

    with patch("builtins.input", return_value="y"), \
         patch("builtins.print"), \
         patch("integrations.antigravity.tools.validate_architecture.run_validate_architecture", return_value="Violação: precisa de tipagem"), \
         patch("integrations.antigravity.tools.validate_architecture.generate_architecture_fix", return_value="def new_function() -> None:\n    pass\n"):

        handle_cmd_antigravity(args)

    with open(temp_file, "r") as f:
        content = f.read()

    assert content == "def new_function() -> None:\n    pass\n"

def test_validate_with_fix_rejected(temp_file):
    parser = create_parser()
    args = parser.parse_args(["agy", "validate", temp_file, "--fix"])
    args.agy_cmd = "validate"

    with patch("builtins.input", return_value="n"), \
         patch("builtins.print"), \
         patch("integrations.antigravity.tools.validate_architecture.run_validate_architecture", return_value="Violação detectada."), \
         patch("integrations.antigravity.tools.validate_architecture.generate_architecture_fix", return_value="def new_function() -> None:\n    pass\n"):

        handle_cmd_antigravity(args)

    with open(temp_file, "r") as f:
        content = f.read()

    assert content == "def old_function():\n    pass\n"
