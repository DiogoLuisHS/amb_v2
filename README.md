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

```
amb [comando] [subcomando] [opções]
```

### ⚙️ 2.1. Configuração e Diagnóstico de Projetos (`setup`, `check`, `prompt`)

| Comando | Descrição |
| :--- | :--- |
| `amb setup` | Executa o assistente inteligente de detecção da stack, gerando `.amb/amb_project.json`, adaptando personas e configurando o `.env`. |
| `amb setup --auto` | Executa o setup e provisionamento em modo não-interativo automático. |
| `amb setup --prompt` ou `amb prompt` | Exibe no terminal o **Prompt Mestre de Auto-Configuração de IA** para colar no chat de qualquer nova IA. |
| `amb check` (ou `amb status`) | Valida e exibe o checklist das chaves de API (`.env`) e integridade do `.amb/amb_project.json`. |

**Exemplos:**
```bash
# Iniciar o assistente no projeto atual:
amb setup

# Ver o prompt para passar para uma nova IA:
amb prompt

# Validar o checklist de ambiente:
amb check
```

---

### 🏛️ 2.2. Arquitetura & Inteligência de Código (`schema`, `context`)

Ferramentas avançadas para análise arquitetural e geração de roteiros de leitura para IAs e desenvolvedores.

| Comando / Opção | Descrição |
| :--- | :--- |
| `amb schema [filtro]` (alias: `amb db`) | Inspeciona tabelas, colunas, tipos e constraints de schemas de banco de dados (Drizzle ORM, etc.) em modo **Read-Only**. |
| `amb context <modulo>` (alias: `amb ctx`) | Mapeia o grafo de dependências do módulo e gera o **Roteiro Ordenado por Camadas (DB ➔ Services ➔ API ➔ UI)** para a IA. |
| `amb context <modulo> --json` | Retorna o grafo e a classificação dos arquivos em JSON estruturado. |

**Exemplos:**
```bash
# Ver todas as tabelas do banco de dados:
amb schema

# Inspecionar tabelas relacionadas ao Kanban:
amb schema kanban

# Gerar o roteiro de arquivos de um módulo para a IA:
amb context agenda
amb ctx kanban
```

---

### 📡 2.3. Sentinela e Monitor de Atenção em Tempo Real (`monitor`)

Monitora continuamente o status de sessões do Google Jules e deploys no Render Cloud, notificando dúvidas de agentes e erros de build.

| Comando / Opção | Descrição |
| :--- | :--- |
| `amb monitor` | Inicia o sentinela contínuo com polling a cada 15s. |
| `amb monitor --auto-approve` (`-y`) | **Piloto Automático:** Responde dúvidas do Jules e aprova planos de execução automaticamente com o Antigravity. |
| `amb monitor --check-once` | Executa apenas uma rodada de checagem e encerra imediatamente. |
| `amb monitor --interval <segundos>` (`-i`) | Define o tempo de espera entre cada checagem (padrão: 15s). |

**Exemplos:**
```bash
# Monitor contínuo padrão:
amb monitor

# Piloto automático (resolução 100% autônoma):
amb monitor --auto-approve

# Checagem rápida de 1 ciclo:
amb monitor --check-once
```

---

### 🧠 2.4. Conselheiro Cognitivo para Dúvidas de Agentes (`advisor`)

Central de resolução de dúvidas que lê o histórico integral turn-by-turn das sessões do Jules e consulta o Antigravity.

| Comando / Opção | Descrição |
| :--- | :--- |
| `amb advisor` | Abre o menu interativo listando todos os chats com dúvidas pendentes para você revisar e aprovar as respostas. |
| `amb advisor --auto-approve` (`-y`) | Responde todas as dúvidas pendentes de todos os chats em lote sem pedir confirmação. |

**Exemplos:**
```bash
amb advisor
amb advisor --auto-approve
```

---

### 🤖 2.5. Personas Autônomas de Manutenção (`agent`)

Descobre dinamicamente os arquivos de persona em `.amb/personas/` e histórico em `.amb/diarios/` do projeto ativo.

| Comando / Opção | Descrição |
| :--- | :--- |
| `amb agent --list` (`-l`) | Lista todas as personas disponíveis na pasta `.amb/personas/` do projeto ativo. |
| `amb agent --role <nome>` (`-r`) | Executa uma persona localmente no repositório usando a CLI oficial `agy`. |
| `amb agent --role <nome> --task "<instruções>"` | Executa a persona combinando o prompt base com instruções específicas adicionais. |
| `amb agent --role <nome> --dispatch-jules` (`-j`) | Despacha a persona para a nuvem do Google Jules (cria Cloud VM, branch e Pull Request). |
| `amb agent --all` (`-a`) | Executa **todas** as personas da pasta sequencialmente em lote. |
| `amb agent --all --dispatch-jules` | Despacha todas as personas da pasta em lote para a nuvem do Jules. |
| `amb agent --personas-dir <caminho>` | Especifica uma pasta customizada de personas. |

**Exemplos:**
```bash
# Ver o catálogo de personas do projeto:
amb agent --list

# Executar a persona Deadwood localmente:
amb agent --role deadwood

# Despachar o Bolt para a nuvem do Google Jules:
amb agent --role bolt --dispatch-jules

# Executar todas as personas em lote na nuvem do Jules:
amb agent --all --dispatch-jules
```

---

### ⚡ 2.6. Google Jules SDK (`jules`)

Comandos diretos de integração com a API REST `v1alpha` do Google Jules.

| Comando / Opção | Descrição |
| :--- | :--- |
| `amb jules list [--limit <N>]` | Lista as sessões e chats recentes do repositório no Jules. |
| `amb jules get <session_id> [--json]` | Consulta os detalhes de uma sessão, estado atual e link do Pull Request. |
| `amb jules create --prompt "<prompt>" [--title "<título>"]` | Cria uma nova sessão de codificação remota no Jules. |
| `amb jules reply --session-id <id> [--auto-approve]` | Extrai o histórico integral da conversa e envia a resposta sugerida pelo Antigravity. |
| `amb jules approve --session-id <id>` | Aprova o plano de ação formulado pelo agente (`:approvePlan`). |

**Exemplos:**
```bash
amb jules list --limit 5
amb jules get <SESSION_ID>
amb jules create --prompt "Refatorar rotas da API" --title "API Refactor"
amb jules reply --session-id <SESSION_ID> --auto-approve
```

---

### 🎨 2.7. Google Stitch SDK (`stitch`)

Comandos de prototipação visual e refinamento de interface com suporte a Light e Dark Mode.

| Comando / Opção | Descrição |
| :--- | :--- |
| `amb stitch generate --prompt "<prompt>" [--title "<título>"]` | Gera uma nova tela HTML/CSS via Google Stitch SDK. |
| `amb stitch refine --screen-id <id> [--theme auto/light/dark] [--feedback "<obs>"]` | Refina uma tela existente com IA respeitando os tokens do Design System (`@theme`). |
| `amb stitch get --screen-id <id>` | Baixa o código HTML/CSS gerado de uma tela específica. |

**Exemplos:**
```bash
amb stitch generate --prompt "Dashboard financeiro moderno com cards de KPI"
amb stitch refine --screen-id <SCREEN_ID> --theme light
amb stitch get --screen-id <SCREEN_ID>
```

---

### 🚀 2.8. Render Cloud (`render`)

Integração com a infraestrutura em nuvem do Render para monitorar status e disparar deploys.

| Comando | Descrição |
| :--- | :--- |
| `amb render status` | Exibe o status do serviço, último deploy e commit associado. |
| `amb render logs` | Consulta e exibe os últimos logs do servidor de produção. |
| `amb render deploy` | Dispara um novo deploy manual via Render API. |

---

### 🔗 2.9. Pipeline Integrado Design-to-Deploy (`pipeline`)

Orquestra o fluxo ponta a ponta: Parsing do Prompt ➔ Geração no Stitch ➔ Gatekeeper de Design ➔ Síntese com Antigravity ➔ Codificação no Jules ➔ Gatekeeper de QA Local (Typecheck + Build).

| Opção | Descrição |
| :--- | :--- |
| `amb pipeline <arquivo.md>` | Executa o pipeline completo a partir de um arquivo markdown de tarefa. |
| `--auto-approve` | Pula confirmações manuais no Gatekeeper 1 de Design. |
| `--screen-id <id>` | Reaproveita o layout de uma tela já existente no Stitch. |
| `--skip-stitch` | Pula a etapa do Stitch e envia diretamente para o Jules. |
| `--no-qa` | Pula a validação local final de typecheck/build. |

**Exemplos:**
```bash
# Executar a partir de uma especificação em .amb/prompts/:
amb pipeline .amb/prompts/09_fase0_arvore_hipoteses.md

# Executar a partir do template genérico:
amb pipeline amb_v2/pipeline/prompts/template_tarefa.md
```

---

## 📂 3. Estrutura Arquitetural do Ecossistema

```
📁 amb_v2/                            <--- CLI Global & Motor de Execução (Agnóstico)
├── pyproject.toml / setup.py        # Configuração de build e comando global 'amb'
├── cli.py                           # Ponto de entrada unificado da CLI
├── config/                          # Gerenciador de ambiente e setup
├── architecture/                    # Leitor de Schemas e Construtor de Contexto para IA
├── agents/                          # Wrappers e runners de personas
├── integrations/                    # Clientes REST (Jules, Stitch, Render, Antigravity)
├── dashboard/                       # Sentinela de monitoramento e live dashboard
└── pipeline/                        # Orquestrador Design-to-Deploy e templates

📁 .amb/                              <--- Inteligência e Regras de cada Repositório
├── personas/                        # Prompts puros das personas (.md)
├── diarios/                         # Diários de aprendizado com histórico de cada persona (.md)
├── prompts/                         # Especificações de telas e tarefas do projeto (.md)
├── amb_project.json                 # Metadados detectados e configuração do projeto
└── README.md                        # Catálogo de personas e resumo do ambiente
```
