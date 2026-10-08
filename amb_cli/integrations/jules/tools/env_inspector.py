#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
⚡ Jules Tool: env_inspector (SRP)
Localização: amb_cli/integrations/jules/tools/env_inspector.py
Responsabilidade Única: Inspecionar a compatibilidade da stack com a VM do Jules e gerar o script de snapshot.
"""

import os
import json
from typing import Dict, Any, Optional

from core.bootstrap import ensure_amb_env
ensure_amb_env()

from core import Colors, log
from workspace.setup.project_analyzer import ProjectAnalyzer
from workspace.setup.setup_sanitizer import SetupSanitizer


def inspect_jules_env(target_dir: Optional[str] = None) -> Dict[str, Any]:
    """Analisa a stack local e deduz compatibilidade e script para a VM do Google Jules."""
    root = os.path.abspath(target_dir or os.getcwd())
    stack = ProjectAnalyzer.detect_stack(root)
    qa = ProjectAnalyzer.infer_qa_commands(stack, root)
    setup_script_raw = ProjectAnalyzer.infer_setup_script(stack, root)

    setup_script, removed_commands = SetupSanitizer.sanitize_script(setup_script_raw)

    for cmd in removed_commands:
        log("ENV", f"Comando bloqueante ignorado no setup: {cmd}", Colors.YELLOW)

    # Ferramentas nativas garantidas pelo Jules Ubuntu 24.04 VM
    stype = stack.get("type", "").lower()
    native_tools = []
    if "python" in stype:
        native_tools.extend(["Python 3.12.11", "uv 0.7", "poetry 2.1", "pytest 8.4", "ruff", "mypy"])
    if "node" in stype:
        native_tools.extend(["Node.js v22.16", "pnpm 10.12", "yarn 1.22", "bun", "npm 11.4", "chromedriver"])
    if "go" in stype:
        native_tools.append("Go 1.24.3")
    if "rust" in stype:
        native_tools.extend(["Rustc 1.87", "Cargo 1.87"])

    native_tools.extend(["Git 2.49", "Docker 28.2", "ripgrep 14.1", "jq 1.7"])

    return {
        "root": root,
        "stack": stack,
        "qa_commands": qa,
        "setup_script": setup_script,
        "native_vm_tools": native_tools,
        "vm_base_os": "Ubuntu 24.04 LTS",
        "snapshot_recommended": True,
    }


def run_inspect_env(target_dir: Optional[str] = None, as_json: bool = False) -> Dict[str, Any]:
    """Ponto de entrada do comando `amb jules env`."""
    data = inspect_jules_env(target_dir)

    if as_json:
        print(json.dumps(data, indent=2, ensure_ascii=False))
        return data

    root = data["root"]
    stack = data["stack"]
    setup_script = data["setup_script"]
    native_tools = ", ".join(data["native_vm_tools"][:6])

    print(f"\n{Colors.BOLD}{Colors.CYAN}=== ☁️ DIAGNÓSTICO DE AMBIENTE: GOOGLE JULES VM ==={Colors.RESET}\n")
    print(f"  • Diretório Alvo:     {Colors.CYAN}{root}{Colors.RESET}")
    print(f"  • Stack Detectada:    {Colors.GREEN}{stack.get('type')}{Colors.RESET} ({stack.get('primary_language')})")
    print(f"  • SO Base da VM:      {Colors.GREEN}Ubuntu 24.04 LTS (x86_64){Colors.RESET}")
    print(f"  • Ferramentas Nativas: {Colors.BOLD}{native_tools}...{Colors.RESET}")
    print(f"\n{Colors.YELLOW}📋 Script Recomendado para 'Initial Setup' (Run and Snapshot):{Colors.RESET}")
    print(f"{Colors.BOLD}------------------------------------------------------------{Colors.RESET}")
    for line in setup_script.splitlines():
        print(f"  {Colors.GREEN}{line}{Colors.RESET}")
    print(f"{Colors.BOLD}------------------------------------------------------------{Colors.RESET}")
    print(f"\n{Colors.BOLD}💡 Como aplicar no Google Jules:{Colors.RESET}")
    print(f"  1. Acesse o painel web em https://jules.google.com")
    print(f"  2. Selecione o repositório e clique em {Colors.BOLD}Configuration{Colors.RESET} no topo.")
    print(f"  3. Cole as linhas acima no campo {Colors.BOLD}Initial Setup{Colors.RESET}.")
    print(f"  4. Clique em {Colors.BOLD}{Colors.CYAN}Run and Snapshot{Colors.RESET} para validar e congelar a imagem da VM.\n")

    return data
