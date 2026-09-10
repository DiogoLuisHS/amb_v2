import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
import argparse
import subprocess
import os
import sys

# Adiciona o diretório raiz ao sys.path para conseguir importar os parsers
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from cli_modules.cli_parsers import create_parser
try:
    from config import find_repo_root, get_repo_name
except ImportError:
    from config.config import find_repo_root, get_repo_name

class DynamicWizard(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("AMB_V2 - Dynamic Command Wizard")
        self.geometry("850x720")
        self.configure(padx=20, pady=20)
        
        self.result_command = None
        self.param_vars = {}  # Guarda as variáveis do Tkinter para cada ação
        
        # Identifica a raiz do projeto e arquivo .env de onde o comando foi invocado
        self.project_root = find_repo_root()
        self.env_path = os.path.join(self.project_root, ".env")
        self.env_entries = {}

        self.repo_name_var = tk.StringVar(value=self._detect_repo_name())
        self.project_root_var = tk.StringVar(value=self.project_root)
        self.env_path_var = tk.StringVar(value=self.env_path)
        
        # Parse tree
        self.parser = create_parser()
        self.command_map = self._extract_commands(self.parser)
        
        # Remover aliases duplicados para deixar a lista limpa
        seen_parsers = set()
        clean_command_map = {}
        for cmd_name, data in self.command_map.items():
            sub_p = data["parser"]
            if sub_p not in seen_parsers:
                clean_command_map[cmd_name] = data
                seen_parsers.add(sub_p)
        self.command_map = clean_command_map

        # Título
        ttk.Label(self, text="⚡ AMB_V2 Command Wizard", font=("Segoe UI", 16, "bold")).pack(anchor="w", pady=(0, 10))

        # Notebook (Abas)
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True)

        self.tab_runner = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_runner, text="Runner")

        self.tab_settings = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_settings, text="Configurações")

        self._build_runner_tab()
        self._build_settings_tab()

    def _detect_repo_name(self):
        """Detecta o nome do repositório/projeto a partir do .env ou raiz."""
        if os.path.exists(self.env_path):
            try:
                with open(self.env_path, "r", encoding="utf-8", errors="replace") as f:
                    for line in f:
                        line_s = line.strip()
                        if line_s.startswith("GITHUB_REPOSITORY=") and not line_s.startswith("#"):
                            val = line_s.split("=", 1)[1].strip()
                            if val:
                                return val
            except Exception:
                pass
        try:
            repo = get_repo_name()
            if repo:
                return repo
        except Exception:
            pass
        return os.path.basename(self.project_root)

    # =========================================================
    # ABA 1: RUNNER
    # =========================================================
    def _build_runner_tab(self):
        container = ttk.Frame(self.tab_runner, padding=10)
        container.pack(fill="both", expand=True)

        # Contexto do Projeto no Runner
        proj_badge = ttk.Frame(container)
        proj_badge.pack(fill="x", pady=(0, 10))
        ttk.Label(proj_badge, text="Projeto:", font=("Segoe UI", 9, "bold")).pack(side="left")
        ttk.Label(proj_badge, textvariable=self.repo_name_var, foreground="#0066cc", font=("Segoe UI", 9, "bold")).pack(side="left", padx=(5, 15))
        ttk.Label(proj_badge, text="Diretório:", font=("Segoe UI", 9, "bold")).pack(side="left")
        ttk.Label(proj_badge, textvariable=self.project_root_var, foreground="#555555", font=("Segoe UI", 9)).pack(side="left", padx=(5, 0))

        # Seleção de Comando
        frame_cmd = ttk.Frame(container)
        frame_cmd.pack(fill="x", pady=(0, 5))
        ttk.Label(frame_cmd, text="1. Selecione o Comando:", font=("Segoe UI", 10, "bold")).pack(side="left")
        
        self.selected_cmd = tk.StringVar()
        cmd_choices = list(self.command_map.keys())
        self.cb_cmd = ttk.Combobox(frame_cmd, textvariable=self.selected_cmd, values=cmd_choices, state="readonly", width=40)
        self.cb_cmd.pack(side="left", padx=10)
        self.cb_cmd.bind("<<ComboboxSelected>>", self.on_command_select)
        
        # Resumo Dinâmico do Comando
        self.cmd_desc_var = tk.StringVar(value="Selecione um comando para ver os detalhes.")
        lbl_desc = ttk.Label(container, textvariable=self.cmd_desc_var, foreground="gray", wraplength=700)
        lbl_desc.pack(anchor="w", pady=(0, 15))

        if "pipeline" in cmd_choices:
            self.cb_cmd.set("pipeline")
        elif cmd_choices:
            self.cb_cmd.set(cmd_choices[0])

        # Frame dinâmico para os parâmetros
        ttk.Label(container, text="2. Parâmetros Disponíveis:", font=("Segoe UI", 10, "bold")).pack(anchor="w", pady=(10, 5))
        
        self.canvas = tk.Canvas(container, highlightthickness=0)
        scrollbar = ttk.Scrollbar(container, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)
        
        self.canvas.pack(side="top", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        if self.selected_cmd.get():
            self.on_command_select(None)

        # Botão Executar
        frame_btn = ttk.Frame(container)
        frame_btn.pack(fill="x", pady=(15, 0))
        ttk.Button(frame_btn, text="Executar no Terminal", command=self.execute_cmd).pack(side="right")

    def _extract_commands(self, parser, prefix=""):
        commands = {}
        for action in parser._actions:
            if isinstance(action, argparse._SubParsersAction):
                # Extrai o texto de 'help' (que não tem ANSI) do choice_action correspondente
                help_map = {choice.dest: choice.help for choice in action._choices_actions}
                
                for cmd_name, subparser in action.choices.items():
                    full_cmd = f"{prefix} {cmd_name}".strip()
                    help_text = help_map.get(cmd_name, "")
                    commands[full_cmd] = {"parser": subparser, "help": help_text}
                    commands.update(self._extract_commands(subparser, full_cmd))
        return commands

    def on_command_select(self, event):
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        self.param_vars.clear()
        
        cmd_name = self.selected_cmd.get()
        if not cmd_name or cmd_name not in self.command_map:
            return
            
        data = self.command_map[cmd_name]
        subparser = data["parser"]
        help_text = data["help"]
        
        # Atualiza a descrição com o texto de ajuda limpo
        self.cmd_desc_var.set(help_text if help_text else f"Executa a operação '{cmd_name}'.")

        for action in subparser._actions:
            if action.dest == "help" or isinstance(action, argparse._HelpAction):
                continue
            if isinstance(action, argparse._SubParsersAction):
                continue
                
            self._render_action(action)

    def _render_action(self, action):
        frame = ttk.Frame(self.scrollable_frame)
        frame.pack(fill="x", pady=5, padx=5)
        
        is_flag = isinstance(action, (argparse._StoreTrueAction, argparse._StoreFalseAction))
        is_positional = not action.option_strings
        is_required = action.required or is_positional
        
        name_label = action.option_strings[0] if action.option_strings else action.dest
        help_text = action.help or ""
        
        if is_flag:
            var = tk.BooleanVar(value=False)
            self.param_vars[action.dest] = {"type": "flag", "var": var, "opts": action.option_strings}
            ttk.Checkbutton(frame, text=f"{name_label} ({help_text})", variable=var).pack(anchor="w")
            
        elif is_positional or is_required:
            ttk.Label(frame, text=f"{name_label} [Obrigatório]: ", font=("Segoe UI", 9, "bold")).pack(side="left")
            var = tk.StringVar(value=action.default if action.default else "")
            self.param_vars[action.dest] = {"type": "val", "var": var, "opts": [], "required": True}
            
            if action.choices:
                ttk.Combobox(frame, textvariable=var, values=list(action.choices), state="readonly").pack(side="left", fill="x", expand=True)
            else:
                ttk.Entry(frame, textvariable=var).pack(side="left", fill="x", expand=True)
            ttk.Label(frame, text=f"  ℹ {help_text}", foreground="gray").pack(side="left")
            
        else:
            use_var = tk.BooleanVar(value=False)
            val_var = tk.StringVar(value=action.default if action.default else "")
            self.param_vars[action.dest] = {"type": "opt_val", "use_var": use_var, "val_var": val_var, "opts": action.option_strings}
            
            chk = ttk.Checkbutton(frame, text=f"{name_label}", variable=use_var)
            chk.pack(side="left")
            
            if action.choices:
                inp = ttk.Combobox(frame, textvariable=val_var, values=list(action.choices), state="disabled")
            else:
                inp = ttk.Entry(frame, textvariable=val_var, state="disabled")
            inp.pack(side="left", fill="x", expand=True, padx=5)
            
            if "arquivo" in help_text.lower() or "caminho" in help_text.lower() or "file" in help_text.lower() or "prompt" in help_text.lower():
                btn = ttk.Button(frame, text="Browse...", state="disabled", command=lambda v=val_var: self._browse(v))
                btn.pack(side="left", padx=2)
                
                def toggle(u=use_var, i=inp, b=btn):
                    st = "normal" if u.get() else "disabled"
                    st_cb = "readonly" if u.get() and isinstance(i, ttk.Combobox) else st
                    i.config(state=st_cb)
                    b.config(state=st)
                    if u.get(): i.focus()
                chk.config(command=toggle)
            else:
                def toggle(u=use_var, i=inp):
                    st = "normal" if u.get() else "disabled"
                    st_cb = "readonly" if u.get() and isinstance(i, ttk.Combobox) else st
                    i.config(state=st_cb)
                    if u.get(): i.focus()
                chk.config(command=toggle)

            ttk.Label(frame, text=f"  ℹ {help_text}", foreground="gray", wraplength=400).pack(side="left")

    def _browse(self, var):
        path = filedialog.askopenfilename()
        if path:
            var.set(path)

    def execute_cmd(self):
        cmd = ["amb"] + self.selected_cmd.get().split()
        
        for dest, data in self.param_vars.items():
            t = data["type"]
            if t == "flag":
                if data["var"].get() and data["opts"]:
                    cmd.append(data["opts"][0])
            elif t == "val":
                v = data["var"].get().strip()
                if v:
                    cmd.append(f'"{v}"')
            elif t == "opt_val":
                if data["use_var"].get():
                    v = data["val_var"].get().strip()
                    if v and data["opts"]:
                        cmd.append(data["opts"][0])
                        cmd.append(f'"{v}"')
                        
        self.result_command = " ".join(cmd)
        self.destroy()

    # =========================================================
    # ABA 2: SETTINGS (.env)
    # =========================================================
    def _build_settings_tab(self):
        container = ttk.Frame(self.tab_settings, padding=15)
        container.pack(fill="both", expand=True)

        # Header do Projeto Ativo
        header_frame = ttk.LabelFrame(container, text="Contexto do Projeto Ativo", padding=10)
        header_frame.pack(fill="x", pady=(0, 10))

        # Linha 1: Nome do Repositório e botão de trocar pasta
        row_top = ttk.Frame(header_frame)
        row_top.pack(fill="x", pady=2)
        ttk.Label(row_top, text="Repositório:", font=("Segoe UI", 9, "bold"), width=15).pack(side="left")
        ttk.Label(row_top, textvariable=self.repo_name_var, font=("Segoe UI", 9, "bold"), foreground="#0066cc").pack(side="left")
        ttk.Button(row_top, text="📁 Trocar Pasta do Projeto...", command=self._choose_project_dir).pack(side="right")

        # Linha 2: Diretório do Projeto
        row_dir = ttk.Frame(header_frame)
        row_dir.pack(fill="x", pady=2)
        ttk.Label(row_dir, text="Diretório:", font=("Segoe UI", 9, "bold"), width=15).pack(side="left")
        ttk.Label(row_dir, textvariable=self.project_root_var, wraplength=600).pack(side="left")

        # Linha 3: Arquivo .env
        row_env = ttk.Frame(header_frame)
        row_env.pack(fill="x", pady=2)
        ttk.Label(row_env, text="Arquivo .env:", font=("Segoe UI", 9, "bold"), width=15).pack(side="left")
        ttk.Label(row_env, textvariable=self.env_path_var, foreground="#555555", wraplength=600).pack(side="left")

        # Canvas Scrollável para os parâmetros do .env
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

        # Carrega os campos da pasta atual
        self._load_env_fields()

        # Botões de Ação
        btn_bar = ttk.Frame(container)
        btn_bar.pack(fill="x", pady=(10, 0))

        ttk.Button(btn_bar, text="➕ Adicionar Variável", command=self._add_custom_env_var).pack(side="left")
        ttk.Button(btn_bar, text="🔄 Recarregar", command=self._load_env_fields).pack(side="left", padx=5)
        ttk.Button(btn_bar, text="💾 Salvar Configurações no .env", command=self.save_env).pack(side="right")

    def _choose_project_dir(self):
        chosen = filedialog.askdirectory(initialdir=self.project_root, title="Selecione a Pasta do Projeto")
        if chosen:
            self.project_root = os.path.abspath(chosen)
            self.env_path = os.path.join(self.project_root, ".env")
            self.project_root_var.set(self.project_root)
            self.env_path_var.set(self.env_path)
            self.repo_name_var.set(self._detect_repo_name())
            self._load_env_fields()

    def _load_env_fields(self):
        # Limpa widgets existentes
        for child in self.env_scrollable_frame.winfo_children():
            child.destroy()

        self.env_entries.clear()

        # Dicionário com chaves ordenadas
        env_data = {}

        # 1. Carrega o .env do projeto atual se existir
        if os.path.exists(self.env_path):
            try:
                with open(self.env_path, "r", encoding="utf-8", errors="replace") as f:
                    for line in f:
                        line_s = line.strip()
                        if "=" in line_s and not line_s.startswith("#"):
                            k, v = line_s.split("=", 1)
                            env_data[k.strip()] = v.strip()
            except Exception as e:
                messagebox.showwarning("Aviso", f"Erro ao ler .env do projeto: {e}")

        # 2. Garante que as chaves essenciais sempre estejam visíveis mesmo se ausentes no .env
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
            "RENDER_API_KEY",
        ]
        for ck in core_keys:
            if ck not in env_data:
                env_data[ck] = ""

        # Renderiza cada variável
        for key, val in env_data.items():
            self._render_env_row(key, val)

    def _render_env_row(self, key, val):
        row = ttk.Frame(self.env_scrollable_frame)
        row.pack(fill="x", pady=4, padx=5)

        lbl = ttk.Label(row, text=key, width=25, font=("Segoe UI", 9, "bold"), anchor="w")
        lbl.pack(side="left")

        val_var = tk.StringVar(value=val)
        entry = ttk.Entry(row, textvariable=val_var)
        entry.pack(side="left", fill="x", expand=True, padx=(5, 5))

        self.env_entries[key] = (val_var, row)

    def _add_custom_env_var(self):
        var_name = simpledialog.askstring("Nova Variável", "Nome da variável de ambiente (ex: MINHA_CHAVE):", parent=self)
        if var_name:
            var_name = var_name.strip().replace(" ", "_").upper()
            if var_name in self.env_entries:
                messagebox.showwarning("Aviso", f"A variável '{var_name}' já existe na lista!", parent=self)
            else:
                self._render_env_row(var_name, "")

    def save_env(self):
        # Mapeia os novos valores
        new_values = {}
        for k, (var, _) in self.env_entries.items():
            new_values[k] = var.get().strip()

        written_keys = set()
        new_lines = []

        if os.path.exists(self.env_path):
            try:
                with open(self.env_path, "r", encoding="utf-8", errors="replace") as f:
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

        # Adiciona quaisquer chaves que ainda não existiam no arquivo
        for k, v in new_values.items():
            if k not in written_keys:
                new_lines.append(f"{k}={v}\n")
                written_keys.add(k)

        try:
            os.makedirs(os.path.dirname(self.env_path), exist_ok=True)
            with open(self.env_path, "w", encoding="utf-8") as f:
                f.writelines(new_lines)

            # Atualiza variáveis no ambiente de processo
            for k, v in new_values.items():
                if v:
                    os.environ[k] = v

            # Atualiza o nome do repositório exibido caso tenha sido modificado
            if "GITHUB_REPOSITORY" in new_values and new_values["GITHUB_REPOSITORY"]:
                self.repo_name_var.set(new_values["GITHUB_REPOSITORY"])

            messagebox.showinfo(
                "Sucesso",
                f"Configurações salvas com sucesso no arquivo .env!\n\nArquivo:\n{self.env_path}"
            )
        except Exception as e:
            messagebox.showerror("Erro ao Salvar", f"Não foi possível gravar no arquivo .env:\n{e}")

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
