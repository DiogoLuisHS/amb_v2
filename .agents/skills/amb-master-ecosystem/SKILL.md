---
name: amb-master-ecosystem
description: >-
  Authoritative master reference and operational cheatsheet for developing any project using the global AMB_V2 CLI. Use when navigating amb CLI commands (check, setup, gui, agent, jules, stitch, pipeline, agy, git, schema, context), configuring .amb/ in consumer repositories, batch prompt development via -p, and troubleshooting autonomous pipelines.
---

# 🚀 AMB_V2 — Master Developer & CLI Cheatsheet

Guia definitivo de utilização da **CLI global `amb`** para desenvolver, orquestrar agentes autônomos, gerar telas com IA e automatizar a entrega contínua em **qualquer repositório consumidor**.

---

## 📌 1. Como o AMB Opera em Qualquer Projeto

O AMB_V2 é instalado globalmente no seu sistema (`pip install -e /caminho/para/amb_v2`) e pode ser executado dentro do terminal de **qualquer repositório**:
- **Descoberta Automática de Raiz:** O executável `amb` detecta a raiz do projeto onde você está (`.git`, `package.json`, `pyproject.toml`).
- **Configuração do Projeto (`.amb/`):** Cada projeto mantém suas personas, diários cognitivos e comandos de QA em uma pasta local `.amb/`.
- **Credenciais e Ambiente (`.env`):** Lê as chaves de API (`JULES_API_KEY`, `GEMINI_API_KEY`, `STITCH_API_KEY`, `GITHUB_REPOSITORY`) do `.env` do projeto ativo ou do ambiente global.

```bash
# Inicializar o AMB no seu projeto atual:
amb setup

# Diagnosticar o status das ferramentas e credenciais:
amb check

# Abrir o Assistente Gráfico Nativo (Runner + editor de .env):
amb gui
```

---

## 🧭 2. Catálogo Completo de Comandos (`amb`)

### ⚙️ Configuração, Diagnóstico & GUI
| Comando | Descrição & Uso no Projeto |
| :--- | :--- |
| `amb check [--json]` | Diagnóstico de saúde do projeto: valida API keys, Git, GitHub CLI (`gh`), binários de QA e proteção no `.gitignore`. |
| `amb setup [--auto] [-f]` | Detecta a stack do projeto, infere comandos de teste/build e cria a pasta `.amb/`. |
| `amb prompt [-s "<ideia>"]` | Imprime o prompt mestre ou sintetiza uma ideia informal em prompt arquitetural formal via Gemini. |
| `amb config --gemini-confirm <on\|off>` | Habilita ou desabilita a confirmação prévia para chamadas autônomas ao Gemini. |
| `amb gui` (ou `amb ui`) | Abre a interface gráfica interativa (Tkinter) para montar comandos e editar variáveis do `.env`. |

### 🤖 Agentes Autônomos & Personas (`amb agent`)
| Comando | Descrição & Uso no Projeto |
| :--- | :--- |
| `amb agent -p <pasta_ou_arquivo>` | **Desenvolvimento em Lote:** Executa uma pasta inteira de prompts numerados (ex: `-p .amb/prompts/`) sequencialmente com auto-reply e auto-merge. |
| `amb agent -p <pasta> --loop` | Ciclo infinito iterando sobre os prompts da pasta. |
| `amb agent --list` (`-l`) | Lista as personas cadastradas no projeto (`.amb/personas/`). |
| `amb agent --role <nome>` | Despacha persona para o Google Jules na nuvem (cria VM, branch dedicada e abre PR). |
| `amb agent --role <nome> --agy` | Executa a persona **localmente** via Antigravity SDK (`agy` CLI) sem consumir cota Jules. |
| `amb agent --all --loop` | Loop contínuo infinito iterando por todas as personas do projeto. |
| `amb agent --loop --max-cycles <N>` | Limita o loop contínuo a N ciclos de entrega completos. |
| `amb agent --loop --branch <branch>` | Define o branch base para as sessões (padrão: branch atual ou `develop`). |
| `amb agent --loop --modules <m1,m2>` | Rotaciona o foco entre submódulos a cada ciclo com injeção automática de `amb context`. |
| `amb agent --loop --no-auto-merge` | Desativa o merge automático do PR após validação do QA. |

### ☁️ Google Jules Cloud (`amb jules`)
| Comando | Descrição & Uso no Projeto |
| :--- | :--- |
| `amb jules status [--json]` | Diagnóstico de conexão, credenciais e sessões ativas do repositório. |
| `amb jules sources [--json]` | Lista repositórios conectados à conta Google Jules. |
| `amb jules list [--limit N] [--state S]` | Lista sessões recentes do repositório com filtros de estado. |
| `amb jules get <id_ou_url> [--watch]` | Exibe detalhes da sessão com streaming de logs e comandos bash ao vivo (`-w`). |
| `amb jules create -p "<prompt>" [-t "<titulo>"]` | Cria nova sessão na nuvem em branch dedicada. |
| `amb jules reply <id> [-m "<msg>"] [-y]` | Responde dúvidas do agente (manual ou auto-resposta via Gemini Advisor). |
| `amb jules approve <id> [--force]` | Aprova o plano de ação formulado pelo agente (`:approvePlan`). |
| `amb jules merge <id>` | Converte Draft PR em Ready (`gh pr ready`), valida QA local, aprova e faz merge. |
| `amb jules merge --auto-latest` | Detecta e faz merge do PR aberto mais recente da sessão. |
| `amb jules clean [--failed] [--merged] [-f]` | Limpa sessões finalizadas ou com erro fatal na nuvem para economizar cota. |

> **Normalização Universal de IDs:** Todos os comandos aceitam ID numérico puro (`175...`), caminho REST (`sessions/175...`) ou URL web do navegador (`https://jules.google.com/session/175...`).

### 🎨 Google Stitch SDK (`amb stitch`)
| Comando | Descrição & Uso no Projeto |
| :--- | :--- |
| `amb stitch list` | Lista todas as telas criadas no projeto Stitch ativo. |
| `amb stitch generate -p "<prompt>" [-d <device>]` | Gera nova tela visual (`MOBILE`, `DESKTOP`, `TABLET`, `AGNOSTIC`). |
| `amb stitch refine -s <id> -p "<prompt>"` | Refina tela existente com novos tokens visuais e componentes. |
| `amb stitch get -s <id> [-o <arquivo>]` | Exporta DOM HTML, CSS e metadados da tela para arquivo local. |
| `amb stitch variants -s <id> -c <N>` | Gera variantes visuais exploratórias (1 a 5 variações). |
| `amb stitch download -o <dir>` | Baixa assets visuais e HTMLs para a pasta pública do projeto. |
| `amb stitch sync [-f design.md]` | Sincroniza design tokens do projeto com o Design System oficial do Stitch. |
| `amb stitch call <tool> '<json>'` | Invoca qualquer ferramenta oficial do Stitch SDK via JSON-RPC. |

### 🚀 Pipeline Design-to-Deploy (`amb pipeline`)
| Comando | Descrição & Uso no Projeto |
| :--- | :--- |
| `amb pipeline -s <stitch.md> -j <jules.md>` | **Pipeline Completo:** Prompts separados (SRP) para design visual no Stitch e engenharia no Jules. |
| `amb pipeline -j <jules.md> --skip-stitch` | Executa apenas a etapa de engenharia de backend/código sem interface. |
| `amb pipeline --resume-session <id>` | Retoma o monitoramento e QA de uma sessão Jules já iniciada. |
| `amb pipeline -s <s.md> -j <j.md> -y` | Modo 100% autônomo sem pausas de aprovação no Gatekeeper 1. |

### 🧠 Antigravity, Regras & Contexto (`amb agy`, `amb context`, `amb schema`)
| Comando | Descrição & Uso no Projeto |
| :--- | :--- |
| `amb context [modulo] [--json]` | Mapeia as camadas do projeto (Database ➔ Services ➔ API ➔ UI) para acelerar IAs. |
| `amb schema [filtro]` | Inspeciona schemas e tabelas do banco de dados do projeto (Drizzle, Prisma, etc.). |
| `amb validate <arquivo>` (ou `amb agy validate`) | Audita conformidade arquitetural do código contra as regras do repositório. |
| `amb agy rules [--content]` | Lista e inspeciona as regras arquiteturais ativas no repositório. |
| `amb agy run "<prompt>" [-m <modelo>]` | Executa inferência cognitiva arbitrária via Gemini REST. |

### 🐙 Git & Pull Requests (`amb git`)
| Comando | Descrição & Uso no Projeto |
| :--- | :--- |
| `amb git status [--json]` | Status detalhado do Git local, branches, upstream e integridade da CLI `gh`. |
| `amb git sync [-r origin] [-b branch]` | Sincroniza branch ativa com fetch + pull com auto-stash transparente. |
| `amb git pr list [--no-drafts]` | Lista Pull Requests abertos no GitHub. |
| `amb git pr get <id>` | Detalhes estruturados, checks de CI e comentários do PR. |
| `amb git pr create -t "<titulo>" [-b "<body>"]` | Abre Pull Request no GitHub a partir da branch atual. |
| `amb git pr ready <id>` | Converte Draft PR em Ready for Review. |
| `amb git pr approve <id>` | Aprova formalmente o Pull Request. |
| `amb git pr merge <id>` | Faz merge via squash e exclui a branch remota. |

---

## ⚡ 3. Os 3 Fluxos de Desenvolvimento Mais Poderosos

### Fluxo 1: Desenvolvimento em Lote por Prompts (`amb agent -p`)
1. Crie uma pasta `.amb/prompts/` com arquivos numerados dividindo a feature:
   - `01_database.md`: Migrations e modelos.
   - `02_services.md`: Regras de negócio e use cases.
   - `03_api.md`: Endpoints e rotas.
   - `04_ui.md`: Telas e componentes.
2. Execute no terminal do projeto:
   ```bash
   amb agent -p .amb/prompts/ --branch feature/minha-feature
   ```
3. O AMB despachará cada arquivo sequencialmente para o Jules, vigiará a execução, responderá dúvidas com o Gemini, rodará o QA local (`amb_project.json`) e fará o auto-merge de cada PR antes de avançar para o próximo!

### Fluxo 2: Loop Autônomo Contínuo (`amb agent --loop`)
1. Escolha uma persona de engenharia (ex: `engineer`):
   ```bash
   amb agent --role engineer --loop --max-cycles 5
   ```
2. O AMB extrai o contexto arquitetural do projeto automaticamente (`amb context`), despacha para a Cloud VM do Jules, responde eventuais dúvidas ou erros de build com o Gemini e realiza merge seguro com validação de testes locais.

### Fluxo 3: Design-to-Deploy com Stitch & Jules (`amb pipeline`)
1. Crie `specs/login_ui.md` com a especificação visual para o Stitch.
2. Crie `specs/login_eng.md` com os requisitos de código para o Jules.
3. Execute:
   ```bash
   amb pipeline -s specs/login_ui.md -j specs/login_eng.md
   ```
4. O Stitch gera a tela ➔ você valida no Gatekeeper ➔ o Jules implementa no framework do seu projeto ➔ o pipeline valida o QA e abre/mescla o PR.

---

## 🛡️ 4. Guia Rápido de Troubleshooting

| Sintoma | Causa Mais Comum | Solução Imediata |
| :--- | :--- | :--- |
| `amb: command not found` | AMB_V2 não foi instalado no modo global editável | Rode `pip install -e /caminho/para/amb_v2` no terminal. |
| `Falta JULES_API_KEY no .env` | Chave de API ausente ou `.env` não encontrado | Rode `amb gui` para cadastrar visualmente ou adicione ao `.env`. |
| `Jules PR preso em Draft` | Jules abre PRs em Draft por padrão | Use `amb jules merge <id>` (ele roda `gh pr ready` automaticamente). |
| `Falha de QA no Windows` | Comando no `amb_project.json` usa bash puro | Configure executáveis nativos (ex: `npm run test` em vez de `./test.sh`). |
| `Loop gastando cota Jules` | Tarefa simples que poderia rodar localmente | Adicione a flag `--agy` (ex: `amb agent --role <persona> --agy`). |
