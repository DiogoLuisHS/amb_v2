#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🧙‍♂️ AMB_V2 - Assistente Inteligente de Setup de Projetos (SRP Orquestrador)
Localização: amb_v2/config/setup_project.py
Responsabilidade Única: Orquestrar a execução do setup invocando os submódulos
especializados em config/setup_modules (ProjectAnalyzer, AmbProvisioner, CognitiveSynthesizer).
"""

import os
import sys
import json

# Bootstrap dinâmico de caminhos amb_v2
_cur = os.path.dirname(os.path.abspath(__file__))
while _cur and os.path.basename(_cur) != "amb_v2":
    _p = os.path.dirname(_cur)
    if _p == _cur:
        break
    _cur = _p
_AMB = _cur

for _sub in [
    "config", "config/setup_modules", "agents", "pipeline", "dashboard", "dashboard/watchers",
    "integrations/jules", "integrations/jules/tools",
    "integrations/stitch", "integrations/stitch/tools",
    "integrations/antigravity", "integrations/antigravity/tools",
    "integrations/render", "integrations/render/tools",
]:
    _p = os.path.normpath(os.path.join(_AMB, *_sub.split("/")))
    if os.path.exists(_p) and _p not in sys.path:
        sys.path.insert(0, _p)

# Adiciona o diretório atual ao sys.path para importar config
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
from config import Colors, log, log_error, find_repo_root, get_env

# Importa as classes especializadas extraídas para os submódulos (SRP)
from project_analyzer import ProjectAnalyzer
from amb_provisioner import AmbProvisioner
from cognitive_synthesizer import CognitiveSynthesizer


def run_setup(interactive: bool = True):
    """Executa o fluxo completo de setup, provisiona .amb e salva as configurações."""
    root = find_repo_root()
    log("SETUP", f"Iniciando análise do projeto em: {root}", Colors.CYAN)

    # 1. Análise
    detected_repo = ProjectAnalyzer.detect_git_repo(root)
    stack = ProjectAnalyzer.detect_stack(root)

    print(f"\n{Colors.BOLD}🔍 Resultados da Auto-Detecção:{Colors.RESET}")
    print(f"  • Repositório Git:    {Colors.GREEN}{detected_repo or 'Não detectado'}{Colors.RESET}")
    print(f"  • Tipo de Projeto:    {Colors.GREEN}{stack['type']}{Colors.RESET}")
    print(f"  • Gerenciador:        {Colors.GREEN}{stack['package_manager']}{Colors.RESET}")
    print(f"  • Frameworks:         {Colors.GREEN}{', '.join(stack['frameworks']) or 'Genérico'}{Colors.RESET}")
    print(f"  • Pasta de Regras:    {Colors.GREEN}{stack['rules_dir'] or 'Nenhuma detectada'}{Colors.RESET}")
    print(f"  • Render Deploy:      {Colors.GREEN}{'Configurado (render.yaml)' if stack['has_render_yaml'] else 'Nenhum'}{Colors.RESET}\n")

    current_repo = get_env("GITHUB_REPOSITORY", detected_repo or "")
    current_stitch_id = get_env("STITCH_PROJECT_ID", "")
    current_render_id = get_env("RENDER_SERVICE_ID", "")

    # 2. Interatividade se solicitado
    if interactive:
        print(f"{Colors.YELLOW}Configuração Interativa de Metadados (pressione ENTER para manter o valor sugerido):{Colors.RESET}")
        
        in_repo = input(f"👉 Repositório GitHub (ex: owner/repo) [{current_repo}]: ").strip()
        if in_repo:
            current_repo = in_repo

        in_stitch = input(f"👉 Stitch Project ID [{current_stitch_id}]: ").strip()
        if in_stitch:
            current_stitch_id = in_stitch

        in_render = input(f"👉 Render Service ID (opcional) [{current_render_id}]: ").strip()
        if in_render:
            current_render_id = in_render

    # 3. Provisionamento da Estrutura .amb/ e Personas Contextualizadas
    log("SETUP", "Provisionando estrutura .amb/ e contextualizando personas...", Colors.CYAN)
    AmbProvisioner.provision_structure(root, stack, current_repo or "Projeto")


    # 4. Síntese Cognitiva
    log("SETUP", "Inferindo diretrizes e resumo técnico do projeto...", Colors.CYAN)
    summary_spec = CognitiveSynthesizer.infer_project_specs(root, stack)

    # 5. Salvar amb_project.json dentro de .amb/ do projeto
    project_data = {
        "repository": current_repo,
        "stitch_project_id": current_stitch_id,
        "render_service_id": current_render_id,
        "stack": stack,
        "technical_summary": summary_spec
    }

    out_dir = os.path.join(root, ".amb")
    os.makedirs(out_dir, exist_ok=True)
    out_json = os.path.join(out_dir, "amb_project.json")
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(project_data, f, indent=2, ensure_ascii=False)

    log("SETUP", f"✅ Arquivo de configuração salvo em: {out_json}", Colors.GREEN)

    # 6. Atualizar .env se necessário
    env_path = os.path.join(root, ".env")
    env_updates = {}
    if current_repo:
        env_updates["GITHUB_REPOSITORY"] = current_repo
    if current_stitch_id:
        env_updates["STITCH_PROJECT_ID"] = current_stitch_id
    if current_render_id:
        env_updates["RENDER_SERVICE_ID"] = current_render_id

    if env_updates:
        if not os.path.exists(env_path):
            with open(env_path, "w", encoding="utf-8") as f:
                f.write("# AMB_V2 - Variáveis de Ambiente do Projeto\n")
                for k, v in env_updates.items():
                    f.write(f"{k}={v}\n")
            log("SETUP", f"✅ Arquivo .env criado com sucesso em: {env_path}", Colors.GREEN)
        else:
            try:
                with open(env_path, "r", encoding="utf-8") as f:
                    lines = f.readlines()
                
                existing_keys = set()
                new_lines = []
                for line in lines:
                    k = line.split("=")[0].strip() if "=" in line else None
                    if k in env_updates:
                        new_lines.append(f"{k}={env_updates[k]}\n")
                        existing_keys.add(k)
                    else:
                        new_lines.append(line)

                for k, v in env_updates.items():
                    if k not in existing_keys:
                        new_lines.append(f"{k}={v}\n")

                with open(env_path, "w", encoding="utf-8") as f:
                    f.writelines(new_lines)
                log("SETUP", f"✅ Arquivo .env atualizado com as chaves do projeto.", Colors.GREEN)
            except Exception as e:
                log_error("SETUP", f"Não foi possível atualizar .env: {e}")

    print(f"\n{Colors.BOLD}{Colors.GREEN}🎉 Setup do Projeto Concluído com Sucesso!{Colors.RESET}")
    print(f"Estrutura .amb/ e Personas contextualizadas com base na stack {stack.get('type')}.")
    print(f"Configuração salva em: {out_json}")
    print(f"Você agora pode executar os comandos da CLI 'amb' normalmente.")


def print_setup_prompt():
    """Exibe o Prompt Mestre de Auto-Configuração de IA para novos projetos."""
    prompt_text = """# 🚀 PROMPT DE AUTO-CONFIGURAÇÃO DO AMB_V2

Missão: Configuração e Ativação do Ecossistema AMB_V2 no Projeto Atual.

Você deve analisar este repositório e configurar o ecossistema de automação amb_v2 de forma 100% compatível, genérica e sem falhas.

---

### 📋 Passos Obrigatórios de Execução:

1. Inspeção e Detecção da Stack:
   - Inspecione a raiz do projeto (package.json, bun.lock, pnpm-lock.yaml, pyproject.toml, .git/config, render.yaml, pastas de regras .antigravity/rules ou .gemini/rules).
   - Identifique o repositório remoto (owner/repo), a stack técnica (frameworks frontend e backend) e o gerenciador de pacotes.

2. Execução do Setup Automático (Provisionamento de .amb e Personas):
   - Execute o setup automático que criará a estrutura .amb/ e adaptará as personas à stack detectada:
     amb setup --auto  (ou python amb_v2/config/setup_project.py --auto)

3. Geração / Atualização do .env:
   - Verifique se o arquivo .env existe na raiz do repositório.
   - Garanta que as seguintes variáveis estejam declaradas no .env:
     * STITCH_API_KEY=
     * STITCH_PROJECT_ID=
     * JULES_API_KEY=
     * GITHUB_REPOSITORY=<owner/repo detectado>
     * GEMINI_API_KEY=
     * RENDER_API_KEY=
     * RENDER_SERVICE_ID=

4. Validação e Teste do Ambiente:
   - Execute o script de validação para checar o carregamento correto das variáveis e caminhos:
     amb check
   - Execute a inspeção de schemas do banco de dados:
     amb schema
   - Execute o teste de listagem das personas:
     amb agent --list

5. Regras Mandatórias:
   - Zero Fallback: Sem supressão silenciosa de erros ou mascaramento de falhas.
   - SRP: Mantenha cada script em seu submódulo oficial (config/, agents/, architecture/, integrations/, dashboard/).
   - Dual-Theme Nativo: Respeite o Design System do projeto com suporte a Light e Dark Mode via tokens CSS.

Ao finalizar, exiba o resumo da stack detectada e o status das chaves configuradas."""

    print("\n" + "=" * 75)
    print(f"{Colors.BOLD}{Colors.CYAN}📋 PROMPT MESTRE DE AUTO-CONFIGURAÇÃO PARA IA (Copie e cole na sua IA):{Colors.RESET}")
    print("=" * 75 + "\n")
    print(prompt_text)
    print("\n" + "=" * 75 + "\n")


if __name__ == "__main__":
    if "--prompt" in sys.argv or "-p" in sys.argv:
        print_setup_prompt()
    else:
        is_auto = "--auto" in sys.argv or "--non-interactive" in sys.argv
        run_setup(interactive=not is_auto)
