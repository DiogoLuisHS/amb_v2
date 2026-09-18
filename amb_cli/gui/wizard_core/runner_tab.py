import tkinter as tk
from tkinter import ttk, filedialog
import argparse
from typing import Dict, Any, Callable


class RunnerTab:
    """Manages the Runner Tab for executing CLI commands."""

    def __init__(self, parent_frame: ttk.Frame, wizard: Any):
        self.wizard = wizard
        self.param_vars: Dict[str, Any] = {}
        self.command_map = self.wizard.command_map

        container = ttk.Frame(parent_frame, padding=10)
        container.pack(fill="both", expand=True)

        self._build_project_context(container)
        self._build_command_selection(container)
        self._build_dynamic_params_frame(container)
        self._build_execute_button(container)

    def _build_project_context(self, container: ttk.Frame):
        proj_badge = ttk.Frame(container)
        proj_badge.pack(fill="x", pady=(0, 10))
        ttk.Label(proj_badge, text="Projeto:", font=("Segoe UI", 9, "bold")).pack(side="left")
        ttk.Label(proj_badge, textvariable=self.wizard.repo_name_var, foreground="#0066cc", font=("Segoe UI", 9, "bold")).pack(side="left", padx=(5, 15))
        ttk.Label(proj_badge, text="Diretório:", font=("Segoe UI", 9, "bold")).pack(side="left")
        ttk.Label(proj_badge, textvariable=self.wizard.project_root_var, foreground="#555555", font=("Segoe UI", 9)).pack(side="left", padx=(5, 0))

    def _build_command_selection(self, container: ttk.Frame):
        frame_cmd = ttk.Frame(container)
        frame_cmd.pack(fill="x", pady=(0, 5))
        ttk.Label(frame_cmd, text="1. Selecione o Comando:", font=("Segoe UI", 10, "bold")).pack(side="left")

        self.selected_cmd = tk.StringVar()
        cmd_choices = list(self.command_map.keys())
        self.cb_cmd = ttk.Combobox(frame_cmd, textvariable=self.selected_cmd, values=cmd_choices, state="readonly", width=40)
        self.cb_cmd.pack(side="left", padx=10)
        self.cb_cmd.bind("<<ComboboxSelected>>", self.on_command_select)

        self.cmd_desc_var = tk.StringVar(value="Selecione um comando para ver os detalhes.")
        lbl_desc = ttk.Label(container, textvariable=self.cmd_desc_var, foreground="gray", wraplength=700)
        lbl_desc.pack(anchor="w", pady=(0, 15))

        if "pipeline" in cmd_choices:
            self.cb_cmd.set("pipeline")
        elif cmd_choices:
            self.cb_cmd.set(cmd_choices[0])

    def _build_dynamic_params_frame(self, container: ttk.Frame):
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

    def _build_execute_button(self, container: ttk.Frame):
        frame_btn = ttk.Frame(container)
        frame_btn.pack(fill="x", pady=(15, 0))
        ttk.Button(frame_btn, text="Executar no Terminal", command=self.wizard.execute_cmd).pack(side="right")

    def on_command_select(self, event: Any):
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        self.param_vars.clear()

        cmd_name = self.selected_cmd.get()
        if not cmd_name or cmd_name not in self.command_map:
            return

        data = self.command_map[cmd_name]
        subparser = data["parser"]
        help_text = data["help"]

        self.cmd_desc_var.set(help_text if help_text else f"Executa a operação '{cmd_name}'.")

        for action in subparser._actions:
            if action.dest == "help" or isinstance(action, argparse._HelpAction):
                continue
            if isinstance(action, argparse._SubParsersAction):
                continue

            self._render_action(action)

    def _render_action(self, action: argparse.Action):
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

    def _browse(self, var: tk.StringVar):
        path = filedialog.askopenfilename()
        if path:
            var.set(path)

    def build_command_string(self) -> str:
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

        return " ".join(cmd)
