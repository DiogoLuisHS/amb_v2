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

Todo agente de IA (incluindo o Jules) deve obedecer estritamente aos seguintes invariantes:

### 1. Limite de Linhas e Atomização (Regra 02)
- **Teto Recomendado:** Arquivos entre **100 e 250 linhas**.
- **Teto Máximo:** Nenhum arquivo deve ultrapassar **300 linhas**. Se atingir esse limite, decomponha o módulo em um subpacote atômico com submódulos de responsabilidade única.

### 2. Responsabilidade Única (SRP) e Zero Redundância (DRY)
- Cada classe ou função deve fazer apenas uma coisa e fazê-la bem.
- Nunca crie arquivos genéricos do tipo `utils.py` ou `helpers.py`. Crie submódulos especializados e descritivos.

### 3. Tipagem Estrita e Qualidade de Código
- Todo método e função deve possuir `type hints` completos (`typing.Optional`, `List`, `Dict`, `Union`, etc.).
- Não utilize `from modulo import *`. Todo import deve ser explícito no topo do arquivo.

### 4. Compatibilidade Multiplataforma e Tolerância a Encodings
- Sempre especifique `encoding="utf-8", errors="replace"` em operações de leitura e escrita de arquivos (`open()`, `Path.write_text()`) para compatibilidade perfeita com Windows, Linux e macOS.

---

## 🔍 3. Comandos de Validação e QA Local

Antes de concluir qualquer tarefa ou abrir Pull Request, o Jules deve garantir que todos os comandos abaixo passem com 100% de sucesso na VM:

```bash
# 1. Executar a suíte de testes unitários (obrigatório manter 100% verde):
pytest -q

# 2. Checagem de sintaxe e compilação rápida:
python -m py_compile cli.py

# 3. Auditar conformidade arquitetural contra as regras do repositório:
python -m amb_cli.cli validate <arquivo_modificado>
```

---

## 📋 4. Convenções de Pull Request e Commits

- **Commits Convencionais:** Prefixar mensagens com tipo semântico: `feat:`, `fix:`, `refactor:`, `test:`, `docs:`, `chore:`.
- **Testes Dedicados:** Toda nova funcionalidade deve obrigatoriamente incluir um arquivo de teste unitário correspondente em `tests/test_<modulo>.py`.
- **Atomização de PRs:** Mantenha os Pull Requests cirúrgicos e focados em estritamente um objetivo para permitir auto-merge seguro.
