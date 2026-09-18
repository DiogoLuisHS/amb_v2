import tkinter as tk
from tkinter import ttk
import subprocess
import os
import sys

# Adiciona o diretório raiz ao sys.path para conseguir importar os parsers
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from cli_modules.cli_parsers import create_parser
try:
    from config import find_repo_root
except ImportError:
    from config.config import find_repo_root

from gui.wizard_core.parser_extractor import extract_commands, clean_command_map, detect_repo_name
from gui.wizard_core.runner_tab import RunnerTab
from gui.wizard_core.settings_tab import SettingsTab


class DynamicWizard(tk.Tk):
    """Main Application Window for the AMB_V2 Command Wizard."""

    def __init__(self):
        super().__init__()
        self.title("AMB_V2 - Dynamic Command Wizard")
        self.geometry("850x720")
        self.configure(padx=20, pady=20)
        
        self.result_command = None
        
        self.project_root = find_repo_root()
        self.env_path = os.path.join(self.project_root, ".env")

        self.repo_name_var = tk.StringVar(value=detect_repo_name(self.project_root, self.env_path))
        self.project_root_var = tk.StringVar(value=self.project_root)
        self.env_path_var = tk.StringVar(value=self.env_path)
        
        self.parser = create_parser()
        raw_command_map = extract_commands(self.parser)
        self.command_map = clean_command_map(raw_command_map)

        ttk.Label(self, text="⚡ AMB_V2 Command Wizard", font=("Segoe UI", 16, "bold")).pack(anchor="w", pady=(0, 10))

        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True)

        self.tab_runner_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_runner_frame, text="Runner")

        self.tab_settings_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_settings_frame, text="Configurações")

        self.runner_tab = RunnerTab(self.tab_runner_frame, self)
        self.settings_tab = SettingsTab(self.tab_settings_frame, self)

    def execute_cmd(self):
        """Executes the command built by the RunnerTab."""
        self.result_command = self.runner_tab.build_command_string()
        self.destroy()


def start_wizard():
    app = DynamicWizard()
    app.attributes('-topmost', True)
    app.after_idle(app.attributes, '-topmost', False)
    app.mainloop()
    
    if app.result_command:
        print(f"\n⚡ Executando comando gerado pelo Wizard (no projeto {app.project_root}):\n> {app.result_command}\n")
        subprocess.run(app.result_command, shell=True, cwd=app.project_root)

if __name__ == "__main__":
    start_wizard()
