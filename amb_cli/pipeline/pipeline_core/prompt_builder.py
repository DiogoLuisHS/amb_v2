import re
from typing import Optional, Any
from core import Colors, log

def parse_single_prompt(markdown_text: str) -> tuple[str, str]:
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

def clean_html_for_summary(html: str) -> str:
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

def synthesize_stitch_ui(client_agy: Any, stitch_prompt: str, stitch_html: str, screen_title: str) -> str:
    """Gera um resumo executivo da UI do Stitch em Markdown de alta densidade e concisão."""
    cleaned_dom = clean_html_for_summary(stitch_html)

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

def build_executive_prompt(
    repo_name: str,
    starting_branch: str,
    file_label: str,
    jules_prompt: str,
    stitch_prompt: str,
    current_screen_id: Optional[str],
    screen_title: Optional[str],
    screenshot_url: Optional[str],
    stitch_summary: Optional[str],
    rules_summary: Optional[str],
    skip_stitch: bool
) -> str:
    """Montagem do Prompt Executivo Consolidado"""
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
        "- **Tipagem Estrita**: Tipagem rigorosa da stack do projeto, contratos explícitos e sem tipos genéricos opacos.",
        "- **Integridade Local**: Todo o código implementado deve passar no typecheck e no build sem erros.",
        "",
        rules_summary if rules_summary else "",
    ])

    return "\n".join(filter(lambda s: s is not None, prompt_sections)).strip()
