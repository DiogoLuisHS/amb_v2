# 🚀 AMB_V2 — CLI Global de Automação, Agentes e Integrações

O **`amb_v2`** é um ecossistema universal de automação, agentes cognitivos e engenharia de software para monorepos e aplicações modernas. Ele centraliza o motor de execução em uma **CLI global unificada (`amb`)**, consumindo dinamicamente as regras, personas, diários e configurações da pasta **`.amb/`** de cada repositório ativo.

---

## 📦 1. Instalação Global (Single Source of Truth)

Instale o pacote globalmente em **modo editável (`-e`)** a partir da pasta do `amb_v2`:

```bash
pip install -e amb_v2/
```

> **💡 Vantagem do modo `-e`:** Qualquer melhoria ou novo comando adicionado ao `amb_v2` passa a valer **instantaneamente** para todos os projetos no seu terminal, sem necessidade de reinstalação!

---

## 🧭 2. Guia de Referência Completo de Comandos (`amb`)

```bash
amb [comando] [subcomando] [opções]
```

### ⚙️ 2.1. Configuração e Diagnóstico de Projetos (`setup`, `check`, `prompt`)

| Comando | Descrição |
| :--- | :--- |
| `amb setup` (alias: `init`) | Executa o assistente inteligente de detecção da stack, gerando `.amb/amb_project.json`, adaptando personas e configurando o `.env`. |
| `amb setup --auto` | Executa o setup e provisionamento em modo não-interativo automático. |
| `amb prompt` | Exibe no terminal o **Prompt Mestre de Auto-Configuração de IA** para colar no chat de qualquer nova IA. |
| `amb prompt --synthesize "<ideia>"` | Sintetiza uma ideia informal em um prompt arquitetural estruturado com o Gemini. |
| `amb check` (alias: `status`) | Valida e exibe o checklist das chaves de API (`.env`) e integridade do `.amb/amb_project.json`. |

**Exemplos:**
```bash
# Iniciar o assistente no projeto atual:
amb setup

# Sintetizar ideia com IA:
amb prompt --synthesize "Criar tela de checkout com Stripe e validação Zod"

# Validar o checklist de ambiente:
amb check
```

---

### 📡 2.2. Sentinela, Advisor & Dashboard Web (`monitor`, `advisor`, `dashboard`)

Monitora continuamente o status de sessões do Google Jules e deploys no Render Cloud, com suporte a auto-resposta via Gemini e interface Web SPA em tempo real.

| Comando / Opção | Descrição |
| :--- | :--- |
| `amb monitor` (aliases: `watch`, `sentinel`) | Inicia o sentinela contínuo em tempo real com polling a cada 15s. |
| `amb monitor --check-once` (`-1`) | Executa apenas uma rodada de checagem de status/alertas e encerra imediatamente. |
| `amb monitor --interactive` (`-i`) | Checa pendências e abre o menu cognitivo com IA para inspecionar e responder dúvidas. |
| `amb monitor --auto-approve` (`-y`) | **Piloto Automático:** vigia e responde automaticamente todas as dúvidas no Jules usando o Gemini. |
| `amb advisor` (alias: `ask`) | Menu cognitivo interativo para responder chats pendentes do Jules com sugestão de IA. |
| `amb dashboard` (aliases: `web`, `ui`) | Inicia o servidor Web SPA em tempo real na porta configurada (padrão: 3333). |

**Exemplos:**
```bash
# Sentinela contínuo:
amb monitor

# Checagem rápida de status:
amb monitor -1

# Menu de resolução de dúvidas com IA:
amb advisor

# Iniciar Dashboard Web:
amb dashboard --port 3333
```

---

### 🤖 2.3. Personas Autônomas de Manutenção (`agent`)

Descobre dinamicamente os arquivos de persona em `.amb/personas/` e histórico em `.amb/diarios/` do projeto ativo.

| Comando / Opção | Descrição |
| :--- | :--- |
| `amb agent --list` (`-l`) | Lista todas as personas disponíveis na pasta `.amb/personas/` do projeto ativo. |
| `amb agent --role <nome>` (`-r`) | Executa uma persona localmente no repositório usando a CLI oficial `agy`. |
| `amb agent --role <nome> --task "<instruções>"` | Executa a persona combinando o prompt base com instruções específicas adicionais. |
| `amb agent --role <nome> --dispatch-jules` (`-j`) | Despacha a persona para a nuvem do Google Jules (cria Cloud VM, branch e Pull Request). |
| `amb agent --all` (`-a`) | Executa **todas** as personas da pasta sequencialmente em lote. |
| `amb agent --loop` (`-c`) | **Loop Contínuo Autônomo:** executa ciclos contínuos de personas com monitoramento e merge automático. |

**Exemplos:**
```bash
# Ver catálogo de personas:
amb agent --list

# Executar a persona relay localmente:
amb agent --role relay

# Despachar o sentry para a nuvem do Jules:
amb agent --role sentry --dispatch-jules
```

---

### ⚡ 2.4. Google Jules SDK (`jules`)

Integração completa com a API REST do Google Jules, gestão de tarefas e integração de PRs no Git.

| Comando / Opção | Descrição |
| :--- | :--- |
| `amb jules list [--limit <N>]` | Lista as sessões e chats recentes do repositório no Jules. |
| `amb jules get <session_id> [--watch] [--json]` | Consulta os detalhes da sessão ou entra em modo streaming ao vivo com `--watch` (`-w`). |
| `amb jules create --prompt "<prompt>" [--title "<título>"]` | Cria uma nova sessão de codificação remota no Jules. |
| `amb jules reply [--session-id <id>] [-m "texto"] [-y]` | Responde dúvidas pendentes com IA ou envia mensagem direta se `--message` (`-m`). |
| `amb jules approve --session-id <id>` | Aprova o plano de ação formulado pelo agente (`:approvePlan`). |
| `amb jules merge [--session-id <id>] [--auto-latest]` | Detecta o PR gerado pela sessão, aprova, faz merge no GitHub e valida build/typecheck local. |
| `amb jules clean [--force]` (alias: `cleanup`) | Audita e remove na nuvem sessões do Jules que já foram integradas no Git. |

**Exemplos:**
```bash
# Listar sessões recentes:
amb jules list

# Acompanhar streaming de logs de uma sessão:
amb jules get 17502412430766789460 --watch

# Responder dúvida pendente com Gemini:
amb jules reply -s 17502412430766789460

# Fazer merge e validação de QA do PR gerado pelo Jules:
amb jules merge -s 17502412430766789460
```

---

### 🎨 2.5. Google Stitch SDK (`stitch`)

Prototipação visual, geração de telas, exploração de variantes e sincronização de Design System.

| Comando / Opção | Descrição |
| :--- | :--- |
| `amb stitch generate --prompt "<prompt>" [--title "<título>"]` | Gera uma nova tela visual HTML/CSS via Google Stitch SDK. |
| `amb stitch refine --screen-id <id> --prompt "<instruções>"` | Refina uma tela existente respeitando os tokens do Design System. |
| `amb stitch variants --screen-id <id> [--count 3]` | Gera variantes visuais exploratórias a partir de uma tela base. |
| `amb stitch sync [--file <design.md>]` | Sincroniza design tokens do arquivo `design.md` com o Stitch. |
| `amb stitch get --screen-id <id>` | Baixa o código HTML/CSS e dados de uma tela específica. |

**Exemplos:**
```bash
# Gerar nova tela:
amb stitch generate --prompt "Dashboard financeiro moderno com cards de métricas"

# Gerar variantes visuais:
amb stitch variants --screen-id <SCREEN_ID> --count 3

# Sincronizar Design Tokens locais com a nuvem:
amb stitch sync
```

---

### 🚀 2.6. Render Cloud (`render`)

Integração com a infraestrutura em nuvem do Render para monitorar deploys e serviços.

| Comando | Descrição |
| :--- | :--- |
| `amb render status` | Exibe o status do serviço, último deploy e commit associado. |
| `amb render logs` | Consulta e exibe os últimos logs do servidor de produção. |
| `amb render services` | Lista todos os serviços configurados na conta Render com seus IDs. |
| `amb render deploy` | Dispara um novo deploy manual via Render API. |

---

### 🔍 2.7. Qualidade, Pipeline, Schemas & Contexto (`validate`, `pipeline`, `schema`, `context`)

| Comando | Descrição |
| :--- | :--- |
| `amb validate <arquivo>` (aliases: `lint`, `audit`) | Audita um arquivo de código contra as diretrizes de `.antigravity/rules/`. |
| `amb pipeline <arquivo.md>` | Executa o pipeline completo Design-to-Deploy ponta a ponta. |
| `amb schema [filtro]` (alias: `amb db`) | Inspeciona tabelas e colunas de schemas do banco de dados (Read-Only). |
| `amb context <modulo>` (alias: `amb ctx`) | Gera o roteiro ordenado de leitura de arquivos por camadas para a IA. |

---

## 📂 3. Estrutura Arquitetural Enxuta

```
📁 amb_v2/
├── pyproject.toml / setup.py        # Configuração de build e comando global 'amb'
├── cli.py                           # Ponto de entrada CLI unificado (100% consolidado)
├── config/                          # Gerenciador de ambiente, validações e setup
├── architecture/                    # Leitor de Schemas e Construtor de Contexto por Camadas
├── agents/
│   ├── auto_reply.py                # Motor cognitivo de resposta e auto-advisor
│   └── local_agent_runner.py        # Executor dinâmico de personas e ciclos autônomos
├── dashboard/
│   ├── dashboard_server.py          # Servidor e SPA do Dashboard Web em tempo real
│   ├── unified_monitor.py           # Sentinela contínuo e loop de vigilância
│   └── watchers/                    # Watchers do Jules e Render
├── integrations/
│   ├── antigravity/
│   │   └── antigravity_client.py    # Client Gemini + síntese de prompt e validação
│   ├── jules/
│   │   ├── jules_client.py          # Client REST API oficial do Google Jules
│   │   └── tools/                   # Automações Git/PR (merge_session_pr, cleanup)
│   ├── render/
│   │   └── render_client.py         # Client oficial da Render Cloud API
│   └── stitch/
│       ├── stitch_client.mjs        # Runner Node.js do Stitch SDK
│       └── stitch_client.py         # Client Python (geração, refinamento, variantes, sync)
└── pipeline/
    └── pipeline.py                  # Orquestrador Design-to-Deploy ponta a ponta
```
