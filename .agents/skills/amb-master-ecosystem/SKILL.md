---
name: amb-master-ecosystem
description: >-
  Authoritative master reference and operational cheatsheet for the AMB_V2 engineering CLI and autonomous multi-agent ecosystem. Use when navigating amb CLI commands (check, setup, gui, agent, jules, stitch, pipeline, agy, git), understanding repository architecture in amb_cli/, batch development via -p, and troubleshooting autonomous pipelines.
---

# 🚀 AMB_V2 — Master Ecosystem & Operational Cheatsheet

Guia definitivo e fonte de autoridade central para operação da **CLI global `amb`**, arquitetura de software em `amb_cli/` e orquestração de agentes autônomos (Google Jules, Antigravity/Gemini e Google Stitch).

---

## 🏛️ 1. Arquitetura Modular (`amb_cli/`)

O ecossistema `amb_v2` é organizado em módulos altamente atomizados (todos <= 300 linhas), seguindo estritamente o Princípio da Responsabilidade Única (SRP):

```text
amb_v2/
├── pyproject.toml / setup.py        # Configuração de build e comando global 'amb'
├── amb_cli/                         # Pacote Python principal da CLI (92 módulos atomizados)
│   ├── cli.py                       # Ponto de entrada CLI (Single Source of Truth)
│   ├── cli_modules/                 # Handlers e parsers modulares (SRP)
│   │   ├── cli_parsers.py           # Declaração modular de argumentos (argparse)
│   │   ├── cli_handlers.py          # Despacho enxuto de subcomandos
│   │   └── handlers_core/           # Handlers desacoplados (antigravity, git, jules, stitch)
│   ├── core/                        # Núcleo de infraestrutura (bootstrap, env, exceptions, logger, diagnostics)
│   ├── workspace/                   # Governança do repo consumidor (project_context, rules_manager, design_tokens, setup/)
│   ├── gui/                         # Assistente Gráfico Nativo Tkinter (wizard_app.py, wizard_core/)
│   ├── architecture/                # Inteligência de repositório (ai_context_builder.py, db_schema_reader.py)
│   ├── agents/                      # Orquestração de agentes (autonomous_loop.py, auto_reply.py, local_agent_runner.py)
│   ├── integrations/                # Clientes oficiais (jules, stitch, antigravity, git, common/base_google_client)
│   └── pipeline/                    # Orquestrador Design-to-Deploy (pipeline.py, quality_gatekeeper.py)
├── .agents/rules/                   # Regras de governança arquitetural do ecossistema
├── .amb/                            # Configurações locais, diários cognitivos e personas
└── tests/                           # Suíte de testes unitários (159 testes, 100% green)
```

---

## 🧭 2. Matriz Completa de Comandos da CLI (`amb`)

### ⚙️ Configuração, Diagnóstico & GUI
| Comando | Descrição & Uso Recomendado |
| :--- | :--- |
| `amb check [--json]` | Diagnóstico completo de ambiente: API keys, Git, GitHub CLI (`gh`), binários de QA e proteção no `.gitignore`. |
| `amb setup [--auto] [-f] [--path <dir>]` | Assistente de inicialização de projetos consumidores: detecta stack, infere QA e gera `.amb/`. |
| `amb prompt [-s "<ideia>"] [-r <role>]` | Imprime prompt mestre ou sintetiza ideia informal em prompt estruturado com Gemini. |
| `amb config --gemini-confirm <on\|off>` | Liga ou desliga a exigência de confirmação antes de disparar requisições ao Gemini. |
| `amb gui` (ou `amb ui`) | Abre a interface gráfica interativa nativa (Tkinter) com runner dinâmico e editor de `.env`. |

### 🤖 Agentes, Personas & Loop Autônomo (`amb agent`)
| Comando | Descrição & Uso Recomendado |
| :--- | :--- |
| `amb agent -p <pasta_ou_arquivo>` | **Desenvolvimento em Lote:** Executa uma pasta inteira de prompts numerados (ex: `-p .amb/prompts/`) sequencialmente com auto-reply e auto-merge. |
| `amb agent -p <pasta> --loop` | Ciclo infinito iterando sobre a pasta de prompts. |
| `amb agent --list` (`-l`) | Lista todas as personas disponíveis no projeto ativo (`.amb/personas/`). |
| `amb agent --role <nome>` | Despacha persona para o Google Jules na nuvem (Cloud VM + Branch + PR). |
| `amb agent --role <nome> --agy` | Executa a persona **localmente** via Antigravity SDK (`agy` CLI) sem consumir cota Jules. |
| `amb agent --all --loop` | Ciclo contínuo iterando sobre todas as personas cadastradas. |
| `amb agent --loop --max-cycles <N>` | Limita o loop contínuo a N ciclos de entrega completos. |
| `amb agent --loop --branch <branch>` | Define o branch alvo para a sessão Jules (padrão: branch atual ou `develop`). |
| `amb agent --loop --modules <m1,m2>` | Rotaciona o foco entre submódulos a cada ciclo com injeção automática de `amb context`. |

### ☁️ Google Jules Cloud (`amb jules`)
| Comando | Descrição & Uso Recomendado |
| :--- | :--- |
| `amb jules status [--json]` | Diagnóstico de conexão, credenciais e sessões ativas no Jules. |
| `amb jules sources [--json]` | Lista fontes e repositórios vinculados na conta Jules. |
| `amb jules list [--limit N] [--state S]` | Lista sessões do repositório ativo com paginação e filtros. |
| `amb jules get <id_ou_url> [--watch]` | Detalhes da sessão com streaming de logs ao vivo (`--watch`). |
| `amb jules create -p "<prompt>" [-t "<titulo>"]` | Cria nova sessão na nuvem em branch dedicada. |
| `amb jules reply <id> [-m "<msg>"] [-y]` | Responde dúvidas do agente (manual ou auto-resposta via Gemini Advisor). |
| `amb jules approve <id> [--force]` | Aprova plano de execução (`:approvePlan`). |
| `amb jules merge <id>` | Converte Draft PR em Ready (`gh pr ready`), aprova, executa QA local e mescla. |
| `amb jules merge --auto-latest` | Detecta e mescla o PR aberto mais recente da sessão. |
| `amb jules clean [--failed] [--merged] [-f]` | Limpa sessões encerradas ou com falha fatal na nuvem. |

> **Normalização de IDs:** Todos os comandos aceitam ID numérico puro (`175...`), formato REST (`sessions/175...`) ou URL web (`https://jules.google.com/session/175...`).

### 🎨 Google Stitch SDK (`amb stitch`)
| Comando | Descrição & Uso Recomendado |
| :--- | :--- |
| `amb stitch list` | Lista telas do projeto Stitch ativo. |
| `amb stitch generate -p "<prompt>" [-d <device>]` | Gera nova tela (`MOBILE`, `DESKTOP`, `TABLET`, `AGNOSTIC`). |
| `amb stitch refine -s <id> -p "<prompt>"` | Refina tela existente com novos tokens e ajustes. |
| `amb stitch get -s <id> [-o <arquivo>]` | Exporta DOM HTML, CSS e metadados da tela. |
| `amb stitch variants -s <id> -c <N>` | Gera variantes visuais exploratórias (1 a 5 variações). |
| `amb stitch download -o <dir>` | Baixa assets visuais e HTMLs do projeto. |
| `amb stitch sync [-f design.md]` | Sincroniza design tokens com o Design System oficial. |
| `amb stitch call <tool> '<json>'` | Invoca qualquer ferramenta oficial do Stitch SDK via JSON-RPC. |

### 🚀 Pipeline Design-to-Deploy (`amb pipeline`)
| Comando | Descrição & Uso Recomendado |
| :--- | :--- |
| `amb pipeline -s <stitch.md> -j <jules.md>` | **Pipeline Completo:** Prompts separados (SRP) para design visual no Stitch e engenharia no Jules. |
| `amb pipeline -j <jules.md> --skip-stitch` | Executa apenas a etapa de engenharia de backend/código sem interface. |
| `amb pipeline --resume-session <id>` | Retoma o monitoramento e QA de uma sessão Jules já iniciada. |
| `amb pipeline -s <s.md> -j <j.md> -y` | Modo 100% autônomo sem pausas no Gatekeeper 1. |

### 🧠 Antigravity & Regras (`amb agy`)
| Comando | Descrição & Uso Recomendado |
| :--- | :--- |
| `amb agy status [--json]` | Diagnóstico do runtime cognitivo, agy CLI e regras ativas. |
| `amb agy rules [--content] [--json]` | Inspeciona regras arquiteturais ativas via `RulesManager`. |
| `amb agy prompt -i "<ideia>" -r <role>` | Sintetiza ideia em prompt formal com regras ativas. |
| `amb agy validate <arquivo> [--json]` | Audita conformidade arquitetural contra as regras do repositório. |
| `amb agy run "<prompt>" [-m <modelo>]` | Executa inferência cognitiva arbitrária via Gemini REST. |

### 🐙 Git & Pull Requests (`amb git`)
| Comando | Descrição & Uso Recomendado |
| :--- | :--- |
| `amb git status [--json]` | Exibe status detalhado do repositório local e upstream. |
| `amb git sync [-r origin] [-b branch]` | Executa fetch + pull com auto-stash transparente. |
| `amb git diff [--cached]` | Exibe diff unificado de arquivos alterados. |
| `amb git pr list [--no-drafts]` | Lista Pull Requests abertos no GitHub. |
| `amb git pr get <id>` | Detalhes estruturados, checks e comentários do PR. |
| `amb git pr create -t "<titulo>" [-b "<body>"]` | Abre Pull Request no GitHub. |
| `amb git pr ready <id>` | Marca Draft PR como pronto para revisão. |
| `amb git pr approve <id>` | Aprova formalmente o Pull Request. |
| `amb git pr merge <id>` | Executa merge via squash e exclui branch remota. |

---

## ⚡ 3. Padrões Operacionais & Boas Práticas

1. **Desenvolvimento em Lote por Prompts (`.amb/prompts/`):**
   - Divida tarefas complexas em arquivos numerados: `01_db_schema.md`, `02_services.md`, `03_ui_components.md`.
   - Execute: `amb agent -p .amb/prompts/`.
   - Cada arquivo é processado até a criação do PR, QA aprovado e auto-merge antes de avançar para o próximo.

2. **Injeção de Contexto Automática:**
   - O comando `amb agent --loop` executa automaticamente `ai_context_builder.py` para injetar o grafo de dependências e roteiro arquitetural no prompt do Jules, economizando até 30 minutos de exploração por sessão.

3. **Compatibilidade com Windows:**
   - Todos os subprocessos usam `shutil.which()` para resolução de executáveis (`npm.cmd`, `yarn.cmd`) com `shell=False`.
   - Normalização de encoding UTF-8 em todos os I/O de arquivo e terminal.

4. **Tratamento Resiliente de APIs:**
   - Retries automáticos com jitter exponencial via `BaseGoogleClient`.
   - Mascaramento rigoroso de chaves sensíveis em logs e dumps JSON.
