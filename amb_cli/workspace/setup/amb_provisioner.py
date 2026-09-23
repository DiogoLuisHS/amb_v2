import os
from typing import Dict, Any, Optional


class AmbProvisioner:
    """Provisiona a estrutura .amb/, personas de exemplo, diários e proteção de ambiente."""

    @classmethod
    def provision_structure(
        cls,
        root: str,
        stack: Dict[str, Any],
        repo_name: str,
        qa_commands: Optional[Dict[str, str]] = None,
        force: bool = False
    ) -> None:
        """Cria as pastas de personas, diários, prompts e proteção de segurança (.gitignore, .env.example)."""
        amb_root = os.path.join(root, ".amb")
        personas_dir = os.path.join(amb_root, "personas")
        diarios_dir = os.path.join(amb_root, "diarios")
        prompts_dir = os.path.join(amb_root, "prompts")

        for d in [amb_root, personas_dir, diarios_dir, prompts_dir]:
            os.makedirs(d, exist_ok=True)

        # 1. Cria .gitkeep em prompts para versionamento limpo
        gitkeep_prompts = os.path.join(prompts_dir, ".gitkeep")
        if not os.path.exists(gitkeep_prompts):
            with open(gitkeep_prompts, "w", encoding="utf-8") as f:
                f.write("")

        # 2. Contexto de Comandos de QA da Stack
        qa = qa_commands or {}
        typecheck_cmd = qa.get("typecheck") or qa.get("build") or "npm run typecheck / mypy ."
        build_cmd = qa.get("build") or qa.get("test") or "npm run build / pytest"

        # 3. Persona Única Genérica de Exemplo (Engineer)
        engineer_template = {
            "title": "🤖 Engineer: Autonomous Software Engineer",
            "content": f"""# 🤖 Engineer: Autonomous Software Engineer

Você é o "Engineer" 🤖 — o Engenheiro de Software Autônomo responsável pela continuidade, arquitetura e aperfeiçoamento do repositório **{repo_name}**.

---

## 🎯 Sua Missão
1. Analisar os arquivos do escopo e identificar débitos técnicos, bugs ou novas funcionalidades necessárias.
2. Implementar soluções limpas, modulares e de alta coesão seguindo rigorosamente o princípio da responsabilidade única (SRP).
3. Preservar convenções arquiteturais existentes e manter estilo consistente de código.
4. Abrir Pull Requests concisos e bem documentados.

---

## 🛡️ Diretrizes e Limites Mandatórios (Boundaries)
- **Validação de QA**: Antes de concluir o turno ou abrir o PR, garanta que o código passe com 0 erros em:
  - `{typecheck_cmd}`
  - `{build_cmd}`
- **Tipagem Estrita**: 0 `any` implícito, interfaces explícitas e contratos de dados seguros.
- **Escopo Cirúrgico**: Evite alterações desnecessárias fora do escopo da tarefa solicitada.
- **Diário de Bordo**: Consulte lições anteriores e registre novos aprendizados em `.amb/diarios/engineer.md`.
"""
        }

        # Cria ou atualiza a persona de exemplo
        p_file = os.path.join(personas_dir, "engineer.md")
        if not os.path.exists(p_file) or force:
            with open(p_file, "w", encoding="utf-8") as pf:
                pf.write(engineer_template["content"].strip() + "\n")

        # Cria diário inicial de aprendizados se não existir
        d_file = os.path.join(diarios_dir, "engineer.md")
        if not os.path.exists(d_file):
            with open(d_file, "w", encoding="utf-8") as df:
                df.write(
                    f"# 🤖 Diário de Aprendizado do Engineer (`.amb/diarios/engineer.md`)\n\n"
                    f"Este diário consolida o histórico de aprendizados, decisões arquiteturais e padrões identificados no repositório {repo_name}.\n\n"
                    f"---\n"
                )

        # 4. Criação do .env.example sanitizado
        env_example_path = os.path.join(root, ".env.example")
        if not os.path.exists(env_example_path) or force:
            example_content = f"""# ==============================================================================
# 🔑 AMB_V2 - Template de Variáveis de Ambiente do Projeto
# Copie este arquivo para .env e preencha suas chaves:
#   cp .env.example .env
# ==============================================================================

# Repositório GitHub ativo (owner/repo)
GITHUB_REPOSITORY={repo_name}

# Google Jules Cloud API Key (obtenha em https://jules.google.com)
JULES_API_KEY=

# Google Gemini / Antigravity API Key (obtenha em https://aistudio.google.com)
GEMINI_API_KEY=

# Google Stitch SDK (opcional, para prototipagem de UI)
STITCH_API_KEY=
STITCH_PROJECT_ID=
"""
            with open(env_example_path, "w", encoding="utf-8") as ef:
                ef.write(example_content)

        # 5. Proteção de Segurança: Garantir .env no .gitignore
        cls.ensure_gitignore_security(root)

        # 6. Criação de .amb/README.md informativo
        cls.write_amb_readme(amb_root, repo_name, stack, qa)

    @classmethod
    def ensure_gitignore_security(cls, root: str) -> None:
        """Garante que .env e artefatos de telemetria local estejam no .gitignore de forma não-destrutiva."""
        gitignore_path = os.path.join(root, ".gitignore")
        required_patterns = [
            ".env",
            ".env.local",
            ".amb/loop_state.json",
            ".amb/telemetry.jsonl",
            "__pycache__/",
        ]

        existing_lines = []
        if os.path.exists(gitignore_path):
            try:
                with open(gitignore_path, "r", encoding="utf-8", errors="replace") as f:
                    existing_lines = [line.strip() for line in f.readlines()]
            except Exception:
                existing_lines = []

        to_add = [p for p in required_patterns if p not in existing_lines]
        if to_add:
            mode = "a" if os.path.exists(gitignore_path) else "w"
            with open(gitignore_path, mode, encoding="utf-8") as f:
                if existing_lines and not existing_lines[-1] == "":
                    f.write("\n")
                f.write("# AMB_V2 - Arquivos Locais e Segredos de Ambiente\n")
                for item in to_add:
                    f.write(f"{item}\n")

    @classmethod
    def write_amb_readme(
        cls,
        amb_root: str,
        repo_name: str,
        stack: Dict[str, Any],
        qa: Dict[str, str]
    ) -> None:
        """Gera documentação contextualizada dentro de .amb/."""
        readme_file = os.path.join(amb_root, "README.md")
        frameworks_str = ", ".join(stack.get("frameworks", [])) or "Genérico"
        rules_str = stack.get("rules_dir") or "Nenhuma pasta de regras identificada"
        qa_lines = "\n".join([f"- **{k.title()}**: `{v}`" for k, v in qa.items()]) if qa else "- *Nenhum comando de QA configurado*"

        readme_content = f"""# 🧭 AMB_V2 — Configuração e Inteligência Local (`.amb/`)

Este diretório centraliza a configuração do projeto, personas autônomas e diários de aprendizado para o repositório **{repo_name}**.

---

## 🔍 Resumo da Stack Detectada

| Propriedade | Valor |
| :--- | :--- |
| 📦 **Repositório GitHub** | `{repo_name}` |
| 🛠️ **Stack Principal** | `{stack.get('type')}` |
| ⚡ **Gerenciador de Pacotes** | `{stack.get('package_manager')}` |
| 🧩 **Frameworks & Libs** | `{frameworks_str}` |
| 📜 **Regras Arquiteturais** | `{rules_str}` |

### 🛡️ Comandos de QA Configurados:
{qa_lines}

---

## 🤖 Personas Autônomas (`.amb/personas/`)

O AMB_V2 utiliza personas em formato Markdown como especialistas no código:
- **`personas/engineer.md`**: Persona genérica de referência (Engenheiro de Software Autônomo).
- **Como adicionar novas personas**: Basta criar um arquivo `.md` em `.amb/personas/` (ex: `security.md`, `refactor.md`, `qa.md`) com a instrução desejada.
- O AMB descobre dinamicamente qualquer arquivo `.md` presente nesta pasta!

---

## 🚀 Comandos Principais da CLI `amb`

```bash
# 1. Diagnóstico completo de saúde do ambiente:
amb check

# 2. Listar personas disponíveis:
amb agent --list

# 3. Executar o engenheiro autônomo localmente:
amb agent --role engineer

# 4. Despachar para a VM em nuvem do Google Jules:
amb agent --role engineer --loop

# 5. Desenvolvimento autônomo por pasta de prompts (em lote com auto-merge):
amb agent -p .amb/prompts/

# 6. Iniciar o sentinela de vigilância contínua:
amb monitor --auto-approve
```
"""
        with open(readme_file, "w", encoding="utf-8") as rf:
            rf.write(readme_content)
