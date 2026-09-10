# 🚀 AMB_V2 — CLI Global de Automação, Agentes e Engenharia

O **`amb_v2`** é um ecossistema universal de automação de engenharia, orquestração de agentes autônomos e integração contínua para monorepos e aplicações modernas. Ele disponibiliza a **CLI global `amb`**, permitindo operar qualquer repositório no terminal através do arquivo `.env` e da pasta `.amb/`.

---

## 📦 1. Instalação Global

Para que o comando `amb` esteja disponível em qualquer terminal ou repositório:

```bash
# Na pasta raiz do amb_v2:
pip install -e .
```

> **💡 Modo Editável (`-e`):** Qualquer melhoria no código do `amb_v2` é aplicada imediatamente em todos os seus projetos sem necessidade de reinstalar.

---

## 🧭 2. Guia Completo de Comandos (`amb`)

```bash
amb [comando] [subcomando] [opções]
```

---

### ⚙️ 2.1. Configuração e Diagnóstico (`setup`, `check`, `prompt`)

Gerencia o provisionamento, checklist de credenciais e geração de prompts para IAs.

| Comando / Opção | Alias | Descrição |
| :--- | :--- | :--- |
| `amb check` | `amb status` | Valida as chaves de API (`.env`) e integridade do projeto. |
| `amb setup` | `amb init` | Assistente interativo de detecção de stack e configuração do `.env`. |
| `amb setup --auto` | — | Executa o setup em modo automático/não-interativo. |
| `amb prompt` | `amb setup -p` | Imprime o Prompt Mestre de Auto-Configuração para colar em novas IAs. |
| `amb prompt --synthesize "<ideia>"` | `-s` | Converte uma ideia informal em prompt arquitetural estruturado com Gemini. |
| `amb prompt --role <especialidade>` | `-r` | Define a especialidade da IA para a síntese do prompt (ex: `frontend`, `security`). |

```bash
# Exemplos:
amb check
amb setup
amb prompt --synthesize "Criar painel de métricas financeiras com gráficos e filtros por data" --role frontend
```

---

### 📡 2.2. Sentinela, Advisor & Assistente Gráfico (`monitor`, `advisor`, `gui`)

Vigilância em tempo real das sessões do Jules e deploys do Render, auto-resposta via Gemini e Assistente Gráfico nativo para montagem de comandos e gestão de variáveis do `.env`.

| Comando / Opção | Alias | Descrição |
| :--- | :--- | :--- |
| `amb monitor` | `watch`, `sentinel` | Inicia o sentinela contínuo em tempo real (polling a cada 15s). |
| `amb monitor --check-once` | `-1` | Executa apenas 1 rodada de checagem de status e encerra. |
| `amb monitor --interactive` | `-i` | Inspeciona pendências e abre o menu interativo cognitivo (Advisor). |
| `amb monitor --auto-approve` | `-y` | **Piloto Automático:** vigia e responde dúvidas no Jules 100% via Gemini. |
| `amb monitor --interval <N>` | — | Define o intervalo de polling em segundos (padrão: 15s). |
| `amb advisor` | `ask` | Menu interativo cognitivo para revisar e responder chats com pendência no Jules. |
| `amb advisor --auto-approve` | `-y` | Responde todas as dúvidas pendentes em lote com IA sem pedir confirmação. |
| `amb gui` | `ui`, `wizard` | Abre o Assistente Gráfico Interativo (Tkinter) com Runner dinâmico e Gestor de `.env` do projeto ativo. |

```bash
# Exemplos:
amb monitor -1                  # Checagem instantânea de status
amb monitor -y                  # Sentinela autônomo (vigia e auto-responde no Jules)
amb advisor                     # Menu interativo para responder chats pendentes
amb gui                         # Abre a interface gráfica nativa (Runner + .env)
```

---

### 🤖 2.3. Agentes e Personas Autônomas (`agent`)

Descobre dinamicamente e executa as personas da pasta `.amb/personas/` (ou `.jules/personas/`).

| Comando / Opção | Alias | Descrição |
| :--- | :--- | :--- |
| `amb agent --list` | `-l` | Lista todas as personas disponíveis no projeto ativo. |
| `amb agent --role <nome>` | `-r` | Executa uma persona localmente via CLI `agy` (ex: `pixel`, `relay`, `sentry`). |
| `amb agent --role <nome> --dispatch-jules` | `-j` | Despacha a persona para a nuvem do Google Jules (Cloud VM + Branch + PR). |
| `amb agent --role <nome> --task "<texto>"` | `-t` | Anexa instruções ou escopo adicional ao prompt base da persona. |
| `amb agent --all` | `-a` | Executa todas as personas da pasta sequencialmente em lote. |
| `amb agent --loop` | `-c`, `--continuous` | **Ciclo Autônomo:** loop contínuo de envio, vigilância, auto-reply e auto-merge no Git. |
| `amb agent --all --loop` | — | Loop autônomo iterando por **todas as personas** a cada ciclo. |
| `amb agent --loop --max-cycles <N>` | — | Limita a execução do loop a N ciclos completos antes de parar. |
| `amb agent --loop --branch <branch>` | `-b` | Define o branch-alvo para criação da sessão Jules (padrão: `develop`). |
| `amb agent --loop --modules <m1,m2>` | — | Rotaciona o foco entre módulos do repositório a cada ciclo. |
| `amb agent --personas-dir <pasta>` | — | Define um diretório customizado de personas. |

> **💡 `amb context` automático no loop:** ao despachar cada sessão, o `autonomous_loop` roda automaticamente `amb context <modulo>` e **anexa o roteiro arquitetural completo** (DB → Services → UI) ao prompt enviado ao Jules, reduzindo em 20-30min o tempo de exploração inicial por sessão.

```bash
# Exemplos:
amb agent --list                                        # Ver personas disponíveis
amb agent --role pixel                                  # Executar persona localmente
amb agent --role pixel -j                               # Despachar persona para o Jules na nuvem
amb agent --role pixel --loop                           # Loop contínuo infinito com auto-merge de PR
amb agent --role pixel --loop --max-cycles 3            # Loop com limite de 3 ciclos
amb agent --all --loop --max-cycles 2                   # Todas as personas, 2 ciclos completos
amb agent --all --loop --branch main --max-cycles 5     # Loop na branch main
amb agent --role relay --loop --modules agenda,kanban   # Rotacionar entre módulos por ciclo
```

---

### ⚡ 2.4. Google Jules Cloud (`jules`)

Integração direta com o Google Jules para desenvolvimento remoto e gestão de PRs no GitHub.

| Comando / Opção | Alias | Descrição |
| :--- | :--- | :--- |
| `amb jules list` | — | Lista as sessões recentes do repositório no Jules (`--limit <N>`). |
| `amb jules get <id>` | — | Exibe detalhes da sessão, status da VM e URL do Pull Request. |
| `amb jules get <id> --watch` | `-w` | Acompanha streaming em tempo real das atividades, mensagens e comandos bash. |
| `amb jules get <id> --json` | — | Retorna o payload completo da sessão em JSON puro. |
| `amb jules create -p "<prompt>"` | `--prompt` | Cria uma nova sessão no Jules vinculada ao repositório do `.env`. |
| `amb jules create -p "..." -t "<título>"` | `--title` | Cria uma sessão com título personalizado. |
| `amb jules reply` | `advisor` | Abre menu interativo com IA para listar e responder dúvidas pendentes. |
| `amb jules reply -s <id>` | `--session-id` | Gera sugestão com Gemini e responde turn-by-turn a uma sessão específica. |
| `amb jules reply -s <id> -m "<texto>"` | `--message` | Envia mensagem manual direta para o chat da sessão no Jules. |
| `amb jules reply -s <id> -y` | `--auto-approve` | Envia a resposta sugerida pelo Gemini imediatamente sem pedir confirmação. |
| `amb jules approve -s <id>` | `--session-id` | Aprova o plano de ação formulado pelo agente (`:approvePlan`). |
| `amb jules merge -s <id>` | `--session-id` | Detecta o PR da sessão, publica se Draft, aprova, faz merge e valida QA local. |
| `amb jules merge --auto-latest` | — | Detecta e faz merge do Pull Request aberto mais recente (incluindo Drafts). |
| `amb jules merge -s <id> --branch <b>` | `-b` | Define o branch-alvo do merge (padrão: `develop`). |
| `amb jules clean` | `cleanup` | Audita e remove na nuvem do Jules as sessões já integradas no Git (`-f` para forçar). |
| `amb jules clean --failed` | — | Remove as sessões que terminaram em estado de erro fatal (FAILED). |

> **💡 Publicação automática de Draft PRs:** o Jules sempre cria PRs como **Draft**. O pipeline `amb jules merge` executa `gh pr ready` automaticamente antes do merge, sem necessidade de intervenção manual.

```bash
# Exemplos:
amb jules list --limit 5
amb jules get 17502412430766789460 --watch          # Streaming de logs ao vivo
amb jules create -p "Refatorar componentes de modal" -t "Modal Refactor"
amb jules reply -s 17502412430766789460              # Responder dúvida com Gemini
amb jules merge -s 17502412430766789460              # Merge do PR no GitHub + QA local
amb jules merge -s 17502412430766789460 -b main      # Merge na branch main
amb jules clean                                      # Auditar sessões e limpar PRs já mergeados
amb jules clean --failed --force                     # Deletar sessões com erro fatal (FAILED)
```

---

### 🎨 2.5. Google Stitch SDK (`stitch`)

Geração de interfaces visuais, refinamento com Design Tokens e variantes exploratórias.

| Comando / Opção | Alias | Descrição |
| :--- | :--- | :--- |
| `amb stitch generate -p "<prompt>"` | `--prompt` | Gera uma nova tela HTML/CSS via Google Stitch SDK. |
| `amb stitch refine -s <id> -p "<prompt>"` | `--screen-id` | Refina uma tela existente com novas instruções visuais. |
| `amb stitch variants -s <id>` | `--screen-id` | Gera variantes visuais exploratórias a partir de uma tela base. |
| `amb stitch variants -s <id> -c <N>` | `--count` | Define o número de variantes a serem geradas (padrão: 3). |
| `amb stitch sync` | — | Sincroniza design tokens do `design.md` com o Design System do Stitch. |
| `amb stitch sync -f <caminho>` | `--file` | Especifica um arquivo customizado de design tokens. |
| `amb stitch get -s <id>` | `--screen-id` | Baixa o código HTML/CSS, DOM e screenshot da tela. |

```bash
# Exemplos:
amb stitch generate -p "Dashboard SaaS com sidebar escura e cards de KPI"
amb stitch refine -s <SCREEN_ID> -p "Tornar os botões arredondados e ajustar contraste"
amb stitch variants -s <SCREEN_ID> --count 3
amb stitch sync
```

---

### 🚀 2.6. Render Cloud (`render`)

Integração com a infraestrutura em nuvem do Render para monitoramento e deploys.

| Comando | Descrição |
| :--- | :--- |
| `amb render status` | Exibe o status do serviço, último deploy e commit associado. |
| `amb render logs` | Consulta e exibe os últimos logs do servidor de produção. |
| `amb render services` | Lista todos os serviços configurados na conta Render com seus IDs. |
| `amb render deploy` | Dispara um novo deploy manual via Render API. |

```bash
# Exemplos:
amb render status
amb render logs
amb render services
amb render deploy
```

---

### 🔍 2.7. Qualidade, Pipeline, Schemas & Contexto (`validate`, `pipeline`, `schema`, `context`)

Ferramentas avançadas para governança de código, orquestração Design-to-Deploy e inteligência de monorepo.

> [!TIP]
> **Separação de Responsabilidade no Pipeline (SRP)**: O comando `amb pipeline` agora aceita arquivos dedicados para Stitch (Design visual com `-s`) e Jules (Engenharia de software com `-j`), garantindo especificações limpas e focadas.

| Comando / Opção | Alias | Descrição |
| :--- | :--- | :--- |
| `amb pipeline -s <stitch.md> -j <jules.md>` | `run`, `deploy` | Executa o pipeline orquestrado ponta a ponta **Design-to-Deploy** com prompts separados para Stitch e Jules. |
| `amb pipeline -j <jules.md> --skip-stitch` | — | Pula a etapa visual do Stitch e vai direto para a engenharia no Jules. |
| `amb pipeline -s <s.md> -j <j.md> -y` | `--auto-approve` | Pula confirmações manuais no Gatekeeper 1 de Design (Modo 100% autônomo). |
| `amb pipeline -s <s.md> -j <j.md> --branch <b>` | `-b` | Define o branch-alvo de início para o Jules (Padrão: detecta a atual). |
| `amb pipeline -s <s.md> -j <j.md> --device <D>`| `-d` | Dispositivo alvo para o Stitch (`DESKTOP`, `MOBILE`, `TABLET`). |
| `amb pipeline -s <s.md> -j <j.md> --sync-ds` | — | Sincroniza design tokens locais (`design.md`) com o Stitch antes de gerar. |
| `amb pipeline --edit-screen-id <id>` | — | Refina uma tela existente no Stitch em vez de criar uma nova. |
| `amb pipeline --screen-id <id>` | — | Utiliza uma tela já existente no Stitch como ponto de partida (não recria). |
| `amb pipeline --resume-session <id>` | `-r` | Retoma o monitoramento ao vivo e QA de uma sessão Jules já iniciada. |
| `amb pipeline --no-qa` | — | Desabilita o teste QA local automático no final da execução. |
| `amb validate <arquivo>` | `lint`, `audit` | Audita o código contra as diretrizes e regras de `.antigravity/rules/`. |
| `amb schema [filtro]` | `db` | Inspeciona tabelas e colunas de schemas do banco de dados (Read-Only). |
| `amb context <modulo>` | `ctx`, `ai-context` | Gera o roteiro ordenado de leitura de arquivos por camadas para a IA. |
| `amb context <modulo> --json` | — | Retorna o grafo de dependências e arquivos em formato JSON estruturado. |

```bash
# Exemplos do Pipeline:
amb pipeline -s specs/login_ui.md -j specs/login_eng.md        # Execução completa (Design no Stitch + Engenharia no Jules)
amb pipeline -j specs/fix_api.md --skip-stitch                 # Tarefa de backend/engenharia pura (sem tela Stitch)
amb pipeline -s specs/painel.md -j specs/painel_eng.md -y      # Pipeline autônomo sem pausas de aprovação
amb pipeline --resume-session 538227422414712240               # Reconectar a uma sessão remota do Jules

# Demais ferramentas:
amb validate src/components/Header.tsx             # Auditoria de regras arquiteturais
amb schema kanban                                  # Inspecionar tabelas relacionadas ao kanban
amb context agenda                                 # Roteiro de arquivos (DB ➔ Services ➔ API ➔ UI)
```


---

## 📋 3. Tabela de Referência Rápida de Todos os Comandos

| Categoria | Comando CLI | Equivalente Script `python` |
| :--- | :--- | :--- |
| **Setup & Env** | `amb check` | `python config/config.py` |
| **Setup & Env** | `amb setup` | `python config/setup_project.py` |
| **Setup & Env** | `amb prompt` | `python config/setup_project.py --prompt` |
| **Setup & Env** | `amb prompt --synthesize "..."` | `python integrations/antigravity/tools/synthesize_prompt.py` |
| **Vigilância** | `amb monitor` | `python dashboard/unified_monitor.py` |
| **Vigilância** | `amb monitor -1` | `python dashboard/unified_monitor.py --check-once` |
| **Vigilância** | `amb monitor -y` | `python dashboard/unified_monitor.py --auto-approve` |
| **Vigilância** | `amb advisor` | `python dashboard/auto_advisor.py` |
| **Interface** | `amb gui` (ou `amb ui`) | `python gui/wizard_app.py` |
| **Personas** | `amb agent --list` | `python agents/local_agent_runner.py --list` |
| **Personas** | `amb agent --role <nome>` | `python agents/local_agent_runner.py --role <nome>` |
| **Personas** | `amb agent --role <nome> -j` | `python agents/local_agent_runner.py --role <nome> -j` |
| **Personas** | `amb agent --loop` | `python agents/autonomous_loop.py` |
| **Personas** | `amb agent --all --loop` | `python agents/autonomous_loop.py --all` |
| **Personas** | `amb agent --loop --max-cycles <N>` | `python agents/autonomous_loop.py --max-cycles <N>` |
| **Personas** | `amb agent --loop --branch <b>` | `python agents/autonomous_loop.py --branch <b>` |
| **Jules Cloud** | `amb jules list` | `python integrations/jules/tools/list_sessions.py` |
| **Jules Cloud** | `amb jules get <id>` | `python integrations/jules/tools/get_session.py <id>` |
| **Jules Cloud** | `amb jules get <id> --watch` | `python integrations/jules/tools/monitor_activities.py <id>` |
| **Jules Cloud** | `amb jules create -p "..."` | `python integrations/jules/tools/create_session.py` |
| **Jules Cloud** | `amb jules reply -s <id>` | `python agents/auto_reply.py -s <id>` |
| **Jules Cloud** | `amb jules reply -s <id> -m "..."` | `python integrations/jules/tools/send_message.py` |
| **Jules Cloud** | `amb jules approve -s <id>` | `python integrations/jules/tools/approve_plan.py` |
| **Jules Cloud** | `amb jules merge -s <id>` | `python integrations/jules/tools/merge_session_pr.py` |
| **Jules Cloud** | `amb jules merge --auto-latest` | `python integrations/jules/tools/merge_session_pr.py --auto-latest` |
| **Jules Cloud** | `amb jules clean` | `python integrations/jules/tools/cleanup_sessions.py` |
| **Stitch SDK** | `amb stitch generate -p "..."` | `python integrations/stitch/tools/generate_screen.py` |
| **Stitch SDK** | `amb stitch refine -s <id> -p "..."` | `python integrations/stitch/tools/edit_screen.py` |
| **Stitch SDK** | `amb stitch variants -s <id>` | `python integrations/stitch/tools/generate_variants.py` |
| **Stitch SDK** | `amb stitch sync` | `python integrations/stitch/tools/sync_design_system.py` |
| **Stitch SDK** | `amb stitch get -s <id>` | `python integrations/stitch/tools/get_screen.py` |
| **Render Cloud**| `amb render services` | `python integrations/render/tools/list_services.py` |
| **Render Cloud**| `amb render status` | `python integrations/render/tools/get_deploy_status.py` |
| **Render Cloud**| `amb render logs` | `python integrations/render/tools/fetch_logs.py` |
| **Render Cloud**| `amb render deploy` | `python integrations/render/tools/trigger_deploy.py` |
| **Qualidade** | `amb validate <arquivo>` | `python integrations/antigravity/tools/validate_architecture.py` |
| **Pipeline** | `amb pipeline -s <s.md> -j <j.md>` | `python pipeline/pipeline.py -s <s.md> -j <j.md>` |
| **Arquitetura** | `amb schema [filtro]` | `python architecture/db_schema_reader.py` |
| **Arquitetura** | `amb context <modulo>` | `python architecture/ai_context_builder.py` |

---

## 📂 4. Estrutura do Repositório

```text
📁 amb_v2/
├── pyproject.toml / setup.py        # Configuração de build e comando global 'amb'
├── cli.py                           # CLI global unificada (Single Source of Truth)
├── cli_modules/                     # Handlers e parsers modulares da CLI (SRP)
├── config/
│   ├── config.py                    # Gerenciador central de .env, validações e caminhos
│   └── setup_project.py             # Assistente de provisionamento e stack
├── gui/
│   ├── README.md                    # Documentação do Assistente Gráfico
│   └── wizard_app.py                # Assistente Gráfico Nativo (Tkinter) dinâmico e gestor de .env
├── architecture/
│   ├── db_schema_reader.py          # Leitor de schemas e banco de dados (Read-Only)
│   └── ai_context_builder.py        # Construtor de contexto por camadas para IA
├── agents/
│   ├── auto_reply.py                # Resposta cognitiva com Gemini e histórico turn-by-turn
│   ├── autonomous_loop.py           # Loop contínuo autônomo (Jules + Gemini + Auto-Merge)
│   └── local_agent_runner.py        # Executor dinâmico de personas
├── dashboard/
│   ├── unified_monitor.py           # Sentinela contínuo e loop de vigilância
│   └── watchers/                    # Watchers especializados do Jules e Render
├── integrations/
│   ├── antigravity/
│   │   ├── antigravity_client.py    # Client Gemini + síntese de prompt e validação
│   │   └── tools/                   # Facades retrocompatíveis
│   ├── jules/
│   │   ├── jules_client.py          # Client REST API oficial do Jules
│   │   └── tools/                   # Facades e automações Git (merge_session_pr, cleanup)
│   ├── render/
│   │   ├── render_client.py         # Client oficial Render Cloud API
│   │   └── tools/                   # Facades retrocompatíveis
│   └── stitch/
│       ├── stitch_client.mjs        # Runner Node.js do Stitch SDK
│       ├── stitch_client.py         # Client Python oficial (telas, variantes, design system)
│       └── tools/                   # Facades retrocompatíveis
└── pipeline/
    ├── README.md                    # Documentação da arquitetura do pipeline
    └── pipeline.py                  # Orquestrador Design-to-Deploy ponta a ponta
```

---

## ⚙️ 5. Configuração Avançada

### QA Pós-Merge Customizável

O pipeline de merge (`amb jules merge`) lê os comandos de QA do `.amb/amb_project.json` do projeto ativo. Se não configurado, detecta automaticamente a stack (Node/Python/Go).

```json
// .amb/amb_project.json
{
  "qa": {
    "typecheck": "npm run typecheck",
    "build": "npm run build",
    "test": "npm run test"
  }
}
```

### Personalização de Personas

Crie arquivos `.md` em `.amb/personas/` com o seguinte formato:

```markdown
# Nome da Persona

Descrição resumida (aparece no `amb agent --list`).

## Missão

Instruções detalhadas que serão enviadas ao Google Jules...
```

---

## 📚 6. Documentação Adicional

| Arquivo | Descrição |
| :--- | :--- |
| [`SUGGESTIONS.md`](./SUGGESTIONS.md) | Sugestões de melhoria pendentes organizadas por MoSCoW (MUST/SHOULD/COULD/WON'T). |
| [`CHANGELOG_FIXES.md`](./CHANGELOG_FIXES.md) | Histórico de bugs corrigidos e features implementadas com causa raiz e commits. |
| [`config/README.md`](./config/README.md) | Guia de variáveis de ambiente e estrutura do `.env`. |
| [`gui/README.md`](./gui/README.md) | Documentação do Assistente Gráfico Interativo (Tkinter) e Gestor de .env. |
| [`pipeline/README.md`](./pipeline/README.md) | Guia da arquitetura de prompts separados Design-to-Deploy. |
| [`dashboard/README.md`](./dashboard/README.md) | Documentação do Sentinela e Monitor Unificado. |

