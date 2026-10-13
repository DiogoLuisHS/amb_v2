import pytest
from unittest.mock import patch, MagicMock
from amb_cli.workspace.setup.setup_project import run_setup
from amb_cli.cli_modules.cli_parsers import create_parser

@patch("amb_cli.core.diagnostics.run_environment_diagnostics")
@patch("amb_cli.workspace.setup.setup_project.AmbProvisioner.provision_structure")
def test_run_setup_without_check(mock_provision, mock_diagnostics, tmp_path):
    run_setup(interactive=False, target_dir=str(tmp_path), dry_run=False, run_check=False)
    mock_diagnostics.assert_not_called()

@patch("amb_cli.workspace.setup.setup_project.run_environment_diagnostics", create=True)
@patch("amb_cli.workspace.setup.setup_project.AmbProvisioner.provision_structure")
def test_run_setup_with_check(mock_provision, mock_diagnostics, tmp_path):
    # run_environment_diagnostics is imported locally in run_setup when run_check is True,
    # so we mock the one in core.diagnostics as well, or we mock the exact place where it's imported
    with patch("core.diagnostics.run_environment_diagnostics") as mock_core_diagnostics:
        run_setup(interactive=False, target_dir=str(tmp_path), dry_run=False, run_check=True)
        mock_core_diagnostics.assert_called_once_with(as_json=False)

@patch("amb_cli.workspace.setup.setup_project.run_environment_diagnostics", create=True)
def test_run_setup_dry_run_with_check(mock_diagnostics, tmp_path):
    with patch("core.diagnostics.run_environment_diagnostics") as mock_core_diagnostics:
        run_setup(interactive=False, target_dir=str(tmp_path), dry_run=True, run_check=True)
        mock_core_diagnostics.assert_called_once_with(as_json=False)

def test_setup_parser_check_flag():
    parser = create_parser()
    args = parser.parse_args(["setup", "--check"])
    assert getattr(args, "check", False) is True
