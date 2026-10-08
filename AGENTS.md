# 🤖 AGENTS.md — Diretrizes de Engenharia e Convenções do AMB_V2

Este arquivo é a fonte canônica de instruções para o **Google Jules**, agentes do **Antigravity** e desenvolvedores trabalhando no repositório `AMB_V2`.

---

## 🧭 1. Visão Geral do Repositório

O **AMB_V2** é um ecossistema global de automação de engenharia, orquestração de agentes autônomos e integração contínua para monorepos e aplicações modernas. Ele disponibiliza a CLI global `amb`.

### 📂 Mapa Arquitetural das Camadas
- `amb_cli/core/`: Fundações centrais do framework (logging, tratamento de erros, `ConfigManager` singleton, `LocalTelemetry`, `ConsolePresenter`).
- `amb_cli/workspace/`: Contexto do repositório alvo (`amb_project.json`, `rules_manager.py`, setup dinâmico de stacks).
- `amb_cli/integrations/`: Clientes e adaptadores externos:
  - `jules/`: Cliente REST do Google Jules, `SessionState`, `SessionMonitor`, watcher e sentinelas.
  - `stitch/`: Google Stitch SDK para geração e refinamento de interfaces visuais.
  - `git/`: `GitService` para branches, PRs, auto-stash e merges via GitHub CLI (`gh`).
  - `antigravity/`: Backends cognitivos do Gemini e governança de regras.
- `amb_cli/agents/`: Orquestradores autônomos (`autonomous_loop.py`, `LoopStateMachine`, `PersonaEngine`, auto-reply).
- `amb_cli/pipeline/`: Pipeline Design-to-Deploy, `QualityGatekeeper` e `LocalQASandbox`.
- `amb_cli/cli_modules/`: Parsers (`cli_parsers.py`), handlers dedicados e despacho unificado.
- `tests/`: Suíte abrangente de testes unitários isolados com mocks rápidos via `pytest`.

---

## 📐 2. Regras Rígidas de Engenharia de Software

Todo agente de IA (incluindo o Jules) deve obedecer estritamente às regras canônicas do repositório catalogadas em [`.agents/rules/`](./.agents/rules/):

1. **[Regra 01: SRP e Separação de Camadas](./.agents/rules/01_single_responsibility.md)** — Cada módulo tem uma única responsabilidade; sem catch-alls ou utils genéricos.
2. **[Regra 02: Atomização e Limite de 300 Linhas](./.agents/rules/02_atomization_and_ai_context.md)** — Arquivos entre 100 e 250 linhas, teto máximo rígido de 300 linhas.
3. **[Regra 03: Zero Redundância (DRY)](./.agents/rules/03_dry_and_zero_redundancy.md)** — Sem código duplicado; use abstrações e enums canônicos.
4. **[Regra 04: Tipagem Estrita e Exceções AmbError](./.agents/rules/04_code_quality_and_typing.md)** — Tipagem explícita com `typing` e tratamento robusto de erros.
5. **[Regra 05: Documentação e Docstrings Concisas](./.agents/rules/05_concise_documentation.md)** — Documentação clara e enxuta, sem prolixidade.
6. **[Regra 06: Segurança Git e Retrocompatibilidade](./.agents/rules/06_git_safety_and_compatibility.md)** — Operações seguras no Git e preservação da branch base.
7. **[Manifesto Completo AMB Standards](./.agents/rules/amb_standards.md)** — Padrões globais de arquitetura e qualidade.

> **Tolerância a Encodings (Windows/Multiplataforma):** Sempre utilize `encoding="utf-8", errors="replace"` em operações de leitura e escrita de arquivos (`open()`, `Path.write_text()`).

---

## 🔍 3. Comandos de Validação e QA Local

Antes de concluir qualquer tarefa ou abrir Pull Request, o Jules deve garantir que todos os comandos abaixo passem com 100% de sucesso na VM:

```bash
# 1. Executar a suíte de testes unitários (obrigatório manter 100% verde):
pytest -q

# 2. Checagem de sintaxe e compilação do core:
python -m py_compile amb_cli/cli.py cli.py

# 3. Auditar conformidade arquitetural contra as regras do repositório:
python -m amb_cli.cli validate <arquivo_modificado>
```

---

## 📋 4. Convenções de Pull Request e Commits

- **Commits Convencionais:** Prefixar mensagens com tipo semântico: `feat:`, `fix:`, `refactor:`, `test:`, `docs:`, `chore:`.
- **Testes Dedicados:** Toda nova funcionalidade deve obrigatoriamente incluir um arquivo de teste unitário correspondente em `tests/test_<modulo>.py`.
- **Atomização de PRs:** Mantenha os Pull Requests cirúrgicos e focados em estritamente um objetivo para permitir auto-merge seguro via `amb jules merge`.
