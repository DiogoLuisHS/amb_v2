import pytest
import tkinter as tk
from unittest.mock import patch, MagicMock

from amb_cli.core.exceptions import AmbError
from amb_cli.gui.wizard_app import start_wizard
from amb_cli.gui.wizard_core.settings_tab import SettingsTab

def test_start_wizard_headless_fallback():
    """Test that start_wizard gracefully falls back when DynamicWizard raises TclError in a headless environment."""
    with patch("amb_cli.gui.wizard_app.DynamicWizard") as mock_wizard:
        # Simulate headless environment failure
        mock_wizard.side_effect = tk.TclError("no display name and no $DISPLAY environment variable")

        with pytest.raises(Exception) as exc_info:
            import sys
            # The exception that is actually raised and caught by pytest might be different due to import behavior,
            # so we'll just check if it raised what we expect
            # We must be careful because it will raise an actual AmbError from core.exceptions which
            # is different from amb_cli.core.exceptions if they are loaded differently.
            start_wizard()

        assert "Interface gráfica indisponível no ambiente atual" in str(exc_info.value)
        assert "Execute a CLI diretamente pelo terminal" in getattr(exc_info.value, 'hint', str(exc_info.value))

@patch("amb_cli.gui.wizard_core.settings_tab.os.path.exists")
@patch("amb_cli.gui.wizard_core.settings_tab.open")
@patch("amb_cli.gui.wizard_core.settings_tab.os.makedirs")
@patch("amb_cli.gui.wizard_core.settings_tab.messagebox")
def test_save_env_syncs_config_manager(mock_messagebox, mock_makedirs, mock_open, mock_exists):
    """Test that saving settings automatically reloads ConfigManager."""
    mock_exists.return_value = False # simplify file reading logic

    # Mock ConfigManager.reload()
    mock_manager = MagicMock()

    # Mock wizard parent
    mock_wizard = MagicMock()
    mock_wizard.env_path = "/tmp/fake.env"

    # Need to patch creating variables as Tk needs a root window
    with patch("amb_cli.gui.wizard_core.settings_tab.tk.StringVar"), \
         patch("amb_cli.gui.wizard_core.settings_tab.ttk.Frame"), \
         patch("amb_cli.gui.wizard_core.settings_tab.ttk.Scrollbar"), \
         patch("amb_cli.gui.wizard_core.settings_tab.tk.Canvas"), \
         patch("amb_cli.gui.wizard_core.settings_tab.ttk.LabelFrame"), \
         patch("amb_cli.gui.wizard_core.settings_tab.ttk.Label"), \
         patch("amb_cli.gui.wizard_core.settings_tab.ttk.Button"), \
         patch("amb_cli.gui.wizard_core.settings_tab.ttk.Entry"):

        tab = SettingsTab(MagicMock(), mock_wizard)
        # Give it some fake env entries to save
        mock_var = MagicMock()
        mock_var.get.return_value = "fake_val"
        tab.env_entries = {"FAKE_KEY": (mock_var, None)}

        import sys
        sys.modules['core.config_manager'] = MagicMock(ConfigManager=MagicMock(get_instance=MagicMock(return_value=mock_manager)))

        try:
             tab.save_env()
        finally:
             del sys.modules['core.config_manager']

    # Ensure reload was called
    mock_manager.reload.assert_called_once()

    # Ensure success message was displayed and contains the new string
    mock_messagebox.showinfo.assert_called_once()
    assert "Configurações salvas e recarregadas com sucesso!" in mock_messagebox.showinfo.call_args[0][1]

@patch("amb_cli.gui.wizard_core.settings_tab.os.path.exists")
@patch("amb_cli.gui.wizard_core.settings_tab.open")
@patch("amb_cli.gui.wizard_core.settings_tab.os.makedirs")
@patch("amb_cli.gui.wizard_core.settings_tab.messagebox")
def test_save_env_resilience(mock_messagebox, mock_makedirs, mock_open, mock_exists):
    """Test that saving settings does not crash if ConfigManager.reload() raises an exception."""
    mock_exists.return_value = False

    mock_manager = MagicMock()
    mock_manager.reload.side_effect = Exception("Simulated ConfigManager failure")

    # Mock wizard parent
    mock_wizard = MagicMock()
    mock_wizard.env_path = "/tmp/fake.env"

    with patch("amb_cli.gui.wizard_core.settings_tab.tk.StringVar"), \
         patch("amb_cli.gui.wizard_core.settings_tab.ttk.Frame"), \
         patch("amb_cli.gui.wizard_core.settings_tab.ttk.Scrollbar"), \
         patch("amb_cli.gui.wizard_core.settings_tab.tk.Canvas"), \
         patch("amb_cli.gui.wizard_core.settings_tab.ttk.LabelFrame"), \
         patch("amb_cli.gui.wizard_core.settings_tab.ttk.Label"), \
         patch("amb_cli.gui.wizard_core.settings_tab.ttk.Button"), \
         patch("amb_cli.gui.wizard_core.settings_tab.ttk.Entry"):

        tab = SettingsTab(MagicMock(), mock_wizard)
        tab.env_entries = {}

        # This should not raise an exception
        import sys
        sys.modules['core.config_manager'] = MagicMock(ConfigManager=MagicMock(get_instance=MagicMock(return_value=mock_manager)))

        try:
             tab.save_env()
        finally:
             del sys.modules['core.config_manager']

    # Ensure success message was still displayed
    mock_messagebox.showinfo.assert_called_once()
    assert "Configurações salvas e recarregadas com sucesso!" in mock_messagebox.showinfo.call_args[0][1]
