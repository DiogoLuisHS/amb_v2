import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import subprocess
import sys

class AmbWizard(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("AMB_V2 - Assistente de Comandos")
        self.geometry("600x550")
        self.configure(padx=20, pady=20)
        
        self.result_command = None

        # Título Principal
        lbl_title = ttk.Label(self, text="⚡ AMB_V2 Wizard", font=("Segoe UI", 16, "bold"))
        lbl_title.pack(anchor="w", pady=(0, 15))

        # Abaixo, criamos um Frame para o Pipeline, já que é o foco principal
        frame_pipe = ttk.LabelFrame(self, text=" Pipeline de Integração (Stitch + Jules) ", padding=15)
        frame_pipe.pack(fill="both", expand=True)

        # Seleção de Arquivos MD
        ttk.Label(frame_pipe, text="1. Arquivos de Especificação", font=("Segoe UI", 10, "bold")).pack(anchor="w", pady=(0, 5))
        
        # Stitch
        frame_s = ttk.Frame(frame_pipe)
        frame_s.pack(fill="x", pady=2)
        ttk.Label(frame_s, text="Stitch Prompt (.md):", width=20).pack(side="left")
        self.stitch_path = tk.StringVar()
        ttk.Entry(frame_s, textvariable=self.stitch_path).pack(side="left", fill="x", expand=True, padx=5)
        ttk.Button(frame_s, text="Browse...", command=lambda: self.browse_file(self.stitch_path)).pack(side="left")

        # Jules
        frame_j = ttk.Frame(frame_pipe)
        frame_j.pack(fill="x", pady=2)
        ttk.Label(frame_j, text="Jules Prompt (.md):", width=20).pack(side="left")
        self.jules_path = tk.StringVar()
        ttk.Entry(frame_j, textvariable=self.jules_path).pack(side="left", fill="x", expand=True, padx=5)
        ttk.Button(frame_j, text="Browse...", command=lambda: self.browse_file(self.jules_path)).pack(side="left")

        # Divisor
        ttk.Separator(frame_pipe, orient="horizontal").pack(fill="x", pady=15)

        # Flags Booleanas
        ttk.Label(frame_pipe, text="2. Opções de Execução", font=("Segoe UI", 10, "bold")).pack(anchor="w", pady=(0, 5))
        
        self.skip_stitch = tk.BooleanVar()
        ttk.Checkbutton(frame_pipe, text="--skip-stitch (Pular etapa visual)", variable=self.skip_stitch).pack(anchor="w")

        self.no_qa = tk.BooleanVar()
        ttk.Checkbutton(frame_pipe, text="--no-qa (Desabilitar validação local)", variable=self.no_qa).pack(anchor="w")

        self.auto_appr = tk.BooleanVar()
        ttk.Checkbutton(frame_pipe, text="--auto-approve (Aprovação automática Jules)", variable=self.auto_appr).pack(anchor="w")

        self.sync_ds = tk.BooleanVar()
        ttk.Checkbutton(frame_pipe, text="--sync-ds (Sincronizar Design Tokens antes)", variable=self.sync_ds).pack(anchor="w")

        # Divisor
        ttk.Separator(frame_pipe, orient="horizontal").pack(fill="x", pady=15)

        # Inputs Dinâmicos
        ttk.Label(frame_pipe, text="3. Parâmetros Específicos", font=("Segoe UI", 10, "bold")).pack(anchor="w", pady=(0, 5))

        # Resume Session
        frame_res = ttk.Frame(frame_pipe)
        frame_res.pack(fill="x", pady=2)
        self.use_resume = tk.BooleanVar()
        chk_res = ttk.Checkbutton(frame_res, text="--resume-session", variable=self.use_resume, command=self.toggle_resume)
        chk_res.pack(side="left")
        self.resume_val = tk.StringVar()
        self.entry_res = ttk.Entry(frame_res, textvariable=self.resume_val, state="disabled")
        self.entry_res.pack(side="left", fill="x", expand=True, padx=5)

        # Device
        frame_dev = ttk.Frame(frame_pipe)
        frame_dev.pack(fill="x", pady=2)
        ttk.Label(frame_dev, text="--device:").pack(side="left", padx=(0, 10))
        self.device_val = tk.StringVar(value="DESKTOP")
        ttk.Combobox(frame_dev, textvariable=self.device_val, values=["DESKTOP", "MOBILE", "TABLET"], state="readonly", width=15).pack(side="left")

        # Botão Inferior
        frame_btn = ttk.Frame(self)
        frame_btn.pack(fill="x", pady=(15, 0))
        ttk.Button(frame_btn, text="Executar no Terminal", command=self.execute_cmd).pack(side="right")

    def browse_file(self, string_var):
        path = filedialog.askopenfilename(filetypes=[("Markdown Files", "*.md"), ("All Files", "*.*")])
        if path:
            string_var.set(path)

    def toggle_resume(self):
        if self.use_resume.get():
            self.entry_res.config(state="normal")
            self.entry_res.focus()
        else:
            self.entry_res.config(state="disabled")
            self.resume_val.set("")

    def execute_cmd(self):
        cmd = ["amb", "pipeline"]
        
        if self.stitch_path.get():
            cmd.extend(["--stitch-prompt", f'"{self.stitch_path.get()}"'])
        
        if self.jules_path.get():
            cmd.extend(["--jules-prompt", f'"{self.jules_path.get()}"'])
            
        if self.skip_stitch.get():
            cmd.append("--skip-stitch")
        if self.no_qa.get():
            cmd.append("--no-qa")
        if self.auto_appr.get():
            cmd.append("--auto-approve")
        if self.sync_ds.get():
            cmd.append("--sync-ds")
            
        if self.use_resume.get() and self.resume_val.get().strip():
            cmd.extend(["--resume-session", self.resume_val.get().strip()])
            
        if self.device_val.get() and self.device_val.get() != "DESKTOP":
            cmd.extend(["--device", self.device_val.get()])

        self.result_command = " ".join(cmd)
        self.destroy()

def start_wizard():
    app = AmbWizard()
    # Traz a janela para frente
    app.attributes('-topmost', True)
    app.after_idle(app.attributes, '-topmost', False)
    app.mainloop()
    
    if app.result_command:
        print(f"\n⚡ Executando comando gerado pelo Wizard:\n> {app.result_command}\n")
        # Roda o comando diretamente no terminal ativo
        subprocess.run(app.result_command, shell=True)

if __name__ == "__main__":
    start_wizard()
