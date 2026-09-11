from typing import Dict, Any
import os


class AmbProvisioner:
    """Provisiona e contextualiza dinamicamente as personas e diários na pasta .amb/."""

    @classmethod
    def provision_structure(
        cls, root: str, stack: Dict[str, Any], repo_name: str
    ) -> None:
        """Cria as pastas de personas, diários e prompts se não existirem."""
        amb_root = os.path.join(root, ".amb")
        personas_dir = os.path.join(amb_root, "personas")
        diarios_dir = os.path.join(amb_root, "diarios")
        prompts_dir = os.path.join(amb_root, "prompts")

        for d in [amb_root, personas_dir, diarios_dir, prompts_dir]:
            os.makedirs(d, exist_ok=True)

        # Contexto de Comandos de QA da Stack
        is_node = "node" in stack.get("type", "").lower() or any(
            f in stack.get("frameworks", [])
            for f in ["React", "Next.js", "Hono", "Express", "Vue"]
        )
        is_python = "python" in stack.get("type", "").lower() or any(
            f in stack.get("frameworks", []) for f in ["FastAPI", "Flask", "Django"]
        )

        typecheck_cmd = (
            "npm run typecheck"
            if is_node
            else ("mypy ." if is_python else "verificação de tipos")
        )
        build_cmd = (
            "npm run build"
            if is_node
            else ("pytest" if is_python else "build do projeto")
        )
        # backend_target = "Hono/Express" if is_node else ("FastAPI/Flask" if is_python else "Backend")
        schema_validator = (
            "Zod" if is_node else ("Pydantic" if is_python else "Schema Validator")
        )

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
""",
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
""",
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
""",
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
""",
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
""",
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
""",
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
""",
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
""",
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
""",
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
""",
            },
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
                    df.write(
                        f"# {pdata['title'].split(':')[0]} Diário do {key.capitalize()} (`.amb/diarios/{key}.md`)\n\n"
                        f"Este diário consolida o histórico de aprendizados e padrões identificados no repositório {repo_name}.\n\n---\n"
                    )

        # Cria ou atualiza README.md em .amb/
        readme_file = os.path.join(amb_root, "README.md")
        frameworks_str = ", ".join(stack.get("frameworks", [])) or "Genérico"
        rules_str = stack.get("rules_dir") or "Nenhuma pasta de regras identificada"
        render_str = (
            "Configurado via render.yaml"
            if stack.get("has_render_yaml")
            else "Manual / Não configurado"
        )

        readme_content = f"""# 🧭 Personas e Diários de Engenharia (`.amb/`)

Este diretório centraliza a inteligência local, especificações de telas, as **10 Personas Autônomas de Manutenção** e seus respectivos **Diários de Aprendizado** no repositório **{repo_name}**.

---

## 🔍 Resumo do Ambiente do Projeto

| Propriedade | Valor Detectado |
| :--- | :--- |
| 📦 **Repositório GitHub** | `{repo_name}` |
| 🛠️ **Stack Principal** | `{stack.get("type")}` |
| ⚡ **Gerenciador de Pacotes** | `{stack.get("package_manager")}` |
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
