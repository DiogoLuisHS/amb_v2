# 📚 AMB_V2 — Documentação e Arquitetura do Projeto

Este diretório centraliza a documentação técnica, especificações de subsistemas, histórico de lançamentos e o backlog de melhorias futuras do ecossistema AMB_V2.

---

## 📑 Documentos Disponíveis

- **[`CHANGELOG.md`](./CHANGELOG.md):** Histórico completo de versões, novas funcionalidades, refatorações atômicas e correções de bugs.
- **[`SUGGESTIONS.md`](./SUGGESTIONS.md):** Backlog de sugestões técnicas, melhorias de DX e novas capacidades ainda não implementadas.
- **[`../amb_cli/gui/README.md`](../amb_cli/gui/README.md):** Documentação do Assistente Gráfico Nativo (Tkinter UI Wizard).
- **[`../amb_cli/pipeline/README.md`](../amb_cli/pipeline/README.md):** Especificação do orquestrador Design-to-Deploy (Stitch + Jules).

---

## 🏗️ Topologia Atual do Repositório

```text
amb_v2/
├── amb_cli/                    # 🚀 PACOTE PRINCIPAL DE CÓDIGO FONTE (92 arquivos, 0 > 300 linhas)
│   ├── agents/                 # Orquestração de Agentes (Jules, Gemini, Local)
│   │   ├── auto_reply_core/    # Núcleo turn-by-turn e aconselhamento cognitivo
│   │   └── loop_core/          # Despachante de ciclos e assistente de sessão
│   ├── architecture/           # Construtor de Contexto e Mapeamento de Schemas DB
│   │   └── context_core/       # Constantes e configurações de camadas
│   ├── cli_modules/            # Handlers, Parsers e Notificadores do CLI
│   │   └── handlers_core/      # Handlers desacoplados por domínio
│   ├── core/                   # Núcleo de Infraestrutura do Framework AMB (bootstrap, logger, env, diagnostics)
│   ├── workspace/              # Contexto e Governança do Projeto Consumidor
│   │   └── setup/              # Analisador de projetos, provisionador .amb/ e wizard
│   ├── gui/                    # Assistente Gráfico Nativo (Tkinter UI Wizard)
│   │   └── wizard_core/        # Runner dinâmico e gestor de .env
│   ├── integrations/           # Clientes Cloud (Jules, Stitch, Antigravity, Git)
│   │   ├── antigravity/        # Motor cognitivo Gemini e regras ativas
│   │   ├── jules/              # Cliente REST e sentinela do Google Jules
│   │   ├── stitch/             # Cliente oficial para Google Stitch SDK
│   │   └── git/                # GitService local e automação da GitHub CLI (gh)
│   └── pipeline/               # Orquestrador Design-to-Deploy
│       └── pipeline_core/      # Estágio de design Stitch e construtor de prompts
│
├── _docs/                      # 📖 DOCUMENTAÇÃO TÉCNICA E HISTÓRICO
│   ├── CHANGELOG.md            # Histórico consolidado de alterações
│   ├── SUGGESTIONS.md          # Backlog de propostas não implementadas
│   └── README.md               # Este índice
│
├── tests/                      # 🧪 SUÍTE DE TESTES UNITÁRIOS (158 testes, 100% green)
│   ├── test_ai_context_builder.py
│   ├── test_alert_notifier.py
│   ├── test_antigravity_integration.py
│   ├── test_auto_reply.py
│   ├── test_auto_reply_srp.py
│   ├── test_base_google_client.py
│   ├── test_bootstrap.py
│   ├── test_cli_commands.py
│   ├── test_config.py
│   ├── test_db_schema_reader.py
│   ├── test_git_service.py
│   ├── test_gui_wizard.py
│   ├── test_jules_integration.py
│   ├── test_merge_session_pr.py
│   ├── test_pipeline.py
│   ├── test_quality_gatekeeper.py
│   ├── test_rules_manager.py
│   ├── test_setup_and_analyzer.py
│   └── test_stitch_integration.py
│
├── .agents/rules/              # 🤖 Regras de Governança Arquitetural do Ecossistema
├── .amb/                       # ⚙️ Configurações Locais, Diário de Aprendizado e Personas
├── cli.py                      # 🔄 Shim Raiz de Compatibilidade (`python cli.py`)
├── amb_bootstrap.py            # 🔄 Shim Raiz de Compatibilidade (`import amb_bootstrap`)
├── test_check.py               # 🧪 Smoke Test Rápido de Bootstrap e Imports
├── pyproject.toml              # 📦 Especificação de Pacote PEP 517/621
├── setup.py                    # 📦 Script de Instalação e Entrypoints
└── README.md                   # 📄 Documentação Principal e Guia de Uso
```

---

## 🚀 Modos de Execução Suportados

1. **Via CLI global instalada:**
   ```bash
   amb --help
   amb check
   ```

2. **Via Módulo Python:**
   ```bash
   python -m amb_cli --help
   python -m amb_cli check
   ```

3. **Via Script Raiz (Compatibilidade):**
   ```bash
   python cli.py --help
   python cli.py check
   ```
