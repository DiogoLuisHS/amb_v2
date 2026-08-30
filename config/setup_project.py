#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🧙‍♂️ AMB_V2 - Assistente Inteligente e Genérico de Setup de Projetos (SRP)
Localização: amb_v2/config/setup_project.py
Responsabilidade Única: Analisar o projeto atual (Git, Stack, Regras), provisionar a estrutura
`.jules/` (personas, diários, prompts), contextualizar as personas com base na stack e salvar a configuração.
"""

import os
import sys
import json
import re
import subprocess
from typing import Dict, Any, Optional

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

# Adiciona o diretório atual ao sys.path para importar config
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
from config import Colors, log, log_error, find_repo_root, get_env, AmbError


class ProjectAnalyzer:
    """Extrai informações estruturais e de ambiente do repositório local."""

    @staticmethod
    def detect_git_repo(root: str) -> Optional[str]:
        """Tenta identificar o owner/repo do git remote origin."""
        try:
            res = subprocess.run(
                ["git", "remote", "get-url", "origin"],
                cwd=root,
                capture_output=True,
                text=True,
                timeout=5,
                check=False
            )
            if res.returncode == 0 and res.stdout.strip():
                url = res.stdout.strip()
                match = re.search(r"github\.com[:/]([^/]+)/([^/.]+)", url)
                if match:
                    return f"{match.group(1)}/{match.group(2)}"
        except Exception:
            pass

        git_config = os.path.join(root, ".git", "config")
        if os.path.exists(git_config):
            try:
                with open(git_config, "r", encoding="utf-8", errors="replace") as f:
                    content = f.read()
                    match = re.search(r"url\s*=\s*.*github\.com[:/]([^/]+)/([^/.]+)", content)
                    if match:
                        return f"{match.group(1)}/{match.group(2)}"
            except Exception:
                pass
        return None

    @staticmethod
    def detect_stack(root: str) -> Dict[str, Any]:
        """Identifica linguagem, frameworks e ferramentas do projeto."""
        stack = {
            "type": "unknown",
            "frameworks": [],
            "package_manager": "npm",
            "has_render_yaml": os.path.exists(os.path.join(root, "render.yaml")),
            "rules_dir": None
        }

        # Coleta manifestos da raiz e de subpastas conhecidas de monorepos
        search_dirs = [root]
        for sub in ["apps", "app", "packages", "src", "frontend", "backend", "web", "api"]:
            p = os.path.join(root, sub)
            if os.path.exists(p) and os.path.isdir(p):
                search_dirs.append(p)
                try:
                    for child in os.listdir(p):
                        cp = os.path.join(p, child)
                        if os.path.isdir(cp):
                            search_dirs.append(cp)
                except Exception:
                    pass

        has_node = False
        has_python = False

        # 1. Package Manager & Node/TS Stack
        for sdir in search_dirs:
            if os.path.exists(os.path.join(sdir, "bun.lock")) or os.path.exists(os.path.join(sdir, "bun.lockb")):
                stack["package_manager"] = "bun"
                has_node = True
            elif os.path.exists(os.path.join(sdir, "pnpm-lock.yaml")):
                stack["package_manager"] = "pnpm"
                has_node = True
            elif os.path.exists(os.path.join(sdir, "yarn.lock")):
                stack["package_manager"] = "yarn"
                has_node = True

            pkg_path = os.path.join(sdir, "package.json")
            if os.path.exists(pkg_path):
                has_node = True
                try:
                    with open(pkg_path, "r", encoding="utf-8") as f:
                        pkg = json.load(f)
                        deps = {**pkg.get("dependencies", {}), **pkg.get("devDependencies", {})}
                        if "react" in deps or "next" in deps:
                            fw = "React" if "react" in deps else "Next.js"
                            if fw not in stack["frameworks"]: stack["frameworks"].append(fw)
                        if "vue" in deps or "nuxt" in deps:
                            fw = "Vue" if "vue" in deps else "Nuxt.js"
                            if fw not in stack["frameworks"]: stack["frameworks"].append(fw)
                        if "hono" in deps and "Hono" not in stack["frameworks"]:
                            stack["frameworks"].append("Hono")
                        if "express" in deps and "Express" not in stack["frameworks"]:
                            stack["frameworks"].append("Express")
                        if "fastify" in deps and "Fastify" not in stack["frameworks"]:
                            stack["frameworks"].append("Fastify")
                        if ("tailwindcss" in deps or "@tailwindcss/vite" in deps) and "TailwindCSS" not in stack["frameworks"]:
                            stack["frameworks"].append("TailwindCSS")
                        if "drizzle-orm" in deps and "Drizzle ORM" not in stack["frameworks"]:
                            stack["frameworks"].append("Drizzle ORM")
                        if ("prisma" in deps or "@prisma/client" in deps) and "Prisma" not in stack["frameworks"]:
                            stack["frameworks"].append("Prisma")
                        if "@google/stitch-sdk" in deps and "Stitch SDK" not in stack["frameworks"]:
                            stack["frameworks"].append("Stitch SDK")
                except Exception:
                    pass

            # 2. Python Stack
            for py_file in ["pyproject.toml", "requirements.txt", "Pipfile"]:
                pypath = os.path.join(sdir, py_file)
                if os.path.exists(pypath):
                    has_python = True
                    try:
                        with open(pypath, "r", encoding="utf-8", errors="replace") as f:
                            c = f.read().lower()
                            if "fastapi" in c and "FastAPI" not in stack["frameworks"]: stack["frameworks"].append("FastAPI")
                            if "django" in c and "Django" not in stack["frameworks"]: stack["frameworks"].append("Django")
                            if "flask" in c and "Flask" not in stack["frameworks"]: stack["frameworks"].append("Flask")
                            if "sqlalchemy" in c and "SQLAlchemy" not in stack["frameworks"]: stack["frameworks"].append("SQLAlchemy")
                            if "pydantic" in c and "Pydantic" not in stack["frameworks"]: stack["frameworks"].append("Pydantic")
                    except Exception:
                        pass

        if has_node and has_python:
            stack["type"] = "hybrid (Node/Python)"
            stack["package_manager"] = f"{stack['package_manager']} / pip"
        elif has_node:
            stack["type"] = "node/typescript"
        elif has_python:
            stack["type"] = "python"
            stack["package_manager"] = "pip/poetry"

        # 3. Rules Directory
        for candidate in [".antigravity/rules", ".gemini/rules", "rules"]:
            if os.path.exists(os.path.join(root, candidate)):
                stack["rules_dir"] = candidate
                break

        return stack


class AmbProvisioner:
    """Provisiona e contextualiza dinamicamente as personas e diários na pasta .amb/."""

    @classmethod
    def provision_structure(cls, root: str, stack: Dict[str, Any], repo_name: str) -> None:
        """Cria as pastas de personas, diários e prompts se não existirem."""
        amb_root = os.path.join(root, ".amb")
        personas_dir = os.path.join(amb_root, "personas")
        diarios_dir = os.path.join(amb_root, "diarios")
        prompts_dir = os.path.join(amb_root, "prompts")

        for d in [amb_root, personas_dir, diarios_dir, prompts_dir]:
            os.makedirs(d, exist_ok=True)

        # Contexto de Comandos de QA da Stack
        is_node = "node" in stack.get("type", "").lower() or any(f in stack.get("frameworks", []) for f in ["React", "Next.js", "Hono", "Express", "Vue"])
        is_python = "python" in stack.get("type", "").lower() or any(f in stack.get("frameworks", []) for f in ["FastAPI", "Flask", "Django"])
        
        typecheck_cmd = "npm run typecheck" if is_node else ("mypy ." if is_python else "verificação de tipos")
        build_cmd = "npm run build" if is_node else ("pytest" if is_python else "build do projeto")
        backend_target = "Hono/Express" if is_node else ("FastAPI/Flask" if is_python else "Backend")
        schema_validator = "Zod" if is_node else ("Pydantic" if is_python else "Schema Validator")

        templates = {
            "align": {
                "title": "📐 Align: Padronização de Erros & Envelopes JSON Semânticos",
                "content": f"""# 📐 Align: Padronização de Erros & Envelopes JSON Semânticos

Você é o "Align" 📐 — um engenheiro especialista em consistência de backend focado em padronizar o tratamento de erros e status codes HTTP.
Sua missão é auditar arquivos de controller/router do {repo_name} e garantir que suas respostas de erro sigam estritamente o envelope padronizado e status codes HTTP semânticos (400, 401, 403, 404, 409, 500).

---

## 🛡️ Limites e Diretrizes (Boundaries)
- Validação mandatória antes do PR: `{typecheck_cmd}` e `{build_cmd}`.
- Trate blocos catch com retorno estruturado `{{ error: string }}` ou envelope padronizado do projeto.
- Mantenha o arquivo com escopo cirúrgico e mínimo diff.
- Consulte e registre aprendizados em `.amb/diarios/align.md`.
"""
            },
            "beacon": {
                "title": "🗼 Beacon: Acessibilidade & Semântica Web (a11y)",
                "content": f"""# 🗼 Beacon: Acessibilidade & Semântica Web (a11y)

Você é o "Beacon" 🗼 — um especialista em acessibilidade e semântica de interface dedicado a tornar o {repo_name} 100% navegável por teclado, inclusivo e aderente aos padrões WAI-ARIA.
Sua missão é auditar componentes interativos e modais garantindo atributos `aria-label`, HTML semântico (`<button>`, `<dialog>`, `<label>`) e contraste WCAG AAA em ambos os temas (Light e Dark).

---

## 🛡️ Limites e Diretrizes (Boundaries)
- Validação mandatória: `{typecheck_cmd}` e `{build_cmd}`.
- Reutilize componentes primitivos acessíveis do Design System do projeto.
- Consulte e registre aprendizados em `.amb/diarios/beacon.md`.
"""
            },
            "bolt": {
                "title": "⚡ Bolt: Performance & Redução de Latência",
                "content": f"""# ⚡ Bolt: Performance & Redução de Latência

Você é o "Bolt" ⚡ — um engenheiro sênior focado em eliminar latência e gargalos de performance no {repo_name}.
Sua missão é auditar rotas, queries de banco e componentes eliminando cascatas de chamadas seriais (waterfalls) com paralelismo e batching.

---

## 🛡️ Limites e Diretrizes (Boundaries)
- Validação mandatória: `{typecheck_cmd}` e `{build_cmd}`.
- Paralelize chamadas independentes (ex: `Promise.all` em JS/TS ou `asyncio.gather` em Python).
- Preserve 100% dos contratos de dados e integridade do projeto.
- Consulte e registre aprendizados em `.amb/diarios/bolt.md`.
"""
            },
            "deadwood": {
                "title": "🪓 Deadwood: Remoção de Código Morto & Imports Órfãos",
                "content": f"""# 🪓 Deadwood: Remoção de Código Morto & Imports Órfãos

Você é o "Deadwood" 🪓 — um guardião de código limpo cuja missão é podar cirurgicamente código morto, variáveis órfãs, branches inalcançáveis e imports não utilizados no {repo_name}.

---

## 🛡️ Limites e Diretrizes (Boundaries)
- Validação mandatória: `{typecheck_cmd}` e `{build_cmd}`.
- Preserve símbolos públicos exportados consumidos em outros módulos.
- Mantenha o escopo estritamente restrito a 1 único arquivo por ciclo.
- Consulte e registre aprendizados em `.amb/diarios/deadwood.md`.
"""
            },
            "doc": {
                "title": "📝 Doc: Documentação Técnica & TSDoc",
                "content": f"""# 📝 Doc: Documentação Técnica & TSDoc

Você é o "Doc" 📝 — um especialista em documentação técnica e clareza de código focado em documentar funções públicas com TSDoc/Docstrings precisas no {repo_name}.

---

## 🛡️ Limites e Diretrizes (Boundaries)
- Validação mandatória: `{typecheck_cmd}` e `{build_cmd}`.
- Documente parâmetros, retornos e erros esperados em Português claro.
- Zero alteração em linhas executáveis de código em runtime.
- Consulte e registre aprendizados em `.amb/diarios/doc.md`.
"""
            },
            "order": {
                "title": "🧭 Order: Organização de Funções (Step-Down Rule)",
                "content": f"""# 🧭 Order: Organização de Funções (Step-Down Rule)

Você é o "Order" 🧭 — um especialista em legibilidade e arquitetura limpa que organiza o fluxo das funções seguindo a Step-Down Rule (leitura de cima para baixo) no {repo_name}.

---

## 🛡️ Limites e Diretrizes (Boundaries)
- Validação mandatória: `{typecheck_cmd}` e `{build_cmd}`.
- Organize imports no topo e funções principais antes de utilitárias privadas.
- Consulte e registre aprendizados em `.amb/diarios/order.md`.
"""
            },
            "pixel": {
                "title": "🎨 Pixel: Fidelidade Visual & Design System (Dual-Theme)",
                "content": f"""# 🎨 Pixel: Fidelidade Visual & Design System (Dual-Theme)

Você é o "Pixel" 🎨 — um guardião de Design System focado em garantir que a interface do {repo_name} utilize 100% tokens semânticos e classes do Design System com suporte a Light e Dark Mode.

---

## 🛡️ Limites e Diretrizes (Boundaries)
- Validação mandatória: `{typecheck_cmd}` e `{build_cmd}`.
- Substitua estilos inline e cores arbitrárias por tokens do Design System.
- Preserve fidelidade visual e responsividade.
- Consulte e registre aprendizados em `.amb/diarios/pixel.md`.
"""
            },
            "pure": {
                "title": "🧪 Pure: Funções Puras & Refatoração SRP",
                "content": f"""# 🧪 Pure: Funções Puras & Refatoração SRP

Você é o "Pure" 🧪 — um especialista em engenharia funcional focado em isolar cálculos matemáticos, transformações de dados e regras de negócio em funções puras e testáveis no {repo_name}.

---

## 🛡️ Limites e Diretrizes (Boundaries)
- Validação mandatória: `{typecheck_cmd}` e `{build_cmd}`.
- Isole cálculos determinísticos sem misturar efeitos colaterais de I/O ou banco.
- Consulte e registre aprendizados em `.amb/diarios/pure.md`.
"""
            },
            "relay": {
                "title": "🛰️ Relay: Validador de Contratos e Fluxo Ponta a Ponta",
                "content": f"""# 🛰️ Relay: Validador de Contratos e Fluxo Ponta a Ponta

Você é o "Relay" 🛰️ — um especialista em arquitetura de dados e consistência de contratos ponta a ponta no {repo_name}.
Sua missão é auditar fatias verticais completas (Banco de Dados -> Service -> Controller API -> Client -> UI) garantindo persistência real e zero contratos quebrados.

---

## 🛡️ Limites e Diretrizes (Boundaries)
- Validação mandatória: `{typecheck_cmd}` e `{build_cmd}`.
- Sem mocks estáticos onde rotas reais de API deveriam persistir no banco.
- Consulte e registre aprendizados em `.amb/diarios/relay.md`.
"""
            },
            "sentry": {
                "title": f"👁️ Sentry: Blindagem de Rotas com {schema_validator}",
                "content": f"""# 👁️ Sentry: Blindagem de Rotas com {schema_validator}

Você é o "Sentry" 👁️ — um especialista em contratos de tipagem e validação rigorosa na borda da API no {repo_name}.
Sua missão é auditar routers e endpoints garantindo validação de schemas em todos os payloads (params, queries e body).

---

## 🛡️ Limites e Diretrizes (Boundaries)
- Validação mandatória: `{typecheck_cmd}` e `{build_cmd}`.
- Rejeite payloads malformados com resposta 400 estruturada.
- Consulte e registre aprendizados em `.amb/diarios/sentry.md`.
"""
            }
        }

        # Cria ou atualiza as personas se não existirem
        for key, pdata in templates.items():
            p_file = os.path.join(personas_dir, f"{key}.md")
            if not os.path.exists(p_file):
                with open(p_file, "w", encoding="utf-8") as pf:
                    pf.write(pdata["content"].strip() + "\n")

            # Cria arquivo inicial de diário se não existir
            d_file = os.path.join(diarios_dir, f"{key}.md")
            if not os.path.exists(d_file):
                with open(d_file, "w", encoding="utf-8") as df:
                    df.write(f"# {pdata['title'].split(':')[0]} Diário do {key.capitalize()} (`.amb/diarios/{key}.md`)\n\n"
                             f"Este diário consolida o histórico de aprendizados e padrões identificados no repositório {repo_name}.\n\n---\n")

        # Cria ou atualiza README.md em .amb/
        readme_file = os.path.join(amb_root, "README.md")
        frameworks_str = ', '.join(stack.get('frameworks', [])) or 'Genérico'
        rules_str = stack.get('rules_dir') or 'Nenhuma pasta de regras identificada'
        render_str = 'Configurado via render.yaml' if stack.get('has_render_yaml') else 'Manual / Não configurado'

        readme_content = f"""# 🧭 Personas e Diários de Engenharia (`.amb/`)

Este diretório centraliza a inteligência local, especificações de telas, as **10 Personas Autônomas de Manutenção** e seus respectivos **Diários de Aprendizado** no repositório **{repo_name}**.

---

## 🔍 Resumo do Ambiente do Projeto

| Propriedade | Valor Detectado |
| :--- | :--- |
| 📦 **Repositório GitHub** | `{repo_name}` |
| 🛠️ **Stack Principal** | `{stack.get('type')}` |
| ⚡ **Gerenciador de Pacotes** | `{stack.get('package_manager')}` |
| 🧩 **Frameworks & Libs** | `{frameworks_str}` |
| 📜 **Regras Arquiteturais** | `{rules_str}` |
| 🚀 **Deploy em Nuvem** | `{render_str}` |

---

## 🤖 Catálogo das 10 Personas Oficiais

| Emoji | Persona | Prompt da Persona | Diário de Aprendizado | Objetivo Principal |
| :--- | :--- | :--- | :--- | :--- |
| 📐 | **Align** | [`personas/align.md`](./personas/align.md) | [`diarios/align.md`](./diarios/align.md) | Padronizar envelopes de erro, status codes HTTP semânticos e contratos de backend. |
| 🗼 | **Beacon** | [`personas/beacon.md`](./personas/beacon.md) | [`diarios/beacon.md`](./diarios/beacon.md) | Acessibilidade (a11y), navegação por teclado, `aria-labels` e contraste WCAG AAA. |
| ⚡ | **Bolt** | [`personas/bolt.md`](./personas/bolt.md) | [`diarios/bolt.md`](./diarios/bolt.md) | Performance, redução de latência, eliminação de waterfalls e paralelização assíncrona. |
| 🪓 | **Deadwood** | [`personas/deadwood.md`](./personas/deadwood.md) | [`diarios/deadwood.md`](./diarios/deadwood.md) | Remoção cirúrgica de código morto, métodos não utilizados e imports órfãos. |
| 📝 | **Doc** | [`personas/doc.md`](./personas/doc.md) | [`diarios/doc.md`](./diarios/doc.md) | Documentação técnica TSDoc/Docstrings e sanitização de anotações informais. |
| 🧭 | **Order** | [`personas/order.md`](./personas/order.md) | [`diarios/order.md`](./diarios/order.md) | Organização top-down de funções seguindo o princípio da *Step-Down Rule*. |
| 🎨 | **Pixel** | [`personas/pixel.md`](./personas/pixel.md) | [`diarios/pixel.md`](./diarios/pixel.md) | Fidelidade visual e Design System, eliminando inline styles com suporte a Light/Dark Mode. |
| 🧪 | **Pure** | [`personas/pure.md`](./personas/pure.md) | [`diarios/pure.md`](./diarios/pure.md) | Extração de funções puras determinísticas e conformidade estrita com SRP. |
| 🛰️ | **Relay** | [`personas/relay.md`](./personas/relay.md) | [`diarios/relay.md`](./diarios/relay.md) | Validador de fluxo ponta a ponta (DB -> Service -> API -> Client -> UI) e persistência. |
| 👁️ | **Sentry** | [`personas/sentry.md`](./personas/sentry.md) | [`diarios/sentry.md`](./diarios/sentry.md) | Blindagem de rotas e validação de schemas de entrada na borda da API. |

---

## 🚀 Principais Comandos da CLI `amb`

```bash
# 1. Diagnóstico e Checklist de Chaves
amb check

# 2. Ver o Prompt Mestre de Auto-Configuração de IA
amb prompt

# 3. Inspecionar Schemas do Banco de Dados (Read-Only)
amb schema [modulo]

# 4. Gerar Roteiro Ordenado de Arquivos para a IA
amb context <modulo>

# 5. Listar todas as Personas Disponíveis
amb agent --list

# 6. Executar uma Persona Localmente no Repositório
amb agent --role deadwood

# 7. Despachar uma Persona para a Nuvem do Google Jules (Cria VM + Branch + PR)
amb agent --role bolt --dispatch-jules

# 8. Despachar TODAS as Personas em Lote para a Nuvem
amb agent --all --dispatch-jules

# 9. Iniciar o Sentinela em Tempo Real (Piloto Automático)
amb monitor --auto-approve

# 10. Menu Cognitivo para Resolver Dúvidas de Agentes
amb advisor

# 11. Executar o Pipeline Design-to-Deploy de uma Tela
amb pipeline .amb/prompts/minha_tela.md
```
"""
        with open(readme_file, "w", encoding="utf-8") as rf:
            rf.write(readme_content)


class CognitiveSynthesizer:
    """Usa o Antigravity SDK ou Gemini para resumir regras e especificações do projeto."""

    @staticmethod
    def infer_project_specs(root: str, stack: Dict[str, Any]) -> str:
        """Gera um resumo técnico conciso das diretrizes do projeto."""
        gemini_key = get_env("GEMINI_API_KEY")
        if not gemini_key:
            return "Stack identificada: " + ", ".join(stack.get("frameworks", []))

        prompt = f"""Analise este resumo técnico de um projeto de software e gere 3 diretrizes essenciais de desenvolvimento em 1 parágrafo:
- Tipo: {stack.get('type')}
- Gerenciador: {stack.get('package_manager')}
- Frameworks: {', '.join(stack.get('frameworks', [])) or 'Genérico'}
- Render Deploy: {'Sim' if stack.get('has_render_yaml') else 'Não'}
"""
        try:
            res = subprocess.run(
                ["agy", "-p", prompt],
                cwd=root,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=20,
                check=False
            )
            if res.returncode == 0 and res.stdout.strip():
                return res.stdout.strip()
        except Exception:
            pass

        return f"Projeto {stack.get('type')} com {', '.join(stack.get('frameworks', [])) or 'stack padrão'} utilizando {stack.get('package_manager')}."


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
