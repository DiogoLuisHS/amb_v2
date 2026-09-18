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
| `amb check` | `amb status` | Diagnóstico de saúde do projeto: chaves de API, Git, GitHub CLI, binários de QA e proteção no `.gitignore`. |
| `amb check --json` | — | Emite o diagnóstico de ambiente completo em formato JSON estruturado. |
| `amb setup` | `amb init` | Assistente de detecção de stack, inferência de comandos de QA, persona de exemplo e configuração do `.env`. |
| `amb setup --auto` | — | Executa o setup em modo automático/não-interativo. |
| `amb setup --force` | `-f` | Força a re-geração de arquivos de configuração e personas mesmo se já existirem. |
| `amb setup --path <dir>` | — | Executa o setup apontando para um diretório de projeto específico em vez do atual. |
| `amb setup --dry-run` | — | Simula a detecção de stack e comandos de QA sem gravar arquivos em disco. |
| `amb prompt` | `amb setup -p` | Imprime o Prompt Mestre de Auto-Configuração para colar em novas IAs. |
| `amb prompt --synthesize "<ideia>"` | `-s` | Converte uma ideia informal em prompt arquitetural estruturado com Gemini (`-o` para salvar). |
| `amb prompt --role <especialidade>` | `-r` | Define a especialidade da IA para a síntese do prompt (ex: `frontend`, `security`). |
| `amb config` | `settings`, `pref` | Exibe o status da autorização prévia para chamadas ao Gemini. |
| `amb config --gemini-confirm <on/off>` | — | Ativa (`on`) ou desativa (`off`) a exigência de confirmação interativa antes de requisições ao Gemini. |

```bash
# Exemplos:
amb check
amb check --json
amb setup --auto
amb setup --path ../meu-outro-projeto --auto
amb prompt --synthesize "Criar painel de métricas financeiras" --role frontend -o prompt.md
amb config --gemini-confirm off                 # Habilitar chamadas autônomas ao Gemini sem interrupção
```

---

### 📡 2.2. Sentinela, Advisor & Assistente Gráfico (`monitor`, `advisor`, `gui`)

Vigilância em tempo real das sessões do Jules, auto-resposta via Gemini e Assistente Gráfico nativo para montagem de comandos e gestão de variáveis do `.env`.

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
| `amb agent --role <nome>` | `-r` | Executa uma persona localmente via CLI `agy` (ex: `engineer`, ou customizadas). |
| `amb agent --role <nome> --dispatch-jules` | `-j` | Despacha a persona para a nuvem do Google Jules (Cloud VM + Branch + PR). |
| `amb agent --role <nome> --task "<texto>"` | `-t` | Anexa instruções ou escopo adicional ao prompt base da persona. |
| `amb agent --all` | `-a` | Executa todas as personas da pasta sequencialmente em lote. |
| `amb agent --loop` | `-c`, `--continuous` | **Ciclo Autônomo:** loop contínuo de envio, vigilância, auto-reply e auto-merge no Git. |
| `amb agent --all --loop` | — | Loop autônomo iterando por **todas as personas** a cada ciclo. |
| `amb agent --loop --max-cycles <N>` | — | Limita a execução do loop a N ciclos completos antes de parar. |
| `amb agent --loop --branch <branch>` | `-b` | Define o branch-alvo para criação da sessão Jules (padrão: `develop`). |
| `amb agent --loop --modules <m1,m2>` | `-m` | Rotaciona o foco entre módulos do repositório a cada ciclo. |
| `amb agent --loop --no-auto-merge` | — | Desabilita o merge automático do Pull Request ao concluir o ciclo com sucesso. |
| `amb agent --personas-dir <pasta>` | — | Define um diretório customizado de personas. |

> **💡 `amb context` automático no loop:** ao despachar cada sessão, o `autonomous_loop` roda automaticamente `amb context <modulo>` e **anexa o roteiro arquitetural completo** (DB → Services → UI) ao prompt enviado ao Jules, reduzindo em 20-30min o tempo de exploração inicial por sessão.

```bash
# Exemplos:
amb agent --list                                        # Ver personas disponíveis
amb agent --role engineer                               # Executar persona localmente
amb agent --role engineer -j                            # Despachar persona para o Jules na nuvem
amb agent --role engineer --loop                        # Loop contínuo infinito com auto-merge de PR
amb agent --role engineer --loop --max-cycles 3         # Loop com limite de 3 ciclos
amb agent --all --loop --max-cycles 2                   # Todas as personas, 2 ciclos completos
amb agent --all --loop --branch main --max-cycles 5     # Loop na branch main
amb agent --role engineer --loop --modules api,web      # Rotacionar entre módulos por ciclo
```

---

### ⚡ 2.4. Google Jules Cloud (`jules`)

Integração direta com o Google Jules para desenvolvimento remoto e gestão de PRs no GitHub.

| Comando / Opção | Alias | Descrição |
| :--- | :--- | :--- |
| `amb jules status` | `check` | Diagnóstico de conectividade, API Key, fontes conectadas e sessões ativas (`--json`). |
| `amb jules sources` | `source` | Lista repositórios e fontes conectados na conta Google Jules (`--json`). |
| `amb jules list` | — | Lista sessões do repositório (`--limit`, `--all`, `--repo`, `--state`, `--json`). |
| `amb jules get <id_ou_url>` | — | Exibe detalhes da sessão, status da VM e URL do Pull Request (`--json`). |
| `amb jules get <id_ou_url> --watch`| `-w` | Acompanha streaming em tempo real das atividades, mensagens e comandos bash. |
| `amb jules create -p "<prompt>"` | `--prompt` | Cria uma nova sessão no Jules vinculada ao repositório do `.env` (`--branch`, `--json`). |
| `amb jules create -p "..." -t "<título>"` | `--title` | Cria uma sessão com título personalizado. |
| `amb jules reply` | `advisor` | Abre menu interativo com IA para listar e responder dúvidas pendentes. |
| `amb jules reply <id>` | `--session-id` | Gera sugestão com Gemini e responde turn-by-turn a uma sessão específica. |
| `amb jules reply <id> -m "<texto>"` | `--message` | Envia mensagem manual direta para o chat da sessão no Jules (`--force`). |
| `amb jules reply <id> -y` | `--auto-approve`| Envia a resposta sugerida pelo Gemini imediatamente sem pedir confirmação. |
| `amb jules approve <id>` | `--session-id` | Valida guardrails e aprova o plano de ação formulado pelo agente (`:approvePlan`, `--force`). |
| `amb jules merge <id>` | `--session-id` | Detecta o PR da sessão, publica se Draft, aprova, faz merge e valida QA local (`--branch`). |
| `amb jules merge --auto-latest` | — | Detecta e faz merge do Pull Request aberto mais recente (incluindo Drafts). |
| `amb jules clean` | `cleanup` | Audita e remove na nuvem do Jules as sessões já integradas no Git (`-f` para forçar). |
| `amb jules clean --failed` | — | Remove as sessões que terminaram em estado de erro fatal (FAILED). |
| `amb jules clean --merged` | — | Remove sessões com PRs já mesclados no Git. |

> **💡 Normalização Universal de IDs:** Todos os comandos do Jules aceitam ID puro (`175...`), formato REST (`sessions/175...`) ou URL direta do navegador (`https://jules.google.com/session/175...`).
> **💡 Publicação automática de Draft PRs:** O Jules sempre cria PRs como **Draft**. O pipeline `amb jules merge` executa `gh pr ready` automaticamente antes do merge, sem necessidade de intervenção manual.

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
| `amb stitch list` | — | Lista todas as telas criadas no projeto Stitch ativo. |
| `amb stitch generate -p "<prompt>"` | `--prompt` | Gera uma nova tela visual (Mobile, Desktop, Tablet ou Agnóstico). |
| `amb stitch refine -s <id> -p "<prompt>"` | `--screen-id` | Refina uma tela existente com novas instruções visuais. |
| `amb stitch get -s <id>` | `--screen-id` | Obtém o código HTML/CSS, DOM e screenshot da tela. |
| `amb stitch variants -s <id> -c <N>` | `--count` | Gera variantes visuais exploratórias (1-5 variações). |
| `amb stitch download -o <dir>` | `--output` | Baixa telas e assets do projeto para um diretório local. |
| `amb stitch project` | — | Consulta metadados e instâncias do projeto Stitch atual. |
| `amb stitch sync` | — | Sincroniza `design.md` com o Design System oficial do Stitch. |
| `amb stitch call <tool> '<json>'` | — | Invoca qualquer ferramenta oficial do Stitch SDK via JSON-RPC. |

```bash
# Exemplos:
amb stitch list
amb stitch generate -p "Dashboard SaaS com cards de KPI" -d MOBILE -o public/dashboard.html
amb stitch refine -s <SCREEN_ID> -p "Tornar os botões arredondados e ajustar contraste"
amb stitch variants -s <SCREEN_ID> --count 3
amb stitch download -o ./dist/stitch_assets
amb stitch sync -f design.md
amb stitch project
```

---

### 🔍 2.6. Qualidade, Pipeline, Schemas & Contexto (`validate`, `pipeline`, `schema`, `context`)

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
| `amb validate <arquivo>` | `lint`, `audit` | Audita o código contra as diretrizes e regras de `.agents/rules/` (`--json`). |
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

### 🧠 2.7. Google Antigravity & Inferência Cognitiva (`agy`, `antigravity`)

Integração nativa com o motor cognitivo do Google Antigravity e Gemini, governança de regras de arquitetura e validação estática de conformidade.

| Comando / Opção | Alias | Descrição |
| :--- | :--- | :--- |
| `amb agy status` | `check` | Diagnóstico de saúde do runtime agy, chaves e regras arquiteturais ativas (`--json`). |
| `amb agy rules` | — | Lista e inspeciona as regras arquiteturais do repositório (`--content`, `-c`, `--json`). |
| `amb agy prompt -i "<ideia>"` | `synthesize`, `synth` | Sintetiza ideia informal em prompt formal com regras ativas (`-r <role>`, `-o <saida>`). |
| `amb agy validate <arquivo>` | `lint`, `audit` | Audita conformidade arquitetural do arquivo contra as regras do repositório (`--json`). |
| `amb agy run "<prompt>"` | `eval` | Inferência cognitiva direta via modelo Gemini (`-m <model>`, `-t <temp>`, `-s <system>`, `-o <saida>`). |

```bash
# Exemplos:
amb agy status                                  # Status do runtime e chaves
amb agy rules --content                         # Exibir conteúdo integral consolidado das regras
amb agy prompt -i "Refatorar modal de login" -r frontend -o prompt.md
amb agy validate amb_cli/gui/wizard_app.py      # Auditar arquivo contra regras arquiteturais
amb agy run "Explique a arquitetura em camadas" -m gemini-2.5-flash
```

---

### 🐙 2.8. Controle de Versão e Pull Requests via Git (`git`)

Controle de versão local, sincronização de branches e automação completa de Pull Requests no GitHub via GitHub CLI (`gh`).

| Comando / Opção | Alias | Descrição |
| :--- | :--- | :--- |
| `amb git status` | — | Exibe status detalhado do Git local, branches, upstream e integridade da CLI `gh` (`--json`). |
| `amb git sync` | — | Sincroniza branch ativa com o remote (`fetch` + `pull` com auto-stash; `-r <remote>`, `-b <branch>`). |
| `amb git diff [arquivo]` | — | Exibe diff unificado de arquivos alterados ou preparados (`--base <branch>`, `--cached`). |
| `amb git pr list` | — | Lista Pull Requests abertos no GitHub (`--no-drafts`, `--repo <dono/repo>`, `--json`). |
| `amb git pr get <id>` | — | Exibe detalhes estruturados, status de checks e comentários do PR (`--json`). |
| `amb git pr create -t "<titulo>"` | — | Cria novo Pull Request no GitHub (`-b "<body>"`, `--base <b>`, `--head <h>`, `--draft`). |
| `amb git pr ready <id>` | — | Marca um Pull Request em rascunho (Draft) como pronto para revisão (`gh pr ready`). |
| `amb git pr approve <id>` | — | Aprova formalmente o Pull Request no GitHub (`--body "<comentario>"`). |
| `amb git pr merge <id>` | — | Faz merge do Pull Request com squash e deleção de branch (`--no-squash`, `--keep-branch`). |
| `amb git pr close <id>` | — | Fecha o Pull Request no GitHub sem realizar merge (`--comment "<motivo>"`, `--delete-branch`). |

```bash
# Exemplos:
amb git status
amb git sync -r origin -b main
amb git diff --cached
amb git pr list
amb git pr create -t "feat: autenticação JWT" -b "Implementa tokens e refresh rotativo"
amb git pr ready 42
amb git pr approve 42 --body "Aprovado via QA AMB"
amb git pr merge 42
```

---

## 📋 3. Tabela de Referência Rápida de Todos os Comandos

| Categoria | Comando CLI Principal | Atalho / Equivalente Direto |
| :--- | :--- | :--- |
| **Setup & Env** | `amb check` | `amb check --json` |
| **Setup & Env** | `amb setup` | `amb setup --auto [--path <dir>]` |
| **Setup & Env** | `amb prompt` | `amb setup -p` |
| **Setup & Env** | `amb prompt -s "<ideia>"` | `amb agy prompt -i "<ideia>"` |
| **Setup & Env** | `amb config` | `amb config --gemini-confirm <on/off>` |
| **Vigilância** | `amb monitor` | `amb monitor -y` (Sentinela Autônomo) |
| **Vigilância** | `amb monitor -1` | `amb monitor --check-once` |
| **Vigilância** | `amb advisor` | `amb jules reply` (Menu cognitivo) |
| **Interface** | `amb gui` | `amb ui` (Assistente Gráfico Tkinter) |
| **Personas** | `amb agent --list` | `amb agent -l` |
| **Personas** | `amb agent --role <nome>` | `amb agent -r <nome>` (Jules Cloud) |
| **Personas** | `amb agent --role <nome> --agy`| `amb agent -r <nome> --local` (Local CLI) |
| **Personas** | `amb agent --loop` | `amb agent -c` (Loop contínuo autônomo) |
| **Personas** | `amb agent --all --loop` | Executa todas as personas em ciclo infinito |
| **Personas** | `amb agent --loop --max-cycles <N>` | Loop contínuo com limite de ciclos |
| **Personas** | `amb agent --loop --modules <m1,m2>` | Loop rotacionando módulos de foco |
| **Personas** | `amb agent --loop --no-auto-merge` | Desabilita merge automático pós-ciclo |
| **Jules Cloud** | `amb jules status` | Diagnóstico de API e fontes conectadas |
| **Jules Cloud** | `amb jules sources` | Lista fontes conectadas na conta Jules |
| **Jules Cloud** | `amb jules list` | Lista sessões (`--limit <N>`, `--all`) |
| **Jules Cloud** | `amb jules get <id>` | Detalhes e status da sessão |
| **Jules Cloud** | `amb jules get <id> --watch` | Streaming de logs e atividades ao vivo |
| **Jules Cloud** | `amb jules create -p "..."` | Cria sessão (`-t "<titulo>"`, `-b <branch>`) |
| **Jules Cloud** | `amb jules reply -s <id>` | Auto-resposta turn-by-turn com Gemini |
| **Jules Cloud** | `amb jules reply -s <id> -m "..."` | Mensagem direta manual para a sessão |
| **Jules Cloud** | `amb jules approve -s <id>` | Aprova o plano de ação formulado |
| **Jules Cloud** | `amb jules merge -s <id>` | Merge do PR no GitHub + QA local |
| **Jules Cloud** | `amb jules merge --auto-latest` | Merge automático do PR mais recente |
| **Jules Cloud** | `amb jules clean` | Limpeza de sessões concluídas/mescladas |
| **Stitch SDK** | `amb stitch list` | Lista todas as telas do projeto |
| **Stitch SDK** | `amb stitch generate -p "..."` | Gera tela (`-d <device>`, `-o <html_file>`) |
| **Stitch SDK** | `amb stitch refine -s <id> -p "..."` | Refina tela existente com novos tokens |
| **Stitch SDK** | `amb stitch get -s <id>` | Obtém código HTML, CSS e screenshot |
| **Stitch SDK** | `amb stitch variants -s <id>` | Gera variantes visuais (`-c <count>`) |
| **Stitch SDK** | `amb stitch download -o <dir>` | Baixa assets e telas do projeto |
| **Stitch SDK** | `amb stitch project` | Consulta metadados do projeto Stitch |
| **Stitch SDK** | `amb stitch sync` | Sincroniza design tokens (`design.md`) |
| **Stitch SDK** | `amb stitch call <tool> '<json>'` | Invoca JSON-RPC tool no Stitch SDK |
| **Antigravity** | `amb agy status` | Status do runtime cognitivo e regras |
| **Antigravity** | `amb agy rules` | Lista regras ativas (`--content`, `-c`) |
| **Antigravity** | `amb agy prompt -i "..."` | Sintetiza prompt executivo com regras |
| **Antigravity** | `amb agy validate <arquivo>` | `amb validate <arquivo>` (Auditoria de código) |
| **Antigravity** | `amb agy run "..."` | Inferência cognitiva direta via Gemini |
| **Git & PRs** | `amb git status` | Status local Git, upstream e GitHub CLI |
| **Git & PRs** | `amb git sync` | Fetch + Pull com auto-stash |
| **Git & PRs** | `amb git diff [--cached]` | Exibe diff unificado |
| **Git & PRs** | `amb git pr list` | Lista Pull Requests abertos |
| **Git & PRs** | `amb git pr get <id>` | Detalhes estruturados do PR |
| **Git & PRs** | `amb git pr create -t "..."` | Cria Pull Request no GitHub |
| **Git & PRs** | `amb git pr ready <id>` | Converte Draft PR em Ready for Review |
| **Git & PRs** | `amb git pr approve <id>` | Aprova Pull Request no GitHub |
| **Git & PRs** | `amb git pr merge <id>` | Realiza o merge do PR |
| **Git & PRs** | `amb git pr close <id>` | Fecha Pull Request sem merge |
| **Pipeline** | `amb pipeline -s <s.md> -j <j.md>` | Orquestrador Design-to-Deploy ponta a ponta |
| **Pipeline** | `amb pipeline -j <j.md> --skip-stitch` | Tarefa de engenharia pura (sem tela) |
| **Pipeline** | `amb pipeline --resume-session <id>` | Retoma monitoramento de sessão remota |
| **Arquitetura** | `amb schema [filtro]` | Consulta catálogo Drizzle DB (Read-Only) |
| **Arquitetura** | `amb context <modulo>` | Roteiro de arquivos em camadas para IA |

---

## 📂 4. Estrutura do Repositório

```text
📁 amb_v2/
├── pyproject.toml / setup.py        # Configuração de build e comando global 'amb'
├── amb_cli/                         # Pacote Python principal da CLI (92 arquivos, todos <= 300 linhas)
│   ├── cli.py                       # Ponto de entrada CLI (Single Source of Truth)
│   ├── cli_modules/                 # Handlers e parsers modulares da CLI (SRP)
│   │   ├── alert_notifier.py        # Emissor de alertas visuais e sonoros
│   │   ├── cli_handlers.py          # Despacho enxuto de subcomandos
│   │   ├── cli_parsers.py           # Definição modular de argumentos e subcomandos
│   │   └── handlers_core/           # Handlers desacoplados por domínio (antigravity, git, jules, stitch)
│   ├── config/                      # Governança de ambiente, bootstrap e setup
│   │   ├── config.py                # Diagnóstico de saúde e variáveis (.env)
│   │   ├── bootstrap.py             # Bootstrap centralizado de ambiente e sys.path
│   │   ├── rules_manager.py         # Governança e cache das regras arquiteturais
│   │   ├── setup_project.py         # Orquestrador do fluxo amb setup
│   │   ├── config_core/             # Núcleo de diagnósticos e tokens de design
│   │   └── setup_modules/           # Analisador de projetos, provisionador .amb/ e sintetizador
│   ├── gui/                         # Assistente Gráfico Nativo (UI Wizard)
│   │   ├── wizard_app.py            # Janela mestre e launcher do Wizard (Tkinter)
│   │   └── wizard_core/             # Runner dinâmico, gestor de .env e parser extractor
│   ├── architecture/                # Inteligência de repositório e leitura de schemas
│   │   ├── db_schema_reader.py      # Leitor de schemas e banco de dados (Read-Only)
│   │   ├── ai_context_builder.py    # Construtor de contexto por camadas para IA
│   │   └── context_core/            # Configurações de camadas e constantes
│   ├── agents/                      # Agentes autônomos e personas
│   │   ├── auto_reply.py            # Resposta cognitiva com Gemini
│   │   ├── autonomous_loop.py       # Loop contínuo autônomo (Jules + Gemini + Auto-Merge)
│   │   ├── local_agent_runner.py    # Executor dinâmico de personas
│   │   ├── monitor.py               # Sentinela contínuo em tempo real
│   │   ├── auto_reply_core/         # Extração de histórico turn-by-turn e conselheiro cognitivo
│   │   └── loop_core/               # Despachante de ciclos e assistente de sessão
│   ├── integrations/                # Integrações oficiais com APIs e SDKs externos
│   │   ├── antigravity/             # Cliente cognitivo Google Antigravity & Gemini REST
│   │   ├── jules/                   # Cliente REST oficial do Google Jules & watcher
│   │   ├── stitch/                  # Cliente oficial para Google Stitch SDK
│   │   ├── git/                     # Serviço de Git de alta performance e automação GitHub CLI
│   │   └── common/                  # BaseGoogleClient com retries e backoff exponencial
│   └── pipeline/                    # Orquestrador Design-to-Deploy
│       ├── pipeline.py              # Orquestrador do fluxo ponta a ponta
│       ├── quality_gatekeeper.py    # Gatekeeper local de QA e integridade
│       └── pipeline_core/           # Estágio de design no Stitch e construtor de prompts
├── .agents/rules/                   # Regras arquiteturais canônicas do ecossistema
└── tests/                           # Suíte de testes unitários (158 testes, 100% green)
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
| [`_docs/SUGGESTIONS.md`](./_docs/SUGGESTIONS.md) | Roadmap estratégico e priorização MoSCoW (MUST/SHOULD/COULD/WON'T) das próximas sprints. |
| [`_docs/CHANGELOG_FIXES.md`](./_docs/CHANGELOG_FIXES.md) | Fonte única da verdade para histórico de melhorias arquiteturais, features e bugs corrigidos. |
| [`amb_cli/config/README.md`](./amb_cli/config/README.md) | Guia de variáveis de ambiente e estrutura do `.env`. |
| [`amb_cli/gui/README.md`](./amb_cli/gui/README.md) | Documentação do Assistente Gráfico Interativo (Tkinter) e Gestor de .env. |
| [`amb_cli/pipeline/README.md`](./amb_cli/pipeline/README.md) | Guia da arquitetura de prompts separados Design-to-Deploy. |

