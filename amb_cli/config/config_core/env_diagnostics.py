import os
import json
import shutil
from typing import Dict, Any

def run_environment_diagnostics(as_json: bool = False) -> Dict[str, Any]:
    """Valida e exibe o checklist visual de configurações e saúde do repositório ativo."""
    from amb_cli.config.config import find_repo_root, load_project_json, get_env, Colors

    root = find_repo_root()
    p_meta = load_project_json()
    p_json_exists = bool(p_meta)
    env_exists = os.path.exists(os.path.join(root, ".env"))
    gitignore_path = os.path.join(root, ".gitignore")

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

    # 3. Chaves de API
    keys_to_check = [
        ("JULES_API_KEY", "Google Jules SDK / API"),
        ("GEMINI_API_KEY", "Google Antigravity / Gemini"),
        ("STITCH_API_KEY", "Google Stitch SDK"),
        ("STITCH_PROJECT_ID", "Stitch Project ID"),
        ("GITHUB_REPOSITORY", "Repositório GitHub"),
    ]
    keys_status = {}
    for key, desc in keys_to_check:
        val = get_env(key)
        keys_status[key] = {
            "description": desc,
            "configured": bool(val),
            "masked": (val[:4] + "..." + val[-4:] if len(val) > 10 else "***") if val else None
        }

    # 4. QA Commands e binários
    qa_cfg = p_meta.get("qa", {})
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

    # 5. Personas
    personas_dir = os.path.join(root, ".amb", "personas")
    personas_count = len([f for f in os.listdir(personas_dir) if f.endswith(".md")]) if os.path.exists(personas_dir) else 0

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
        "keys": keys_status,
        "qa": qa_status,
        "personas_count": personas_count
    }

    if as_json:
        print(json.dumps(report, indent=2, ensure_ascii=False))
        return report

    # Renderização Visual no Terminal
    print(f"\n{Colors.BOLD}{Colors.CYAN}=== AMB_V2 - DIAGNÓSTICO DE AMBIENTE E SAÚDE DO PROJETO ==={Colors.RESET}\n")
    print(f"📁 Raiz do Projeto: {Colors.BOLD}{root}{Colors.RESET}")
    print(f"📄 Arquivo .env:     {'✅ Encontrado' if env_exists else f'{Colors.YELLOW}⚠️  Não encontrado{Colors.RESET}'}")
    print(f"📄 Config .amb/:    {'✅ amb_project.json ativo' if p_json_exists else f'{Colors.YELLOW}⚠️  Não configurado (rode amb setup){Colors.RESET}'}")

    # Segurança
    if env_exists:
        if env_in_gitignore:
            print(f"🛡️  Segurança:        {Colors.GREEN}✅ .env protegido no .gitignore{Colors.RESET}")
        else:
            print(f"🛡️  Segurança:        {Colors.RED}{Colors.BOLD}🚨 ALERTA: .env NÃO está no .gitignore! Risco de vazamento!{Colors.RESET}")

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

    # Chaves de API
    print(f"\n{Colors.BOLD}🔑 Credenciais e Chaves de API:{Colors.RESET}")
    for key, info in keys_status.items():
        if info["configured"]:
            print(f"  ✅ {info['description']:<30} ({key}): {Colors.GREEN}{info['masked']}{Colors.RESET}")
        else:
            print(f"  ⚠️  {info['description']:<30} ({key}): {Colors.YELLOW}Não configurado{Colors.RESET}")

    # QA
    print(f"\n{Colors.BOLD}🛡️  Suíte de Testes e Validação Local (QA):{Colors.RESET}")
    if qa_status:
        for step, qinfo in qa_status.items():
            status_icon = "✅" if qinfo["available"] else "⚠️ "
            color = Colors.GREEN if qinfo["available"] else Colors.YELLOW
            bin_note = "" if qinfo["available"] else f" ({qinfo['binary']} não encontrado no PATH)"
            print(f"  {status_icon} {step:<12}: {color}{qinfo['command']}{bin_note}{Colors.RESET}")
    else:
        print(f"  {Colors.YELLOW}⚠️  Nenhum comando de QA configurado no amb_project.json{Colors.RESET}")

    # Personas
    print(f"\n{Colors.BOLD}🤖 Inteligência Local & Personas:{Colors.RESET}")
    print(f"  • Personas Ativas: {Colors.GREEN}{personas_count} persona(s) em .amb/personas/{Colors.RESET}")

    print(f"\n{Colors.DIM}Para reconfigurar ou atualizar a stack do projeto: amb setup --force{Colors.RESET}\n")
    return report
