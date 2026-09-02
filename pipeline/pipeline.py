#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
================================================================================
🚀 AMB_V2 - PIPELINE AUTÔNOMO DESIGN-TO-CODE (ORQUESTRADOR UNIFICADO)
================================================================================
Localização: amb_v2/pipeline/pipeline.py
Responsabilidade Única: Orquestrar sequencialmente o fluxo ponta a ponta
utilizando os módulos atômicos isolados de amb_v2 (Setup, Stitch, Jules, Antigravity).

Fluxo em 6 Fases:
  1. 📄 Parsing do Prompt (Separação Visual / Engenharia)
  2. 🎨 Geração Visual no Stitch SDK (@google/stitch-sdk)
  3. 🚪 Gatekeeper 1 (Aprovação / Refinamento / Variantes)
  4. 🧠 Síntese Cognitiva com Antigravity SDK & Regras Arquiteturais
  5. ⚡ Despacho & Monitoramento em Tempo Real no Jules (REST API v1alpha)
  6. 🛡️ Gatekeeper 2 (QA Local: Typecheck & Build de Produção)
================================================================================
"""

import os
import sys
import re
import json
import time
import argparse
import subprocess
from pathlib import Path

# Bootstrap dinâmico de caminhos amb_v2
_cur = os.path.dirname(os.path.abspath(__file__))
while _cur and os.path.basename(_cur) != "amb_v2":
    _p = os.path.dirname(_cur)
    if _p == _cur:
        break
    _cur = _p
_AMB = _cur
for _sub in [
    "config", "agents", "pipeline", "dashboard", "dashboard/watchers",
    "integrations/jules", "integrations/jules/tools",
    "integrations/stitch", "integrations/stitch/tools",
    "integrations/antigravity", "integrations/antigravity/tools",
    "integrations/render", "integrations/render/tools",
]:
    _p = os.path.normpath(os.path.join(_AMB, *_sub.split("/")))
    if os.path.exists(_p) and _p not in sys.path:
        sys.path.insert(0, _p)

from config import Colors, log, log_error, find_repo_root, get_repo_name, get_env, require_env, AmbError, ConfigurationError
from stitch_client import generate_screen, get_screen, edit_screen, generate_variants, sync_design_system
from jules_client import JulesClient
from antigravity_client import AntigravityClient, synthesize_prompt, validate_architecture


class PromptParser:
    """Extrai seção visual e seção de engenharia do arquivo markdown."""

    @staticmethod
    def parse_markdown(markdown_text: str) -> tuple[str, str]:
        stitch_prompt = ""
        jules_prompt = ""

        # Divide por seções estruturadas
        parts = re.split(r"(?i)#+\s*(?:1\.\s*)?(?:🎨\s*)?especificação\s+visual", markdown_text)
        if len(parts) > 1:
            sub = re.split(r"(?i)#+\s*(?:2\.\s*)?(?:⚡\s*)?especificação\s+de\s+engenharia", parts[1])
            stitch_prompt = sub[0].strip()
            if len(sub) > 1:
                jules_prompt = sub[1].strip()
        else:
            parts_jules = re.split(r"(?i)#+\s*(?:2\.\s*)?(?:⚡\s*)?especificação\s+de\s+engenharia", markdown_text)
            if len(parts_jules) > 1:
                stitch_prompt = parts_jules[0].strip()
                jules_prompt = parts_jules[1].strip()
            else:
                stitch_prompt = markdown_text.strip()
                jules_prompt = markdown_text.strip()

        return stitch_prompt, jules_prompt


class QualityGatekeeper:
    """Valida o código localmente após o término da sessão remota com auto-detecção de stack."""

    @staticmethod
    def run_qa(repo_root: str) -> bool:
        log("QA", "Executando verificação de integridade local...", Colors.CYAN)

        def _run_qa_cmd(cmd_str: str, label: str) -> bool:
            if not cmd_str.strip():
                return True
            print(f"\n[{Colors.BOLD}QA{Colors.RESET}] {cmd_str}")
            parts = cmd_str.strip().split()
            proc = subprocess.run(
                parts, cwd=repo_root,
                capture_output=True, text=True, encoding="utf-8", errors="replace", shell=True
            )
            if proc.returncode != 0:
                if proc.stdout.strip():
                    print(proc.stdout)
                if proc.stderr.strip():
                    print(proc.stderr)
                log_error("QA", f"Falha no passo: {label}!")
                return False
            print(f"{Colors.GREEN}✔ {label}: concluído com sucesso!{Colors.RESET}")
            return True

        from config import load_project_json
        proj = load_project_json()
        qa_cfg = proj.get("qa", {})

        # Auto-detecção de stack
        if not qa_cfg:
            if os.path.exists(os.path.join(repo_root, "package.json")):
                qa_cfg = {"typecheck": "npm run typecheck", "build": "npm run build"}
            elif os.path.exists(os.path.join(repo_root, "pyproject.toml")) or os.path.exists(os.path.join(repo_root, "requirements.txt")):
                qa_cfg = {"python_syntax": "python -m py_compile cli.py"}
            elif os.path.exists(os.path.join(repo_root, "go.mod")):
                qa_cfg = {"go_build": "go build ./..."}
            else:
                qa_cfg = {}

        if not qa_cfg:
            print(f"{Colors.GREEN}✔ Nenhuma suíte de QA necessária para este repositório.{Colors.RESET}")
            return True

        for step_key, step_cmd in qa_cfg.items():
            if not _run_qa_cmd(step_cmd, step_key):
                return False

        return True


class PipelineOrchestrator:
    """Orquestrador do Pipeline AMB_V2."""

    @classmethod
    def run(
        cls,
        prompt_file: str,
        auto_approve: bool = False,
        skip_stitch: bool = False,
        no_qa: bool = False,
        resume_session: str = None,
        device_type: str = "DESKTOP",
        edit_screen_id: str = None,
        screen_id: str = None,
        sync_ds: bool = False,
        starting_branch: str = None
    ):
        repo_root = find_repo_root()
        repo_name = get_repo_name()

        # Auto-detecta branch atual do Git local se não fornecida explicitamente
        if not starting_branch or starting_branch in ["develop", "main"]:
            try:
                b_proc = subprocess.run(["git", "branch", "--show-current"], cwd=repo_root, capture_output=True, text=True, check=False)
                cur_branch = b_proc.stdout.strip()
                if cur_branch:
                    starting_branch = cur_branch
            except Exception:
                pass
        starting_branch = starting_branch or "main"

        prompt_path = os.path.abspath(prompt_file)
        file_label = os.path.basename(prompt_path)

        print("\n" + "=" * 75)
        print(f"{Colors.BOLD}{Colors.CYAN}🚀 INICIANDO PIPELINE UNIFICADO AMB_V2: {file_label}{Colors.RESET}")
        print(f"📁 Repositório Alvo: {Colors.BOLD}{repo_name}{Colors.RESET} (Branch: {starting_branch})")
        print("=" * 75)


        # -------------------------------------------------------------
        # RESUME SESSION (Se solicitado)
        # -------------------------------------------------------------
        if resume_session:
            log("PIPELINE", f"Retomando monitoramento da sessão existente: {resume_session}", Colors.HEADER)
            cls._monitor_jules_session(resume_session, repo_root, no_qa)
            return

        # -------------------------------------------------------------
        # ETAPA 1: PARSING DO PROMPT
        # -------------------------------------------------------------
        log("ETAPA 1/6", f"📄 Lendo arquivo de prompt: {file_label}", Colors.HEADER)
        if not os.path.exists(prompt_path):
            raise AmbError(f"Arquivo de prompt não encontrado: {prompt_path}")

        with open(prompt_path, "r", encoding="utf-8", errors="replace") as f:
            raw_content = f.read()

        stitch_prompt, jules_prompt = PromptParser.parse_markdown(raw_content)
        log("PARSER", f"Prompt Visual: {len(stitch_prompt)} chars | Prompt Dev: {len(jules_prompt)} chars", Colors.DIM)

        # Sincronização de Design System se solicitado
        if sync_ds:
            log("ETAPA 1.1", "🎨 Sincronizando Design Tokens locais com o Stitch...", Colors.HEADER)
            try:
                sync_design_system()
            except Exception as e:
                log_error("SYNC-DS", f"Aviso na sincronização de tokens: {e}")

        # -------------------------------------------------------------
        # ETAPA 2: DESIGN NO GOOGLE STITCH SDK
        # -------------------------------------------------------------
        stitch_html = ""
        current_screen_id = screen_id or edit_screen_id
        screenshot_url = ""
        screen_title = ""

        if not skip_stitch:
            log("ETAPA 2/6", "🎨 Processando Layout Visual no Stitch SDK...", Colors.HEADER)
            if current_screen_id and not edit_screen_id:
                log("STITCH", f"Buscando tela existente ID: {current_screen_id}...", Colors.CYAN)
                screen_data = get_screen(screen_id=current_screen_id)
            elif edit_screen_id:
                log("STITCH", f"Refinando tela ID {edit_screen_id} com novo prompt...", Colors.CYAN)
                screen_data = edit_screen(screen_id=edit_screen_id, prompt=stitch_prompt)
            else:
                log("STITCH", f"Disparando geração de nova tela visual ({device_type})...", Colors.CYAN)
                screen_data = generate_screen(prompt=stitch_prompt, device_type=device_type)

            current_screen_id = screen_data.get("screenId") or current_screen_id
            stitch_html = screen_data.get("htmlCode", "")
            screenshot_url = screen_data.get("screenshotUrl", "")
            screen_title = screen_data.get("title", "")

            print("\n" + "-" * 75)
            print(f"✨ {Colors.BOLD}Mockup Stitch Gerado com Sucesso!{Colors.RESET}")
            print(f"🆔 Screen ID: {Colors.GREEN}{current_screen_id}{Colors.RESET}")
            if screen_title:
                print(f"🏷️ Título: {screen_title}")
            if screenshot_url:
                print(f"🖼️ Screenshot: {Colors.BLUE}{screenshot_url}{Colors.RESET}")
            print(f"📦 DOM HTML Extraído: {len(stitch_html)} caracteres")
            print("-" * 75 + "\n")

            # -------------------------------------------------------------
            # ETAPA 3: GATEKEEPER 1 (INTERATIVIDADE VISUAL)
            # -------------------------------------------------------------
            if not auto_approve:
                log("ETAPA 3/6", "🚪 Gatekeeper 1: Decisão de Design e Layout", Colors.HEADER)
                print("Escolha a próxima ação:")
                print("  [1] Aprovar mockup e seguir para Síntese Cognitiva & Jules (Recomendado)")
                print("  [2] Refinar visual com nova instrução no Stitch")
                print("  [3] Gerar 3 variantes de design alternativas")
                print("  [4] Cancelar execução")
                
                try:
                    choice = input(f"\n{Colors.BOLD}Opção [1-4] (Padrão: 1): {Colors.RESET}").strip() or "1"
                except (EOFError, KeyboardInterrupt):
                    choice = "1"

                if choice == "2":
                    instruction = input(f"{Colors.BOLD}Digite a instrução de refinamento: {Colors.RESET}").strip()
                    if instruction:
                        log("STITCH", f"Refinando tela {current_screen_id}...", Colors.CYAN)
                        screen_data = edit_screen(screen_id=current_screen_id, prompt=instruction)
                        stitch_html = screen_data.get("htmlCode", "")
                        screenshot_url = screen_data.get("screenshotUrl", "")
                        print(f"✅ Refinamento concluído. Nova screenshot: {screenshot_url}")
                elif choice == "3":
                    log("STITCH", f"Gerando variantes para a tela {current_screen_id}...", Colors.CYAN)
                    vars_data = generate_variants(screen_id=current_screen_id, count=3)
                    print(f"✅ Variantes geradas: {json.dumps(vars_data, indent=2)}")
                elif choice == "4":
                    print(f"{Colors.YELLOW}Execução cancelada pelo usuário.{Colors.RESET}")
                    return

        # -------------------------------------------------------------
        # ETAPA 4: SÍNTESE COGNITIVA COM ANTIGRAVITY SDK
        # -------------------------------------------------------------
        log("ETAPA 4/6", "🧠 Síntese Cognitiva e Validação Arquitetural...", Colors.HEADER)
        
        # Leitura das regras do repositório
        rules_dir = os.path.join(repo_root, ".antigravity", "rules")
        if not os.path.exists(rules_dir):
            rules_dir = os.path.join(repo_root, ".gemini", "rules")

        rules_summary = ""
        if os.path.exists(rules_dir):
            for rf in sorted(os.listdir(rules_dir)):
                if rf.endswith(".md"):
                    try:
                        with open(os.path.join(rules_dir, rf), "r", encoding="utf-8", errors="replace") as f:
                            rules_summary += f"\n--- [{rf}] ---\n" + f.read()[:600]
                    except Exception:
                        pass

        # Compilação do Prompt de Engenharia de Alta Densidade
        dev_spec = f"""# ESPECIFICAÇÃO DE ENGENHARIA DE SOFTWARE
## Contexto da Tarefa: {file_label}

### 1. Requisitos de Implementação e Funcionalidades:
{jules_prompt}

### 2. Estrutura e Fidelidade Visual (Stitch DOM):
{stitch_html[:8000] if stitch_html else "Utilizar estrutura e tokens definidos no Design System do projeto."}

### 3. Regras Arquiteturais Mandatórias do Projeto:
- Respeitar estritamente a separação de responsabilidades (SRP).
- Seguir os padrões e convenções de código definidos nas regras do repositório.
- Manter validação de tipos estrita e compilação sem erros no build do projeto.
"""

        log("ANTIGRAVITY", "Validando e sintetizando prompt técnico estruturado...", Colors.CYAN)
        client_agy = AntigravityClient()
        executive_prompt = client_agy.generate_text(
            prompt=dev_spec,
            system_instruction=(
                "Você é o Arquiteto de Software Principal do projeto. "
                "Transforme as especificações visuais e de engenharia em um plano de ação detalhado para o agente Google Jules. "
                "Preserve todos os requisitos de domínio, componentes e regras."
            )
        )

        # -------------------------------------------------------------
        # ETAPA 5: DESPACHO NO GOOGLE JULES (REST API)
        # -------------------------------------------------------------
        log("ETAPA 5/6", "⚡ Despachando Tarefa na Cloud do Google Jules...", Colors.HEADER)
        jules_client = JulesClient()
        source_name = f"sources/github/{repo_name}"

        session_resp = jules_client.create_session(
            prompt=executive_prompt,
            source_name=source_name,
            title=f"Task: {file_label.replace('.md', '').replace('_', ' ').title()}",
            base_branch=starting_branch
        )

        session_id = session_resp.get("name", "").split("/")[-1] or session_resp.get("id", "")
        if not session_id:
            raise AmbError(f"Resposta inválida ao criar sessão no Jules: {session_resp}")

        print("\n" + "=" * 75)
        print(f"🎉 {Colors.BOLD}Sessão Remota Iniciada no Google Jules!{Colors.RESET}")
        print(f"🆔 Session ID: {Colors.GREEN}{session_id}{Colors.RESET}")
        print(f"🔗 Acompanhe em: {Colors.BLUE}https://jules.google.com/sessions/{session_id}{Colors.RESET}")
        print("=" * 75 + "\n")

        # -------------------------------------------------------------
        # ETAPA 6: MONITORAMENTO EM TEMPO REAL & QA
        # -------------------------------------------------------------
        cls._monitor_jules_session(session_id, repo_root, no_qa)

    @classmethod
    def _monitor_jules_session(cls, session_id: str, repo_root: str, no_qa: bool = False):
        """Monitora as atividades do Jules, responde a planos e executa o QA ao término."""
        client = JulesClient()
        seen_ids = set()
        plan_approved = False

        log("JULES-MONITOR", f"Streaming de atividades da sessão {session_id}...", Colors.CYAN)

        while True:
            try:
                session = client.get_session(session_id)
                state = session.get("state", "UNKNOWN")

                act_data = client.list_activities(session_id=session_id, page_size=50)
                activities = act_data.get("activities", [])
                activities.reverse()

                for act in activities:
                    aid = act.get("name") or act.get("id") or str(act.get("createTime"))
                    if aid not in seen_ids:
                        seen_ids.add(aid)
                        orig = act.get("originator", "SYSTEM")
                        desc = act.get("description") or act.get("title") or ""

                        # 1. Comando Bash
                        if "bashCommand" in act:
                            cmd = act.get("bashCommand", {}).get("command", "")
                            print(f"[{Colors.YELLOW}BASH{Colors.RESET}] $ {cmd}")
                        # 2. Mensagem do Agente
                        elif "agentMessage" in act or "agentMessaged" in act:
                            txt = (act.get("agentMessaged") or act.get("agentMessage") or {}).get("text") or desc
                            print(f"[{Colors.CYAN}AGENTE{Colors.RESET}] {txt}")
                        # 3. Plano Gerado
                        elif "planGenerated" in act:
                            plan = act.get("planGenerated", {}).get("plan", {})
                            print(f"\n{Colors.BOLD}{Colors.GREEN}📋 PLANO FORMULADO PELO AGENTE:{Colors.RESET}")
                            print(json.dumps(plan, indent=2))
                            if not plan_approved:
                                log("JULES", "Aprovando plano do agente (:approvePlan)...", Colors.GREEN)
                                try:
                                    client.approve_plan(session_id)
                                    plan_approved = True
                                except Exception as ep:
                                    log_error("JULES", f"Falha ao aprovar plano: {ep}")
                        # 4. Dúvida do Agente
                        elif "userFeedbackRequired" in act:
                            q = act.get("userFeedbackRequired", {}).get("question") or desc
                            print(f"\n[{Colors.BOLD}{Colors.RED}❓ DÚVIDA DO AGENTE JULES{Colors.RESET}] {q}")
                            # Auto-resposta com Antigravity
                            client_agy = AntigravityClient()
                            reply = client_agy.generate_text(
                                prompt=f"O agente Jules perguntou durante a codificação: '{q}'. Dê a resposta técnica correta seguindo as diretrizes e padrões do projeto."
                            )
                            print(f"[{Colors.GREEN}RESPOSTA ENVIADA{Colors.RESET}] {reply}")
                            client.send_message(session_id, reply)
                        else:
                            if desc:
                                print(f"[{Colors.DIM}{orig}{Colors.RESET}] {desc}")

                # Estados de Conclusão
                if state in ["COMPLETED", "SUCCEEDED"]:
                    print("\n" + "=" * 75)
                    log("JULES", f"🎉 Sessão {session_id} concluída com sucesso no Jules!", Colors.GREEN)
                    print("=" * 75)
                    break
                elif state in ["FAILED", "CANCELLED", "CLOSED"]:
                    log_error("JULES", f"Sessão finalizada com estado: {state}")
                    break

                time.sleep(6)
            except KeyboardInterrupt:
                print(f"\n{Colors.YELLOW}Monitoramento pausado. A sessão continua executando na nuvem do Jules.{Colors.RESET}")
                return
            except Exception as e:
                log_error("MONITOR", f"Erro temporário de polling: {e}")
                time.sleep(6)

        # -------------------------------------------------------------
        # GATEKEEPER 2: QA LOCAL
        # -------------------------------------------------------------
        if not no_qa:
            log("ETAPA 6/6", "🛡️ Gatekeeper 2: Validação Local de Integridade", Colors.HEADER)
            QualityGatekeeper.run_qa(repo_root)


def main():
    parser = argparse.ArgumentParser(description="Pipeline Autônomo Design-to-Code (AMB_V2)")
    parser.add_argument("prompt_file", nargs="?", help="Caminho do arquivo markdown de prompt (ex: amb_v2/pipeline/prompts/09_fase0_arvore_hipoteses.md)")
    parser.add_argument("--auto-approve", action="store_true", help="Pula confirmações manuais no Gatekeeper 1 de Design")
    parser.add_argument("--skip-stitch", action="store_true", help="Pula a etapa de layout visual do Stitch e vai direto ao Jules")
    parser.add_argument("--no-qa", action="store_true", help="Não executa a verificação local de typecheck/build ao final")
    parser.add_argument("--resume-session", "-r", help="Retoma o monitoramento de uma sessão existente do Jules")
    parser.add_argument("--device-type", choices=["DESKTOP", "MOBILE", "TABLET"], default="DESKTOP", help="Tipo de dispositivo alvo para o Stitch")
    parser.add_argument("--screen-id", help="ID de tela existente no Stitch para reaproveitar")
    parser.add_argument("--edit-screen", help="ID de tela existente para refinar com novo prompt")
    parser.add_argument("--sync-ds", action="store_true", help="Sincroniza os design tokens locais com o Stitch antes de iniciar")
    parser.add_argument("--branch", default="develop", help="Branch de início para o Jules (Padrão: develop)")

    args = parser.parse_args()

    if not args.prompt_file and not args.resume_session:
        parser.print_help()
        sys.exit(0)

    try:
        PipelineOrchestrator.run(
            prompt_file=args.prompt_file,
            auto_approve=args.auto_approve,
            skip_stitch=args.skip_stitch,
            no_qa=args.no_qa,
            resume_session=args.resume_session,
            device_type=args.device_type,
            edit_screen_id=args.edit_screen,
            screen_id=args.screen_id,
            sync_ds=args.sync_ds,
            starting_branch=args.branch
        )
    except AmbError as e:
        log_error("PIPELINE", e.message, hint=e.hint)
        sys.exit(1)
    except Exception as e:
        log_error("PIPELINE", str(e))
        sys.exit(1)


if __name__ == "__main__":
    main()
