# 📚 AMB_V2 - Arquitetura de Pastas e Documentação

Este diretório centraliza a documentação técnica, especificações de subsistemas e guias de integração do ecossistema AMB_V2.

## 🏗️ Topologia de Diretórios do Projeto

Após a refatoração modular v2.3.0, o repositório AMB_V2 está estruturado de forma desacoplada:

```
amb_v2/
├── amb_cli/                    # 🚀 PACOTE PRINCIPAL DE CÓDIGO FONTE
│   ├── agents/                 # Orquestração de Agentes (Jules, Gemini, Local)
│   ├── architecture/           # Construtores de Contexto e Mapeamento de Arquitetura
│   ├── cli_modules/            # Handlers, Parsers e Notificadores do CLI
│   ├── config/                 # Bootstrap, Gerenciador de Regras e Provisionamento
│   ├── gui/                    # Interface Visual e Wizard Interativo
│   ├── integrations/           # Integrações Cloud (Jules, Stitch, Antigravity, Git)
│   ├── pipeline/               # Quality Gatekeeper e Pipeline de Entrega
│   ├── cli.py                  # Ponto de entrada do CLI
│   ├── amb_bootstrap.py        # Bootstrap canônico do pacote
│   ├── __init__.py             # Metadados do pacote amb_cli
│   └── __main__.py             # Suporte a `python -m amb_cli`
│
├── docs/                       # 📖 DOCUMENTAÇÃO TÉCNICA E GUIAS
│   └── README.md               # Este índice
│
├── tests/                      # 🧪 SUÍTE DE TESTES UNITÁRIOS E DE INTEGRAÇÃO
│   ├── test_amb_cli.py
│   ├── test_bootstrap.py
│   ├── test_git_service.py
│   ├── test_jules_client.py
│   ├── test_rules_manager.py
│   └── test_stitch_client.py
│
├── .agents/                    # 🤖 Antigravity Skills e Instruções
├── .amb/                       # ⚙️ Configurações de Projeto, Diário e Personas
├── cli.py                      # 🔄 Shim de Compatibilidade Raiz (`python cli.py`)
├── amb_bootstrap.py            # 🔄 Shim de Compatibilidade Raiz (`import amb_bootstrap`)
├── pyproject.toml              # 📦 Especificação de Pacote PEP 517/621
├── setup.py                    # 📦 Script de Instalação e Entrypoints
└── README.md                   # 📄 Visão Geral e Guia Rápido
```

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

3. **Via Script Raiz (Legado/Compatibilidade):**
   ```bash
   python cli.py --help
   python cli.py check
   ```
