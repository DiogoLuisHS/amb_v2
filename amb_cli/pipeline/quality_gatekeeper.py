#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🛡️ AMB_V2 - Quality Gatekeeper (SRP)
Localização: amb_v2/pipeline/quality_gatekeeper.py
Responsabilidade Única: Executar verificações de integridade local (QA: typecheck, test, build, lint),
resolvendo comandos declarados no .amb/amb_project.json ou inferidos automaticamente pela stack.
"""

import os
import sys
import shlex
import shutil
import subprocess
from typing import Optional, Dict, Any

from config.bootstrap import ensure_amb_env
ensure_amb_env()

from config import Colors, log, log_error, find_repo_root, load_project_json
from config.setup_modules.project_analyzer import ProjectAnalyzer


class QualityGatekeeper:
    """Valida a integridade do código localmente com suporte a amb_project.json e ProjectAnalyzer."""

    @classmethod
    def detect_qa_commands(cls, repo_root: Optional[str] = None) -> Dict[str, str]:
        """Recupera comandos de QA do .amb/amb_project.json ou infere via ProjectAnalyzer."""
        root = os.path.abspath(repo_root or find_repo_root())

        # 1. Tenta carregar do amb_project.json
        proj = load_project_json(repo_root=root) or {}
        qa_cfg = proj.get("qa", {})
        if qa_cfg and isinstance(qa_cfg, dict):
            return qa_cfg

        # 2. Fallback determinístico através do ProjectAnalyzer
        try:
            stack = ProjectAnalyzer.detect_stack(root)
            return ProjectAnalyzer.infer_qa_commands(stack, root)
        except Exception:
            return {}

    @classmethod
    def execute_command(cls, cmd_str: str, label: str, cwd: str) -> bool:
        """Executa um comando de QA isolado com tratamento de saída e erros."""
        if not cmd_str or not cmd_str.strip():
            return True

        clean_cmd = cmd_str.strip()
        print(f"\n[{Colors.BOLD}QA:{label.upper()}{Colors.RESET}] {clean_cmd}")

        proc = subprocess.run(
            clean_cmd,
            cwd=cwd,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            shell=True
        )

        if proc.returncode != 0:
            stdout_txt = proc.stdout.strip() if proc.stdout else ""
            stderr_txt = proc.stderr.strip() if proc.stderr else ""
            if stdout_txt:
                print(f"{Colors.DIM}{stdout_txt}{Colors.RESET}")
            if stderr_txt:
                print(f"{Colors.RED}{stderr_txt}{Colors.RESET}")
            log_error("QA", f"Falha no passo de validação: '{label}' (código {proc.returncode})")
            return False

        print(f"{Colors.GREEN}✔ {label}: concluído com sucesso!{Colors.RESET}")
        return True

    @classmethod
    def run_qa(cls, repo_root: Optional[str] = None) -> bool:
        """Executa toda a suíte de QA configurada ou inferida para o repositório."""
        root = os.path.abspath(repo_root or find_repo_root())
        log("QA", f"Executando verificação de integridade local em: {root}", Colors.CYAN)

        qa_commands = cls.detect_qa_commands(root)
        if not qa_commands:
            print(f"{Colors.GREEN}✔ Nenhuma suíte de QA necessária ou detectada para este repositório.{Colors.RESET}")
            return True

        for step_key, step_cmd in qa_commands.items():
            success = cls.execute_command(step_cmd, step_key, cwd=root)
            if not success:
                return False

        print("\n" + "=" * 75)
        print(f"🎉 {Colors.BOLD}{Colors.GREEN}TODOS OS PASSOS DE QA PASSARAM COM SUCESSO!{Colors.RESET}")
        print("=" * 75 + "\n")
        return True


if __name__ == "__main__":
    ok = QualityGatekeeper.run_qa()
    sys.exit(0 if ok else 1)
