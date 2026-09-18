#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔍 AMB_V2 - Diagnóstico Central de Ambiente e Saúde do Projeto (SRP)
Localização: amb_cli/core/diagnostics.py
Responsabilidade Única: Validar e exibir o checklist visual das credenciais do AMB
e o contexto do workspace do projeto consumidor.
"""

import os
import json
import shutil
from typing import Dict, Any

from amb_cli.core.logger import Colors
from amb_cli.core.env import get_env
from amb_cli.workspace.project_context import find_repo_root, load_project_json
from amb_cli.workspace.setup.project_analyzer import ProjectAnalyzer


def run_environment_diagnostics(as_json: bool = False) -> Dict[str, Any]:
    """Valida e exibe o checklist visual de configurações e saúde do repositório ativo."""
    root = find_repo_root()
    p_meta = load_project_json()
    p_json_exists = bool(p_meta)
    env_exists = os.path.exists(os.path.join(root, ".env"))
    gitignore_path = os.path.join(root, ".gitignore")

    # Stack detection
    stack_info = ProjectAnalyzer.detect_stack(root)

    # 1. Checagem de Git e GitHub CLI
    git_detected = False
    git_branch = None
    git_clean = None
    gh_installed = bool(shutil.which("gh"))
    gh_auth = False

    try:
        from integrations.git.git_service import GitService
        git = GitService(repo_root=root)
        git_branch = git.get_current_branch(cwd=root)
        git_detected = bool(git_branch)
        git_clean = git.is_clean(cwd=root)
        gh_auth = git.check_gh_auth(cwd=root, fail_silently=True)
    except Exception:
        pass

    # 2. Checagem de Segurança (.gitignore)
    env_in_gitignore = False
    if os.path.exists(gitignore_path):
        try:
            with open(gitignore_path, "r", encoding="utf-8", errors="replace") as gf:
                content = gf.read()
                env_in_gitignore = ".env" in content.split() or any(line.strip() == ".env" for line in content.splitlines())
        except Exception:
            pass

    # 3. Credenciais do AMB Framework (Plataforma)
    platform_keys = [
        ("JULES_API_KEY", "Google Jules SDK / API"),
        ("GEMINI_API_KEY", "Google Antigravity / Gemini"),
        ("STITCH_API_KEY", "Google Stitch SDK"),
        ("STITCH_PROJECT_ID", "Stitch Project ID")
    ]
    platform_status = {}
    for key, desc in platform_keys:
        val = get_env(key)
        platform_status[key] = {
            "description": desc,
            "configured": bool(val),
            "masked": (val[:4] + "..." + val[-4:] if len(val) > 10 else "***") if val else None
        }

    # 4. Contexto do Workspace Alvo (Projeto Consumidor)
    workspace_keys = [
        ("GITHUB_REPOSITORY", "Repositório GitHub")
    ]
    workspace_status = {}
    for key, desc in workspace_keys:
        val = get_env(key)
        workspace_status[key] = {
            "description": desc,
            "configured": bool(val),
            "masked": val if val else None
        }

    # 5. QA Commands e binários
    qa_cfg = p_meta.get("qa", {})
    if not qa_cfg:
        qa_cfg = ProjectAnalyzer.infer_qa_commands(stack_info, root)

    qa_status = {}
    for step, cmd in qa_cfg.items():
        parts = cmd.split()
        binary = parts[0] if parts else ""
        bin_found = bool(shutil.which(binary))
        qa_status[step] = {
            "command": cmd,
            "binary": binary,
            "available": bin_found
        }

    # 6. Regras e Personas
    personas_dir = os.path.join(root, ".amb", "personas")
    personas_count = len([f for f in os.listdir(personas_dir) if f.endswith(".md")]) if os.path.exists(personas_dir) else 0
    active_rules_dir = stack_info.get("rules_dir") or ".amb/rules (fallback)"

    report = {
        "root": root,
        "env_file": env_exists,
        "amb_project_json": p_json_exists,
        "env_in_gitignore": env_in_gitignore,
        "git": {
            "detected": git_detected,
            "branch": git_branch,
            "clean": git_clean
        },
        "github_cli": {
            "installed": gh_installed,
            "authenticated": gh_auth
        },
        "platform_keys": platform_status,
        "workspace_keys": workspace_status,
        "stack": stack_info,
        "qa": qa_status,
        "personas_count": personas_count,
        "active_rules_dir": active_rules_dir
    }

    # Compatibilidade com testes antigos: colocar todas as chaves em 'keys'
    report["keys"] = {**platform_status, **workspace_status}

    if as_json:
        print(json.dumps(report, indent=2, ensure_ascii=False))
        return report

    # Renderização Visual no Terminal
    print(f"\n{Colors.BOLD}{Colors.CYAN}=== AMB_V2 - DIAGNÓSTICO DE AMBIENTE E SAÚDE DO PROJETO ==={Colors.RESET}\n")

    # SEÇÃO 1: PLATAFORMA (AMB Framework)
    print(f"{Colors.BOLD}{Colors.BLUE}=== Credenciais do AMB Framework (Plataforma) ==={Colors.RESET}")
    for key, info in platform_status.items():
        if info["configured"]:
            print(f"  ✅ {info['description']:<30} ({key}): {Colors.GREEN}{info['masked']}{Colors.RESET}")
        else:
            print(f"  ⚠️  {info['description']:<30} ({key}): {Colors.YELLOW}Não configurado{Colors.RESET}")

    print(f"\n{Colors.BOLD}{Colors.BLUE}=== Contexto do Workspace Alvo (Projeto Consumidor) ==={Colors.RESET}")
    print(f"📁 Raiz do Projeto: {Colors.BOLD}{root}{Colors.RESET}")
    print(f"📄 Arquivo .env:     {'✅ Encontrado' if env_exists else f'{Colors.YELLOW}⚠️  Não encontrado{Colors.RESET}'}")
    print(f"📄 Config .amb/:    {'✅ amb_project.json ativo' if p_json_exists else f'{Colors.YELLOW}⚠️  Não configurado (rode amb setup){Colors.RESET}'}")

    # Segurança
    if env_exists:
        if env_in_gitignore:
            print(f"🛡️  Segurança:        {Colors.GREEN}✅ .env protegido no .gitignore{Colors.RESET}")
        else:
            print(f"🛡️  Segurança:        {Colors.RED}{Colors.BOLD}🚨 ALERTA: .env NÃO está no .gitignore! Risco de vazamento!{Colors.RESET}")

    # Workspace Chaves
    for key, info in workspace_status.items():
        if info["configured"]:
            print(f"  ✅ {info['description']:<30} ({key}): {Colors.GREEN}{info['masked']}{Colors.RESET}")
        else:
            print(f"  ⚠️  {info['description']:<30} ({key}): {Colors.YELLOW}Não configurado{Colors.RESET}")

    # Git & GitHub
    print(f"\n{Colors.BOLD}🌿 Integração Git & GitHub CLI:{Colors.RESET}")
    if git_detected:
        clean_badge = f"{Colors.GREEN}Working tree limpa{Colors.RESET}" if git_clean else f"{Colors.YELLOW}Modificações pendentes{Colors.RESET}"
        print(f"  • Git Local:       {Colors.GREEN}✅ Branch '{git_branch}' ({clean_badge}){Colors.RESET}")
    else:
        print(f"  • Git Local:       {Colors.YELLOW}⚠️  Repositório Git não detectado{Colors.RESET}")

    if gh_installed:
        if gh_auth:
            print(f"  • GitHub CLI (gh): {Colors.GREEN}✅ Autenticado para Pull Requests{Colors.RESET}")
        else:
            print(f"  • GitHub CLI (gh): {Colors.YELLOW}⚠️  Instalado, mas não autenticado (rode 'gh auth login'){Colors.RESET}")
    else:
        print(f"  • GitHub CLI (gh): {Colors.YELLOW}⚠️  Não instalado (recomendado para automação de PRs){Colors.RESET}")

    # Stack Técnica
    print(f"\n{Colors.BOLD}🛠️  Stack Técnica Detectada:{Colors.RESET}")
    print(f"  • Tipo:            {Colors.GREEN}{stack_info.get('type', 'Desconhecido')}{Colors.RESET}")
    print(f"  • Gerenciador:     {Colors.GREEN}{stack_info.get('package_manager', 'N/A')}{Colors.RESET}")
    fw_list = ", ".join(stack_info.get("frameworks", []))
    print(f"  • Frameworks:      {Colors.GREEN}{fw_list if fw_list else 'Nenhum específico detectado'}{Colors.RESET}")

    # QA
    print(f"\n{Colors.BOLD}🛡️  Suíte de Testes e Validação Local (QA):{Colors.RESET}")
    if qa_status:
        for step, qinfo in qa_status.items():
            status_icon = "✅" if qinfo["available"] else "⚠️ "
            color = Colors.GREEN if qinfo["available"] else Colors.YELLOW
            bin_note = "" if qinfo["available"] else f" ({qinfo['binary']} não encontrado no PATH)"
            print(f"  {status_icon} {step:<12}: {color}{qinfo['command']}{bin_note}{Colors.RESET}")
    else:
        print(f"  {Colors.YELLOW}⚠️  Nenhum comando de QA configurado ou inferido.{Colors.RESET}")

    # Personas e Regras
    print(f"\n{Colors.BOLD}🤖 Inteligência Local & Regras:{Colors.RESET}")
    print(f"  • Personas Ativas: {Colors.GREEN}{personas_count} persona(s) em .amb/personas/{Colors.RESET}")
    print(f"  • Regras Ativas:   {Colors.GREEN}{active_rules_dir}{Colors.RESET}")

    print(f"\n{Colors.DIM}Para reconfigurar ou atualizar a stack do projeto: amb setup --force{Colors.RESET}\n")
    return report
