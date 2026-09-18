import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
from typing import Any

from .parser_extractor import detect_repo_name

class SettingsTab:
    """Manages the Settings (.env) Tab for the Wizard."""

    def __init__(self, parent_frame: ttk.Frame, wizard: Any):
        self.wizard = wizard
        self.env_entries = {}

        container = ttk.Frame(parent_frame, padding=15)
        container.pack(fill="both", expand=True)

        self._build_project_header(container)
        self._build_env_canvas(container)

        self.load_env_fields()

        self._build_action_buttons(container)

    def _build_project_header(self, container: ttk.Frame):
        header_frame = ttk.LabelFrame(container, text="Contexto do Projeto Ativo", padding=10)
        header_frame.pack(fill="x", pady=(0, 10))

        row_top = ttk.Frame(header_frame)
        row_top.pack(fill="x", pady=2)
        ttk.Label(row_top, text="Repositório:", font=("Segoe UI", 9, "bold"), width=15).pack(side="left")
        ttk.Label(row_top, textvariable=self.wizard.repo_name_var, font=("Segoe UI", 9, "bold"), foreground="#0066cc").pack(side="left")
        ttk.Button(row_top, text="📁 Trocar Pasta do Projeto...", command=self.choose_project_dir).pack(side="right")

        row_dir = ttk.Frame(header_frame)
        row_dir.pack(fill="x", pady=2)
        ttk.Label(row_dir, text="Diretório:", font=("Segoe UI", 9, "bold"), width=15).pack(side="left")
        ttk.Label(row_dir, textvariable=self.wizard.project_root_var, wraplength=600).pack(side="left")

        row_env = ttk.Frame(header_frame)
        row_env.pack(fill="x", pady=2)
        ttk.Label(row_env, text="Arquivo .env:", font=("Segoe UI", 9, "bold"), width=15).pack(side="left")
        ttk.Label(row_env, textvariable=self.wizard.env_path_var, foreground="#555555", wraplength=600).pack(side="left")

    def _build_env_canvas(self, container: ttk.Frame):
        ttk.Label(container, text="Parâmetros de Configuração (.env):", font=("Segoe UI", 10, "bold")).pack(anchor="w", pady=(5, 5))

        self.env_canvas = tk.Canvas(container, highlightthickness=0)
        env_scrollbar = ttk.Scrollbar(container, orient="vertical", command=self.env_canvas.yview)
        self.env_scrollable_frame = ttk.Frame(self.env_canvas)

        self.env_scrollable_frame.bind(
            "<Configure>",
            lambda e: self.env_canvas.configure(scrollregion=self.env_canvas.bbox("all"))
        )

        self.env_canvas_window = self.env_canvas.create_window((0, 0), window=self.env_scrollable_frame, anchor="nw")
        self.env_canvas.configure(yscrollcommand=env_scrollbar.set)

        self.env_canvas.bind(
            "<Configure>",
            lambda e: self.env_canvas.itemconfig(self.env_canvas_window, width=e.width)
        )

        self.env_canvas.pack(side="top", fill="both", expand=True)
        env_scrollbar.pack(side="right", fill="y")

    def _build_action_buttons(self, container: ttk.Frame):
        btn_bar = ttk.Frame(container)
        btn_bar.pack(fill="x", pady=(10, 0))

        ttk.Button(btn_bar, text="➕ Adicionar Variável", command=self.add_custom_env_var).pack(side="left")
        ttk.Button(btn_bar, text="🔄 Recarregar", command=self.load_env_fields).pack(side="left", padx=5)
        ttk.Button(btn_bar, text="💾 Salvar Configurações no .env", command=self.save_env).pack(side="right")

    def choose_project_dir(self):
        chosen = filedialog.askdirectory(initialdir=self.wizard.project_root, title="Selecione a Pasta do Projeto")
        if chosen:
            self.wizard.project_root = os.path.abspath(chosen)
            self.wizard.env_path = os.path.join(self.wizard.project_root, ".env")
            self.wizard.project_root_var.set(self.wizard.project_root)
            self.wizard.env_path_var.set(self.wizard.env_path)
            self.wizard.repo_name_var.set(detect_repo_name(self.wizard.project_root, self.wizard.env_path))
            self.load_env_fields()

    def load_env_fields(self):
        for child in self.env_scrollable_frame.winfo_children():
            child.destroy()

        self.env_entries.clear()
        env_data = {}

        if os.path.exists(self.wizard.env_path):
            try:
                with open(self.wizard.env_path, "r", encoding="utf-8", errors="replace") as f:
                    for line in f:
                        line_s = line.strip()
                        if "=" in line_s and not line_s.startswith("#"):
                            k, v = line_s.split("=", 1)
                            env_data[k.strip()] = v.strip()
            except Exception as e:
                messagebox.showwarning("Aviso", f"Erro ao ler .env do projeto: {e}")

        core_keys = [
            "TURSO_DATABASE_URL",
            "TURSO_AUTH_TOKEN",
            "PORT",
            "NODE_ENV",
            "STITCH_API_KEY",
            "STITCH_PROJECT_ID",
            "JULES_API_KEY",
            "GEMINI_API_KEY",
            "GITHUB_REPOSITORY",
        ]
        for ck in core_keys:
            if ck not in env_data:
                env_data[ck] = ""

        for key, val in env_data.items():
            self._render_env_row(key, val)

    def _render_env_row(self, key: str, val: str):
        row = ttk.Frame(self.env_scrollable_frame)
        row.pack(fill="x", pady=4, padx=5)

        lbl = ttk.Label(row, text=key, width=25, font=("Segoe UI", 9, "bold"), anchor="w")
        lbl.pack(side="left")

        val_var = tk.StringVar(value=val)
        entry = ttk.Entry(row, textvariable=val_var)
        entry.pack(side="left", fill="x", expand=True, padx=(5, 5))

        self.env_entries[key] = (val_var, row)

    def add_custom_env_var(self):
        var_name = simpledialog.askstring("Nova Variável", "Nome da variável de ambiente (ex: MINHA_CHAVE):", parent=self.wizard)
        if var_name:
            var_name = var_name.strip().replace(" ", "_").upper()
            if var_name in self.env_entries:
                messagebox.showwarning("Aviso", f"A variável '{var_name}' já existe na lista!", parent=self.wizard)
            else:
                self._render_env_row(var_name, "")

    def save_env(self):
        new_values = {}
        for k, (var, _) in self.env_entries.items():
            new_values[k] = var.get().strip()

        written_keys = set()
        new_lines = []

        if os.path.exists(self.wizard.env_path):
            try:
                with open(self.wizard.env_path, "r", encoding="utf-8", errors="replace") as f:
                    for line in f:
                        line_s = line.strip()
                        if "=" in line_s and not line_s.startswith("#"):
                            k = line_s.split("=", 1)[0].strip()
                            if k in new_values:
                                new_lines.append(f"{k}={new_values[k]}\n")
                                written_keys.add(k)
                                continue
                        new_lines.append(line)
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao ler arquivo .env atual: {e}")
                return

        for k, v in new_values.items():
            if k not in written_keys:
                new_lines.append(f"{k}={v}\n")
                written_keys.add(k)

        try:
            os.makedirs(os.path.dirname(self.wizard.env_path), exist_ok=True)
            with open(self.wizard.env_path, "w", encoding="utf-8") as f:
                f.writelines(new_lines)

            for k, v in new_values.items():
                if v:
                    os.environ[k] = v

            if "GITHUB_REPOSITORY" in new_values and new_values["GITHUB_REPOSITORY"]:
                self.wizard.repo_name_var.set(new_values["GITHUB_REPOSITORY"])

            messagebox.showinfo(
                "Sucesso",
                f"Configurações salvas com sucesso no arquivo .env!\n\nArquivo:\n{self.wizard.env_path}"
            )
        except Exception as e:
            messagebox.showerror("Erro ao Salvar", f"Não foi possível gravar no arquivo .env:\n{e}")
