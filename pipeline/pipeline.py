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
from integrations.stitch.stitch_client import generate_screen, get_screen, edit_screen, generate_variants, sync_design_system
from integrations.jules.jules_client import JulesClient
from integrations.antigravity.antigravity_client import AntigravityClient, synthesize_prompt, validate_architecture



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
        prompt_file: str = None,
        stitch_prompt_file: str = None,
        jules_prompt_file: str = None,
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

        # -------------------------------------------------------------
        # RESUME SESSION (Se solicitado)
        # -------------------------------------------------------------
        if resume_session:
            log("PIPELINE", f"Retomando monitoramento da sessão existente: {resume_session}", Colors.HEADER)
            cls._monitor_jules_session(resume_session, repo_root, no_qa)
            return

        # -------------------------------------------------------------
        # ETAPA 1: LEITURA DOS ARQUIVOS DE PROMPT
        # -------------------------------------------------------------
        log("ETAPA 1/6", f"📄 Lendo arquivos de prompt...", Colors.HEADER)
        
        stitch_prompt = ""
        jules_prompt = ""
        file_label = ""

        # Arquivos dedicados (--stitch-prompt / --jules-prompt)
        if stitch_prompt_file and os.path.exists(stitch_prompt_file):
            with open(stitch_prompt_file, "r", encoding="utf-8", errors="replace") as f:
                stitch_prompt = f.read().strip()
            file_label += os.path.basename(stitch_prompt_file) + " "

        if jules_prompt_file and os.path.exists(jules_prompt_file):
            with open(jules_prompt_file, "r", encoding="utf-8", errors="replace") as f:
                jules_prompt = f.read().strip()
            file_label += os.path.basename(jules_prompt_file)

        # Arquivo unificado (prompt_file posicional ou legado)
        if prompt_file and os.path.exists(prompt_file):
            if not file_label:
                file_label = os.path.basename(prompt_file)
            with open(prompt_file, "r", encoding="utf-8", errors="replace") as f:
                raw_content = f.read().strip()
            p_stitch, p_jules = cls._parse_single_prompt(raw_content)
            if not stitch_prompt:
                stitch_prompt = p_stitch
            if not jules_prompt:
                jules_prompt = p_jules

        file_label = file_label.strip() or "Tarefa Não Identificada"

        print("\n" + "=" * 75)
        print(f"{Colors.BOLD}{Colors.CYAN}🚀 INICIANDO PIPELINE UNIFICADO AMB_V2: {file_label}{Colors.RESET}")
        print(f"📁 Repositório Alvo: {Colors.BOLD}{repo_name}{Colors.RESET} (Branch: {starting_branch})")
        print("=" * 75)

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
        # ETAPA 4: SÍNTESE COGNITIVA E CONSOLIDAÇÃO DO PROMPT PARA O JULES
        # -------------------------------------------------------------
        log("ETAPA 4/6", "🧠 Síntese Cognitiva e Consolidação do Prompt para o Jules...", Colors.HEADER)
        
        # 1. Resumo estruturado de alta densidade do Stitch (Design)
        stitch_summary = ""
        if not skip_stitch and (stitch_html or stitch_prompt):
            log("ANTIGRAVITY", "Consolidando e sintetizando especificação visual do Stitch com IA...", Colors.CYAN)
            client_agy = AntigravityClient()
            stitch_summary = cls._synthesize_stitch_ui(
                client_agy=client_agy,
                stitch_prompt=stitch_prompt,
                stitch_html=stitch_html,
                screen_title=screen_title
            )

        # 2. Leitura e extração segura e limpa das regras do repositório
        rules_dir = os.path.join(repo_root, ".antigravity", "rules")
        if not os.path.exists(rules_dir):
            rules_dir = os.path.join(repo_root, ".gemini", "rules")

        rules_summary = cls._extract_clean_rules(rules_dir)

        # 3. Montagem do Prompt Executivo Consolidado
        # GARANTIA CRÍTICA: O jules_prompt e o stitch_prompt são preservados 100% integrais
        prompt_sections = [
            "# 🚀 ESPECIFICAÇÃO DE ENGENHARIA DE SOFTWARE FULLSTACK (DESIGN-TO-DEPLOY)",
            f"**Repositório**: `{repo_name}`",
            f"**Branch de Trabalho**: `{starting_branch}`",
            f"**Arquivo de Especificação**: `{file_label.strip()}`",
            "",
            "---",
            "",
            "## 🎯 1. REQUISITOS DE ENGENHARIA & BACKEND (INTEGRAL)",
            jules_prompt if jules_prompt else "Implementar funcionalidade conforme padrões do repositório.",
            "",
        ]

        if not skip_stitch and (current_screen_id or stitch_summary or screenshot_url or stitch_prompt):
            meta_items = []
            if current_screen_id:
                meta_items.append(f"- **Screen ID (Stitch)**: `{current_screen_id}`")
            if screen_title:
                meta_items.append(f"- **Título da Tela**: {screen_title}")
            if screenshot_url:
                meta_items.append(f"- **Screenshot de Referência Visual**: {screenshot_url}")

            stitch_section_parts = [
                "---",
                "",
                "## 🎨 2. ESPECIFICAÇÃO DE INTERFACE, UI & FRONTEND (STITCH SPEC)",
                "> ⚠️ **DIRETRIZ FULLSTACK OBRIGATÓRIA PARA O PLANO DO JULES**:",
                "> Você DEVE planejar e implementar TANTO a camada de backend/dados (Seção 1) QUANTO os componentes de interface no frontend descritos nesta seção.",
                "> Crie ou atualize todos os arquivos de componentes de UI (páginas, abas, modais, formulários, rotas frontend) necessários para refletir fielmente o design.",
                "",
            ]

            if meta_items:
                stitch_section_parts.append("### Metadados do Mockup Stitch:\n" + "\n".join(meta_items) + "\n")

            if stitch_summary:
                stitch_section_parts.append(
                    "### 🏛️ Arquitetura Visual Sintetizada (Layout & Componentes):\n" + stitch_summary.strip() + "\n"
                )

            if stitch_prompt:
                stitch_section_parts.append(
                    "### 📐 Especificação Detalhada da UI & Wireframe (Integral):\n" + stitch_prompt.strip() + "\n"
                )

            prompt_sections.extend(stitch_section_parts)

        prompt_sections.extend([
            "---",
            "",
            "## 🛡️ 3. DIRETRIZES ARQUITETURAIS MANDATÓRIAS",
            "- **Separação Estrita de Responsabilidades (SRP)**: Cada módulo, serviço e componente deve possuir responsabilidade única.",
            "- **Tipagem Estrita**: TypeScript rigoroso, interfaces explícitas, 0 `any`.",
            "- **Integridade Local**: Todo o código implementado deve passar no typecheck e no build sem erros.",
            "",
            rules_summary if rules_summary else "",
        ])

        executive_prompt = "\n".join(filter(lambda s: s is not None, prompt_sections)).strip()

        log("PIPELINE", f"Prompt consolidado para o Jules gerado com sucesso!", Colors.GREEN)
        print(f"  📊 {Colors.BOLD}Estatísticas do Prompt Consolidado:{Colors.RESET}")
        print(f"     • Prompt de Engenharia (Jules): {len(jules_prompt)} caracteres (100% preservado)")
        if stitch_prompt:
            print(f"     • Prompt Visual (Stitch): {len(stitch_prompt)} caracteres (100% preservado)")
        if stitch_summary:
            print(f"     • Resumo Arquitetural do Stitch: {len(stitch_summary)} caracteres (ultra-denso)")
        print(f"     • Prompt Final para o Jules: {len(executive_prompt)} caracteres (~{len(executive_prompt.split())} palavras)\n")

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
        """Monitora as atividades do Jules, responde a planos e dúvidas com IA e executa o QA ao término."""
        client = JulesClient()
        from agents.autonomous_loop import monitor_and_assist_session
        
        final_state = monitor_and_assist_session(client=client, session_id=session_id, auto_reply_ai=True)

        # -------------------------------------------------------------
        # GATEKEEPER 2: QA LOCAL
        # -------------------------------------------------------------
        if not no_qa:
            log("ETAPA 6/6", "🛡️ Gatekeeper 2: Validação Local de Integridade", Colors.HEADER)
            QualityGatekeeper.run_qa(repo_root)

    @staticmethod
    def _parse_single_prompt(markdown_text: str) -> tuple[str, str]:
        """Extrai seção visual e seção de engenharia de um único arquivo markdown se presentes."""
        stitch_prompt = ""
        jules_prompt = ""

        # Divide por seções estruturadas se presentes
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

    @classmethod
    def _extract_clean_rules(cls, rules_dir: str, max_chars_per_file: int = 1500) -> str:
        """
        Lê e extrai regras do repositório garantindo:
        1. Formatação Markdown 100% íntegra (fechamento de blocos ```, sem cortes no meio de palavras).
        2. Limite saudável de caracteres por arquivo para não inflar desnecessariamente o prompt.
        3. Preservação de tópicos, diretrizes e convenções arquiteturais.
        """
        if not rules_dir or not os.path.exists(rules_dir):
            return ""

        extracted = []
        for rf in sorted(os.listdir(rules_dir)):
            if not rf.endswith(".md"):
                continue
            fpath = os.path.join(rules_dir, rf)
            try:
                with open(fpath, "r", encoding="utf-8", errors="replace") as f:
                    content = f.read().strip()
                if not content:
                    continue

                if len(content) <= max_chars_per_file:
                    clean_text = content
                else:
                    slice_point = max_chars_per_file
                    newline_idx = content.rfind("\n\n", 0, slice_point)
                    if newline_idx > max_chars_per_file // 2:
                        slice_point = newline_idx
                    else:
                        line_idx = content.rfind("\n", 0, slice_point)
                        if line_idx > max_chars_per_file // 2:
                            slice_point = line_idx
                        else:
                            space_idx = content.rfind(" ", 0, slice_point)
                            if space_idx > 0:
                                slice_point = space_idx

                    clean_text = content[:slice_point].rstrip() + "\n..."

                # Garantir que não existam code blocks abertos (```)
                fence_count = clean_text.count("```")
                if fence_count % 2 != 0:
                    clean_text += "\n```"

                extracted.append(f"### 📋 Regras: {rf}\n{clean_text}")
            except Exception:
                pass

        if not extracted:
            return ""

        return "\n\n".join(extracted)

    @classmethod
    def _clean_html_for_summary(cls, html: str) -> str:
        """Remove scripts, styles pesados, SVGs gigantes e base64 para focar na semântica da interface."""
        import re
        if not html:
            return ""
        # Remove comentários HTML
        html = re.sub(r'<!--[\s\S]*?-->', '', html)
        # Remove <script> tags
        html = re.sub(r'<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>', '', html, flags=re.IGNORECASE)
        # Remove <style> tags
        html = re.sub(r'<style\b[^<]*(?:(?!<\/style>)<[^<]*)*<\/style>', '', html, flags=re.IGNORECASE)
        # Simplifica tags <svg> com paths gigantes
        html = re.sub(r'<svg\b[^>]*>[\s\S]*?<\/svg>', '[Ícone SVG]', html, flags=re.IGNORECASE)
        # Remove base64 data URLs
        html = re.sub(r'data:image\/[a-zA-Z]+;base64,[^\s"\']+', '[Imagem Base64]', html)
        # Limita espaços em branco consecutivos
        html = re.sub(r'\s+', ' ', html).strip()
        return html[:10000]

    @classmethod
    def _synthesize_stitch_ui(cls, client_agy: AntigravityClient, stitch_prompt: str, stitch_html: str, screen_title: str) -> str:
        """Gera um resumo executivo da UI do Stitch em Markdown de alta densidade e concisão."""
        cleaned_dom = cls._clean_html_for_summary(stitch_html)
        
        system_instruction = (
            "Você é um Arquiteto de Software e Especialista em Design System / Frontend. "
            "Sua missão é analisar o layout e os componentes visuais gerados no Stitch e sintetizá-los "
            "em um RESUMO ARQUITETURAL EXECUTIVO DE ALTA DENSIDADE (máximo 200 a 350 palavras). "
            "NÃO inclua código HTML nem CSS cru. Estruture obrigatoriamente nos seguintes tópicos: "
            "1. Estrutura de Layout (grid, flex, containers, seções principais); "
            "2. Componentes Identificados (cards, tabelas, modais, formulários, listas); "
            "3. Elementos Interativos & Ações (botões primários/secundários, inputs, filtros, dropdowns); "
            "4. Tokens de Design (paleta de cores predominante, tipografia, espaçamento e estados visuais). "
            "Seja extremamente direto e denso para que um agente engenheiro (Jules) implemente a interface com fidelidade absoluta."
        )

        prompt_input = f"""Nome da Tela: {screen_title or 'Interface do Usuário'}
Diretrizes Visuais do Stitch Prompt:
{stitch_prompt if stitch_prompt else 'Conforme estrutura semântica abaixo.'}

DOM Semântico Limpo da Tela:
{cleaned_dom if cleaned_dom else 'Sem DOM extraído, basear-se estritamente no prompt de design.'}
"""
        try:
            summary = client_agy.generate_text(prompt=prompt_input, system_instruction=system_instruction)
            if summary and len(summary.strip()) > 30:
                clean_sum = summary.strip()
                # Garante integridade de code blocks
                if clean_sum.count("```") % 2 != 0:
                    clean_sum += "\n```"
                return clean_sum
        except Exception as e:
            log("STITCH", f"Aviso na síntese de UI via IA ({e}). Usando resumo estruturado de fallback.", Colors.YELLOW)

        # Fallback caso IA não responda
        fallback_lines = []
        if stitch_prompt:
            fallback_text = stitch_prompt[:500].rstrip()
            if len(stitch_prompt) > 500:
                fallback_text += "..."
            fallback_lines.append(f"- **Especificação Visual Original**: {fallback_text}")
        fallback_lines.extend([
            "- **Layout**: Interface modular baseada nos componentes descritos na especificação de design.",
            "- **Diretrizes de Estilo**: Respeitar a identidade visual e tokens do repositório.",
        ])
        return "\n".join(fallback_lines)



def main():
    parser = argparse.ArgumentParser(description="Pipeline Autônomo Design-to-Code (AMB_V2)")
    parser.add_argument("prompt_file", nargs="?", help="Caminho do arquivo markdown de prompt unificado")
    parser.add_argument("--stitch-prompt", "-s", help="Caminho do arquivo markdown contendo a especificação visual para o Stitch")
    parser.add_argument("--jules-prompt", "-j", help="Caminho do arquivo markdown contendo a especificação de engenharia para o Jules")
    parser.add_argument("--auto-approve", "-y", action="store_true", help="Pula confirmações manuais no Gatekeeper 1 de Design")
    parser.add_argument("--skip-stitch", action="store_true", help="Pula a etapa de layout visual do Stitch e vai direto ao Jules")
    parser.add_argument("--no-qa", action="store_true", help="Não executa a verificação local de typecheck/build ao final")
    parser.add_argument("--resume-session", "-r", help="Retoma o monitoramento de uma sessão existente do Jules")
    parser.add_argument("--device-type", choices=["DESKTOP", "MOBILE", "TABLET"], default="DESKTOP", help="Tipo de dispositivo alvo para o Stitch")
    parser.add_argument("--screen-id", help="ID de tela existente no Stitch para reaproveitar")
    parser.add_argument("--edit-screen", help="ID de tela existente para refinar com novo prompt")
    parser.add_argument("--sync-ds", action="store_true", help="Sincroniza os design tokens locais com o Stitch antes de iniciar")
    parser.add_argument("--branch", "-b", help="Branch de início para o Jules (Padrão: detecta a atual ou develop)")

    args = parser.parse_args()

    if not args.prompt_file and not args.stitch_prompt and not args.jules_prompt and not args.resume_session:
        parser.print_help()
        sys.exit(0)

    try:
        PipelineOrchestrator.run(
            prompt_file=args.prompt_file,
            stitch_prompt_file=args.stitch_prompt,
            jules_prompt_file=args.jules_prompt,
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
