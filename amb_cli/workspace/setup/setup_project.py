#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AMB_V2 - Assistente Inteligente de Setup de Projetos (SRP Orquestrador).
Responsabilidade: Orquestrar a execução do setup invocando os submódulos
especializados (ProjectAnalyzer, AmbProvisioner, CognitiveSynthesizer).
"""

import os
import sys
import json
from datetime import datetime
from typing import Optional, Dict, Any

from core.bootstrap import ensure_amb_env
ensure_amb_env()

from core import Colors, log, log_error, get_env
from integrations.git.git_service import GitService
from .project_analyzer import ProjectAnalyzer
from .amb_provisioner import AmbProvisioner


def run_setup(
    interactive: bool = True,
    target_dir: Optional[str] = None,
    force: bool = False,
    dry_run: bool = False
) -> Dict[str, Any]:
    """Executa o fluxo completo de setup, provisiona .amb/ e salva as configurações."""
    # 1. Determina a raiz alvo de forma determinística (diretório atual ou especificado)
    root = os.path.abspath(target_dir or os.getcwd())
    log("SETUP", f"Iniciando análise do projeto em: {root}", Colors.CYAN)

    # 2. Análise Estrutural e Git
    detected_repo = ProjectAnalyzer.detect_git_repo(root)
    stack = ProjectAnalyzer.detect_stack(root)
    qa_commands = ProjectAnalyzer.infer_qa_commands(stack, root)

    try:
        current_branch = GitService(repo_root=root).get_current_branch(cwd=root) or "main"
    except Exception:
        current_branch = "main"

    print(f"\n{Colors.BOLD}🔍 Resultados da Auto-Detecção:{Colors.RESET}")
    print(f"  • Diretório Alvo:     {Colors.CYAN}{root}{Colors.RESET}")
    print(f"  • Repositório Git:    {Colors.GREEN}{detected_repo or 'Não detectado'}{Colors.RESET}")
    print(f"  • Branch Atual:       {Colors.GREEN}{current_branch}{Colors.RESET}")
    print(f"  • Tipo de Projeto:    {Colors.GREEN}{stack.get('type')}{Colors.RESET}")
    print(f"  • Linguagem Primária: {Colors.GREEN}{stack.get('primary_language')}{Colors.RESET}")
    print(f"  • Gerenciador:        {Colors.GREEN}{stack.get('package_manager')}{Colors.RESET}")
    print(f"  • Frameworks:         {Colors.GREEN}{', '.join(stack.get('frameworks', [])) or 'Genérico'}{Colors.RESET}")
    print(f"  • Pasta de Regras:    {Colors.GREEN}{stack.get('rules_dir') or 'Nenhuma detectada'}{Colors.RESET}")
    print(f"  • Comandos de QA:     {Colors.GREEN}{json.dumps(qa_commands, ensure_ascii=False)}{Colors.RESET}\n")

    current_repo = get_env("GITHUB_REPOSITORY", detected_repo or os.path.basename(root))
    current_stitch_id = get_env("STITCH_PROJECT_ID", "")

    # 3. Interatividade (se solicitado e não for dry-run)
    if interactive and not dry_run:
        print(f"{Colors.YELLOW}Configuração de Metadados (pressione ENTER para manter o valor sugerido):{Colors.RESET}")

        in_repo = input(f"👉 Repositório GitHub (ex: owner/repo) [{current_repo}]: ").strip()
        if in_repo:
            current_repo = in_repo

        in_stitch = input(f"👉 Stitch Project ID (opcional) [{current_stitch_id}]: ").strip()
        if in_stitch:
            current_stitch_id = in_stitch

        print(f"\n{Colors.YELLOW}Configuração dos Comandos de QA:{Colors.RESET}")
        for step in ["typecheck", "test", "build", "lint"]:
            current_val = qa_commands.get(step, "")
            prompt_label = f"👉 Comando de '{step}' [{current_val}]: "
            in_cmd = input(prompt_label).strip()
            if in_cmd:
                qa_commands[step] = in_cmd
            elif not current_val and not in_cmd:
                # Remove se estava vazio
                qa_commands.pop(step, None)

    # 4. Modo Simulação (Dry-Run)
    if dry_run:
        preview_data = {
            "$schema": "https://amb-v2.dev/schemas/amb_project.v2.json",
            "version": "2.0.0",
            "name": os.path.basename(root),
            "repository": current_repo,
            "default_branch": current_branch,
            "stitch_project_id": current_stitch_id,
            "stack": stack,
            "qa": qa_commands,
            "personas": {
                "active": ["engineer"],
                "custom_dir": None
            }
        }
        print(f"{Colors.BOLD}{Colors.YELLOW}🔍 MODO SIMULAÇÃO (DRY-RUN) — Nenhuma alteração foi feita no disco:{Colors.RESET}")
        print(json.dumps(preview_data, indent=2, ensure_ascii=False))
        return preview_data

    # 5. Provisionamento da Estrutura .amb/ e Persona Genérica
    log("SETUP", "Provisionando estrutura .amb/, persona e segurança...", Colors.CYAN)
    AmbProvisioner.provision_structure(
        root=root,
        stack=stack,
        repo_name=current_repo or os.path.basename(root),
        qa_commands=qa_commands,
        force=force
    )

    # 6. Salvar amb_project.json com schema v2 completo
    project_data = {
        "$schema": "https://amb-v2.dev/schemas/amb_project.v2.json",
        "version": "2.0.0",
        "name": os.path.basename(root),
        "repository": current_repo,
        "default_branch": current_branch,
        "stitch_project_id": current_stitch_id,
        "stack": stack,
        "qa": qa_commands,
        "personas": {
            "active": ["engineer"],
            "custom_dir": None
        },
        "created_at": datetime.now().isoformat()
    }

    out_dir = os.path.join(root, ".amb")
    os.makedirs(out_dir, exist_ok=True)
    out_json = os.path.join(out_dir, "amb_project.json")
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(project_data, f, indent=2, ensure_ascii=False)

    log("SETUP", f"✅ Arquivo de configuração salvo em: {out_json}", Colors.GREEN)

    # 7. Atualizar .env com valores mínimos de projeto
    env_path = os.path.join(root, ".env")
    env_updates = {}
    if current_repo:
        env_updates["GITHUB_REPOSITORY"] = current_repo
    if current_stitch_id:
        env_updates["STITCH_PROJECT_ID"] = current_stitch_id

    if env_updates:
        if not os.path.exists(env_path):
            with open(env_path, "w", encoding="utf-8") as f:
                f.write("# AMB_V2 - Variáveis de Ambiente do Projeto\n")
                for k, v in env_updates.items():
                    f.write(f"{k}={v}\n")
            log("SETUP", f"✅ Arquivo .env criado em: {env_path}", Colors.GREEN)
        else:
            try:
                with open(env_path, "r", encoding="utf-8") as f:
                    lines = f.readlines()

                existing_keys = set()
                new_lines = []
                for line in lines:
                    env_key: Optional[str] = line.split("=")[0].strip() if "=" in line else None
                    if env_key and env_key in env_updates:
                        new_lines.append(f"{env_key}={env_updates[env_key]}\n")
                        existing_keys.add(env_key)
                    else:
                        new_lines.append(line)

                for k, v in env_updates.items():
                    if k not in existing_keys:
                        new_lines.append(f"{k}={v}\n")

                with open(env_path, "w", encoding="utf-8") as f:
                    f.writelines(new_lines)
                log("SETUP", "✅ Arquivo .env atualizado com as chaves do projeto.", Colors.GREEN)
            except Exception as e:
                log_error("SETUP", f"Não foi possível atualizar .env: {e}")

    print(f"\n{Colors.BOLD}{Colors.GREEN}🎉 Setup do Projeto Concluído com Sucesso!{Colors.RESET}")
    print(f"📁 Raiz do Projeto:   {root}")
    print(f"📄 Configuração:      {out_json}")
    print(f"🤖 Persona Ativa:     .amb/personas/engineer.md")
    print(f"🛡️  Comandos de QA:    {', '.join([f'{k}: {v}' for k, v in qa_commands.items()]) or 'Nenhum'}")
    print(f"\n👉 Próximos passos recomendados:")
    print(f"   • Validar ambiente:         {Colors.CYAN}amb check{Colors.RESET}")
    print(f"   • Executar agente autônomo: {Colors.CYAN}amb agent --role engineer{Colors.RESET}")
    print(f"   • Desenvolver por lote/dir: {Colors.CYAN}amb agent -p .amb/prompts/{Colors.RESET}")
    print(f"   • Iniciar sentinela:        {Colors.CYAN}amb monitor{Colors.RESET}\n")

    return project_data


def print_setup_prompt() -> None:
    """Exibe o Prompt Mestre de Auto-Configuração de IA para novos projetos."""
    prompt_text = """# 🚀 PROMPT DE AUTO-CONFIGURAÇÃO DO AMB_V2

Missão: Configuração e Ativação do Ecossistema AMB_V2 no Projeto Atual.

Você deve analisar este repositório e configurar o ecossistema de automação amb_v2 de forma 100% compatível, genérica e sem falhas.

---

### 📋 Passos Obrigatórios de Execução:

1. Inspeção e Detecção da Stack:
   - Inspecione a raiz do projeto (package.json, bun.lock, pnpm-lock.yaml, pyproject.toml, go.mod, Cargo.toml).
   - Identifique o repositório remoto (owner/repo), stack técnica e comandos de teste/build.

2. Execução do Setup Automático:
   - Execute o setup com inferência de QA e provisionamento de personas:
     amb setup --auto

3. Validação do Checklist de Ambiente:
   - Execute a validação completa de saúde:
     amb check
"""
    print("PROMPT MESTRE DE AUTO-CONFIGURAÇÃO PARA IA:\n")
    print(prompt_text)


def main() -> None:
    import argparse
    parser = argparse.ArgumentParser(description="Assistente de Setup AMB_V2.")
    parser.add_argument("--auto", action="store_true", help="Executa o setup de forma automática/não-interativa.")
    parser.add_argument("--path", help="Caminho do diretório alvo a ser configurado.")
    parser.add_argument("--force", action="store_true", help="Sobrescreve arquivos de template existentes.")
    parser.add_argument("--dry-run", action="store_true", help="Simula o setup sem modificar o disco.")
    parser.add_argument("--prompt", action="store_true", help="Exibe o Prompt Mestre para IAs.")

    args = parser.parse_args()
    if args.prompt:
        print_setup_prompt()
    else:
        run_setup(
            interactive=not args.auto,
            target_dir=args.path,
            force=args.force,
            dry_run=args.dry_run
        )


if __name__ == "__main__":
    main()
