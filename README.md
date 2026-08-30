# 🚀 AMB_V2 — CLI Global de Automação, Agentes e Integrações

O **`amb_v2`** é um ecossistema universal de automação, agentes cognitivos e engenharia de software para monorepos e aplicações modernas. Ele pode ser executado tanto via **CLI global unificada (`amb`)** quanto diretamente pelos **scripts individuais (`python ...`)** para 100% de retrocompatibilidade.

---

## 📦 1. Instalação Global (Single Source of Truth)

Instale o pacote globalmente em **modo editável (`-e`)** a partir da pasta do `amb_v2`:

```bash
pip install -e amb_v2/
```

> **💡 Vantagem do modo `-e`:** Qualquer melhoria ou novo comando adicionado ao `amb_v2` passa a valer **instantaneamente** para todos os projetos no seu terminal, sem necessidade de reinstalação!

---

## 🧭 2. Tabela de Equivalência de Comandos (Scripts Anteriores vs Novo CLI)

Abaixo está o mapeamento exato de validação de todos os comandos do repositório:

| Script / Ferramenta Anterior | Novo Comando Unificado (`amb`) | Status | O que faz |
| :--- | :--- | :---: | :--- |
| `python config/config.py` | `amb check` (ou `amb status`) | ✅ Ativo | Valida credenciais do `.env` e integridade do projeto. |
| `python config/setup_project.py` | `amb setup` (ou `amb init`) | ✅ Ativo | Assistente inteligente de provisionamento e stack. |
| `python config/setup_project.py --prompt` | `amb prompt` | ✅ Ativo | Exibe o Prompt Mestre de Auto-Configuração para IAs. |
| `python integrations/antigravity/tools/synthesize_prompt.py --idea "..."` | `amb prompt --synthesize "..."` | ✅ Ativo | Sintetiza ideia informal em prompt técnico com Gemini. |
| `python dashboard/unified_monitor.py` | `amb monitor` | ✅ Ativo | Sentinela contínuo em tempo real (Jules + Render). |
| `python dashboard/unified_monitor.py --check-once` | `amb monitor --check-once` (`-1`) | ✅ Ativo | Checagem de 1 ciclo e encerramento imediato. |
| `python dashboard/unified_monitor.py --auto-approve` | `amb monitor --auto-approve` (`-y`) | ✅ Ativo | Sentinela com auto-resposta de dúvidas via Gemini. |
| `python dashboard/auto_advisor.py` | `amb advisor` (ou `amb monitor -i`) | ✅ Ativo | Menu cognitivo interativo para responder chats do Jules. |
| `python dashboard/dashboard_server.py` | `amb dashboard` (ou `amb web`, `amb ui`) | ✅ Ativo | Servidor e SPA do Dashboard Web em tempo real (porta 3333). |
| `python agents/local_agent_runner.py --list` | `amb agent --list` (`-l`) | ✅ Ativo | Lista personas disponíveis em `.amb/personas/`. |
| `python agents/local_agent_runner.py --role relay` | `amb agent --role relay` (`-r`) | ✅ Ativo | Executa persona específica localmente com CLI `agy`. |
| `python agents/local_agent_runner.py --role relay -j` | `amb agent --role relay -j` | ✅ Ativo | Despacha persona para a nuvem do Google Jules. |
| `python agents/autonomous_loop.py` | `amb agent --loop` (`-c`) | ✅ Ativo | **Loop Contínuo:** ciclo de personas, monitoramento e merge. |
| `python integrations/jules/tools/list_sessions.py` | `amb jules list` | ✅ Ativo | Lista sessões recentes no Google Jules. |
| `python integrations/jules/tools/get_session.py <id>` | `amb jules get <id>` | ✅ Ativo | Detalhes da sessão, status e link do PR. |
| `python integrations/jules/tools/monitor_activities.py <id>` | `amb jules get <id> --watch` (`-w`) | ✅ Ativo | Streaming em tempo real das atividades/bash da sessão. |
| `python integrations/jules/tools/create_session.py` | `amb jules create -p "..."` | ✅ Ativo | Cria uma nova sessão no Google Jules. |
| `python integrations/jules/tools/send_message.py` | `amb jules reply -s <id> -m "..."` | ✅ Ativo | Envia mensagem manual direta para o chat da sessão. |
| `python agents/auto_reply.py -s <id>` | `amb jules reply -s <id>` | ✅ Ativo | Sugere e envia resposta formulada pelo Gemini. |
| `python integrations/jules/tools/approve_plan.py` | `amb jules approve -s <id>` | ✅ Ativo | Aprova plano proposto pelo agente (`:approvePlan`). |
| `python integrations/jules/tools/merge_session_pr.py` | `amb jules merge -s <id>` | ✅ Ativo | Aprova, faz merge do PR no GitHub e valida build local. |
| `python integrations/jules/tools/cleanup_sessions.py` | `amb jules clean` (ou `cleanup`) | ✅ Ativo | Audita e remove sessões já integradas no Git. |
| `python integrations/stitch/tools/generate_screen.py` | `amb stitch generate -p "..."` | ✅ Ativo | Gera nova tela visual via Stitch SDK. |
| `python integrations/stitch/tools/edit_screen.py` | `amb stitch refine -s <id> -p "..."` | ✅ Ativo | Refina tela existente no Stitch. |
| `python integrations/stitch/tools/generate_variants.py` | `amb stitch variants -s <id>` | ✅ Ativo | Gera 3 ou mais variantes visuais exploratórias. |
| `python integrations/stitch/tools/sync_design_system.py` | `amb stitch sync` | ✅ Ativo | Sincroniza design tokens do `design.md` com a nuvem. |
| `python integrations/stitch/tools/get_screen.py` | `amb stitch get -s <id>` | ✅ Ativo | Baixa HTML e screenshot da tela gerada. |
| `python integrations/render/tools/list_services.py` | `amb render services` | ✅ Ativo | Lista serviços e IDs configurados na conta Render. |
| `python integrations/render/tools/get_deploy_status.py` | `amb render status` | ✅ Ativo | Status do deploy mais recente do Render. |
| `python integrations/render/tools/fetch_logs.py` | `amb render logs` | ✅ Ativo | Últimos logs de build/execução do Render. |
| `python integrations/render/tools/trigger_deploy.py` | `amb render deploy` | ✅ Ativo | Dispara novo deploy no Render. |
| `python integrations/antigravity/tools/validate_architecture.py` | `amb validate <arquivo>` (ou `lint`) | ✅ Ativo | Audita código contra as regras arquiteturais. |
| `python pipeline/pipeline.py <arquivo.md>` | `amb pipeline <arquivo.md>` | ✅ Ativo | Pipeline ponta a ponta Design-to-Deploy. |
| `python architecture/db_schema_reader.py` | `amb schema [filtro]` (ou `db`) | ✅ Ativo | Inspeciona schemas e tabelas de banco de dados. |
| `python architecture/ai_context_builder.py` | `amb context <modulo>` (ou `ctx`) | ✅ Ativo | Gera roteiro de leitura ordenado por camadas para IA. |

---

## 🚀 3. Exemplos Práticos de Uso

### 🔹 Diagnóstico & Setup:
```bash
amb check
amb setup
amb prompt --synthesize "Criar tela de checkout responsiva com Stripe"
```

### 🔹 Sentinela & Dashboard Web:
```bash
amb monitor -1              # Checagem instantânea de status
amb monitor -i              # Menu cognitivo (ou: amb advisor)
amb monitor -y              # Sentinela contínuo com auto-resposta Gemini
amb dashboard               # Inicia o Dashboard Web na porta 3333
```

### 🔹 Personas & Ciclos Autônomos:
```bash
amb agent --list            # Lista personas (.md)
amb agent --role relay      # Executa persona específica localmente
amb agent --role relay -j   # Despacha persona para o Jules na nuvem
amb agent --loop            # Loop contínuo com monitoramento e merge automático
```

### 🔹 Google Jules & Integração Git:
```bash
amb jules list                      # Lista sessões
amb jules get <id> --watch          # Streaming em tempo real de logs
amb jules reply -s <id>             # Responde dúvida com Gemini
amb jules reply -s <id> -m "texto"  # Mensagem manual direta
amb jules merge -s <id>             # Merge do PR no GitHub + typecheck local
amb jules clean                     # Limpeza na nuvem de sessões integradas
```

---

## 📂 4. Estrutura Arquitetural do Ecossistema

```text
📁 amb_v2/
├── pyproject.toml / setup.py        # Configuração de build e comando global 'amb'
├── cli.py                           # CLI global unificada (Single Source of Truth)
├── config/
│   ├── config.py                    # Gerenciador central de .env e caminhos
│   └── setup_project.py             # Assistente de provisionamento
├── architecture/
│   ├── db_schema_reader.py          # Leitor de schemas e banco de dados (Read-Only)
│   └── ai_context_builder.py        # Construtor de contexto por camadas para IA
├── agents/
│   ├── auto_reply.py                # Resposta cognitiva com Gemini e histórico
│   ├── autonomous_loop.py           # Loop contínuo autônomo (Jules + Gemini + Merge)
│   └── local_agent_runner.py        # Executor dinâmico de personas
├── dashboard/
│   ├── dashboard_server.py          # Servidor e SPA do Dashboard Web (Porta 3333)
│   ├── unified_monitor.py           # Sentinela contínuo e loop de vigilância
│   └── watchers/                    # Watchers do Jules e Render
├── integrations/
│   ├── antigravity/
│   │   ├── antigravity_client.py    # Client Gemini + síntese de prompt e validação
│   │   └── tools/                   # Facades (synthesize_prompt, validate_architecture)
│   ├── jules/
│   │   ├── jules_client.py          # Client REST API oficial do Jules
│   │   └── tools/                   # Facades e Automações Git (merge_session_pr, cleanup)
│   ├── render/
│   │   ├── render_client.py         # Client oficial Render Cloud
│   │   └── tools/                   # Facades (list_services, trigger_deploy, logs)
│   └── stitch/
│       ├── stitch_client.mjs        # Runner Node.js do Stitch SDK
│       ├── stitch_client.py         # Client Python oficial (telas, variantes, design system)
│       └── tools/                   # Facades (generate_screen, edit_screen, variants, sync)
└── pipeline/
    └── pipeline.py                  # Orquestrador Design-to-Deploy ponta a ponta
```
