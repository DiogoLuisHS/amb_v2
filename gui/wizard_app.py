import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import argparse
import subprocess
import os
import sys

# Adiciona o diretório raiz ao sys.path para conseguir importar os parsers
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from cli_modules.cli_parsers import create_parser

class DynamicWizard(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("AMB_V2 - Dynamic Command Wizard")
        self.geometry("800x700")
        self.configure(padx=20, pady=20)
        
        self.result_command = None
        self.param_vars = {}  # Guarda as variáveis do Tkinter para cada ação
        
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

    # =========================================================
    # ABA 1: RUNNER
    # =========================================================
    def _build_runner_tab(self):
        container = ttk.Frame(self.tab_runner, padding=10)
        container.pack(fill="both", expand=True)

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
        container = ttk.Frame(self.tab_settings, padding=20)
        container.pack(fill="both", expand=True)

        ttk.Label(container, text="Parâmetros do Ambiente (.env)", font=("Segoe UI", 12, "bold")).pack(anchor="w", pady=(0, 15))

        self.env_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".env"))
        
        # Define as chaves padrão garantindo que sempre existam na UI
        self.env_vars = {
            "GEMINI_API_KEY": "",
            "JULES_API_KEY": "",
            "STITCH_API_KEY": "",
            "STITCH_PROJECT_ID": "",
            "RENDER_API_KEY": "",
            "GITHUB_REPOSITORY": "",
            "TURSO_DATABASE_URL": "",
            "TURSO_AUTH_TOKEN": "",
        }
        self.env_entries = {}

        # Carregar .env atual e sobrescrever valores
        if os.path.exists(self.env_path):
            with open(self.env_path, "r", encoding="utf-8") as f:
                for line in f:
                    if "=" in line and not line.strip().startswith("#"):
                        k, v = line.split("=", 1)
                        self.env_vars[k.strip()] = v.strip()

        # Cria a UI de entradas
        form_frame = ttk.Frame(container)
        form_frame.pack(fill="both", expand=True)

        for key, val in self.env_vars.items():
            row = ttk.Frame(form_frame)
            row.pack(fill="x", pady=5)
            
            ttk.Label(row, text=key, width=25, font=("Segoe UI", 9, "bold")).pack(side="left")
            str_var = tk.StringVar(value=val)
            # Para senhas/API Keys ocultar os caracteres? Não, o usuário pediu pra poder alterar explícito.
            ttk.Entry(row, textvariable=str_var).pack(side="left", fill="x", expand=True)
            
            self.env_entries[key] = str_var

        # Salvar Botão
        frame_btn = ttk.Frame(container)
        frame_btn.pack(fill="x", pady=(20, 0))
        ttk.Button(frame_btn, text="💾 Salvar Configurações", command=self.save_env).pack(side="right")

    def save_env(self):
        # Atualiza dicionário em memória
        for k, var in self.env_entries.items():
            self.env_vars[k] = var.get().strip()

        # Lê o arquivo original para preservar formatação e comentários
        new_lines = []
        if os.path.exists(self.env_path):
            with open(self.env_path, "r", encoding="utf-8") as f:
                for line in f:
                    if "=" in line and not line.strip().startswith("#"):
                        k = line.split("=", 1)[0].strip()
                        if k in self.env_vars:
                            new_lines.append(f"{k}={self.env_vars[k]}\n")
                            continue
                    new_lines.append(line)
        else:
            for k, v in self.env_vars.items():
                new_lines.append(f"{k}={v}\n")

        with open(self.env_path, "w", encoding="utf-8") as f:
            f.writelines(new_lines)

        messagebox.showinfo("Sucesso", "Configurações de ambiente salvas com sucesso no arquivo .env!")

def start_wizard():
    app = DynamicWizard()
    app.attributes('-topmost', True)
    app.after_idle(app.attributes, '-topmost', False)
    app.mainloop()
    
    if app.result_command:
        print(f"\n⚡ Executando comando gerado pelo Wizard:\n> {app.result_command}\n")
        subprocess.run(app.result_command, shell=True)

if __name__ == "__main__":
    start_wizard()
