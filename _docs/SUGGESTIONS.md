# 💡 AMB_V2 — Backlog de Sugestões e Priorização MoSCoW

Este documento consolida as propostas técnicas, novas funcionalidades e melhorias arquiteturais do ecossistema AMB_V2, categorizadas pela metodologia de priorização **MoSCoW** (Must Have, Should Have, Could Have e Won't Have).

---

## 📊 Matriz Resumida de Priorização MoSCoW

| Prioridade | Itens Planejados | Foco Principal | Status Atual |
| :--- | :--- | :--- | :--- |
| 🔴 **MUST HAVE** | • `LoopStateMachine` com persistência (`.amb/loop_state.json`)<br>• `SessionMonitor` e enum `SessionState`<br>• Validador Pré-Commit de Regras (`amb validate --staged`) e `amb hooks install` | Estabilidade do loop contínuo e resiliência a falhas/interrupções | ✅ **100% Concluído (PRs #31, #32, #33)** |
| 🟡 **SHOULD HAVE** | • `ConfigManager` Singleton com cache em memória e `amb config reload`<br>• `LocalTelemetry` em `.amb/telemetry.jsonl` e comando `amb stats`<br>• `PersonaEngine` unificado com interpolação e `amb persona validate` | Otimização de performance local e observabilidade de execução | ✅ **100% Concluído (PRs #34, #35, #36)** |
| 🟢 **COULD HAVE** | • `ConsolePresenter` centralizado (`--json` e `--quiet`)<br>• `LocalQASandbox` e sanitizador de logs de QA em `.amb/logs/qa/`<br>• Scanner Proativo de TODOs (`amb suggest`) inspirado no Jules<br>• Notificações no Google Chat via Webhooks<br>• Deploy serverless no Google Cloud Run (`amb cloudrun`)<br>• Sincronização com Google Secret Manager (`amb secret`)<br>• Exportação de telemetria para Google Sheets / Looker Studio | Refinamentos de DX e expansão de integrações no ecossistema Google | 🟡 **Core Concluído (PR #37)** / Extensões em Backlog |
| 🔵 **WON'T HAVE** | • Reescrita do core em TypeScript ou Rust<br>• Frameworks pesados de injeção de dependência (DI)<br>• Bancos de dados relacionais externos para persistência local<br>• Orquestração complexa de clusters Kubernetes (GKE) | Decisões arquiteturais deliberadas fora do escopo | 🔵 Mantido fora de escopo |

---

## 🔴 1. MUST HAVE — Estabilidade Crítica & Ciclo de Vida do Loop (CONCLUÍDO)

### 1.1. Orquestrador de Estados do Loop Autônomo com Persistência Local (`LoopStateMachine`)
* **Status:** ✅ **Concluído (PR #32)**
* **Módulo Implementado:** `amb_cli/agents/loop_core/loop_state_machine.py`
* **Comandos:** `amb loop status`, `amb loop pause` e `amb loop resume`.
* **Persistência:** `.amb/loop_state.json` com recuperação graciosa e transições atômicas.

### 1.2. Unificação de Polling e Monitoramento de Sessões (`SessionMonitor` & `SessionState`)
* **Status:** ✅ **Concluído (PR #31)**
* **Módulos Implementados:** `amb_cli/integrations/jules/jules_core/session_state.py` e `session_monitor.py`.
* **Benefício:** Eliminação de 7 pontos de código redundante e strings mágicas. Reutilizável por sentinelas, watcher e loop.

### 1.3. Validador Pré-Commit de Regras Locais (`amb validate --staged` e `amb hooks install`)
* **Status:** ✅ **Concluído (PR #33)**
* **Módulos Implementados:** `amb_cli/architecture/rules_manager.py` e `amb_cli/cli_modules/handlers_core/hooks_handler.py`.
* **Comandos:** `amb validate --staged` (audita apenas o que está em stage) e `amb hooks install` (instala hook `.git/hooks/pre-commit`).

---

## 🟡 2. SHOULD HAVE — Performance Local, Configurações & Observabilidade (CONCLUÍDO)

### 2.1. Gerenciador Central de Configurações com Cache em Memória (`ConfigManager`)
* **Status:** ✅ **Concluído (PR #34)**
* **Módulo Implementado:** `amb_cli/core/config_manager.py`.
* **Comando:** `amb config reload`. Elimina centenas de leituras concorrentes em disco do `.env` e `amb_project.json`.

### 2.2. Telemetria Local Estruturada & Comando `amb stats` (`LocalTelemetry`)
* **Status:** ✅ **Concluído (PR #35)**
* **Módulos Implementados:** `amb_cli/core/local_telemetry.py` e `amb_cli/cli_modules/handlers_core/stats_handler.py`.
* **Comando:** `amb stats [--json]`. Registrador append-only em `.amb/telemetry.jsonl` com taxa de sucesso de QA e tempos médios.

### 2.3. Engine Unificada de Templates de Persona (`PersonaEngine`)
* **Status:** ✅ **Concluído (PR #36)**
* **Módulos Implementados:** `amb_cli/agents/persona_engine.py` e `amb_cli/cli_modules/handlers_core/persona_handler.py`.
* **Comando:** `amb persona validate`. Valida conformidade das personas e suporta interpolação dinâmica (`{repo_name}`, `{stack}`, `{qa_command}`).

---

## 🟢 3. COULD HAVE — Refinamentos de DX & Extensões Google Cloud

### 3.1. Camada Centralizada de Apresentação de Terminal (`ConsolePresenter`)
* **Status:** ✅ **Concluído (PR #37)**
* **Módulo Implementado:** `amb_cli/core/console_presenter.py`. Suporte unificado às flags globais `--json` e `--quiet`.

### 3.2. Sandbox Local e Sanitizador de Logs de QA (`LocalQASandbox`)
* **Status:** ✅ **Concluído (PR #37)**
* **Módulo Implementado:** `amb_cli/pipeline/pipeline_core/qa_sandbox.py`. Salva logs em `.amb/logs/qa/` e extrai as 30 linhas essenciais de stacktrace em falhas de compilação/teste.

### 3.3. Notificações no Google Chat (Workspace Webhooks)
* **Status:** ⏳ *Em Backlog*. Notificações estruturadas em salas de equipe para planos aguardando aprovação.

### 3.4. Deploy Serverless no Google Cloud Run (`amb cloudrun`)
* **Status:** ⏳ *Em Backlog*. Comando `amb cloudrun deploy` orquestrando deploys pós-merge.

### 3.5. Sincronização com Google Secret Manager (`amb secret`)
* **Status:** ⏳ *Em Backlog*. Sincronização de credenciais locais com o console GCP.

### 3.6. Scanner Proativo de Débitos Técnicos e TODOs (`amb suggest`)
* **Status:** ⏳ *Em Backlog (Inspirado em Jules Suggested Tasks)*.
* **Origem:** Documentação oficial do Google Jules (`https://jules.google/docs/suggested-tasks/`).
* **Conceito:** Varredura proativa de marcações `# TODO:`, `// TODO:`, `# FIXME:` e pendências técnicas na árvore do projeto.
* **Funcionalidade:** Extração de contexto e rationale ao redor da marcação, listagem no terminal e conversão direta em issues/prompts para resolução autônoma via Google Jules (`amb suggest [--sync-issues] [--dispatch <id>]`).

### 3.7. Painel de Visão de Repositório Categorizado (`amb jules repo` ou `amb jules list --grouped`)
* **Status:** ⏳ *Em Backlog (Inspirado em Jules Repo View)*.
* **Origem:** Documentação oficial do Google Jules (`https://jules.google/docs/repo/`).
* **Conceito:** Dashboard no terminal agrupando sessões do repositório ativo em seções categorizadas: 🔄 Em Execução (`Running`), ⏳ Aguardando Atenção (`Waiting Feedback/Plan`), ✅ Concluídas com PR (`Completed`) e ❌ Falhas (`Failed`).

---

## 🔵 4. WON'T HAVE — Fora de Escopo Desta Fase
* **W1:** Reescrita do Core em Outras Linguagens (Rust / TypeScript).
* **W2:** Frameworks Pesados de Injeção de Dependência (DI Containers).
* **W3:** Bancos de Dados Relacionais Externos para Estado Local (usa SQLite/JSON locais).
* **W4:** Infraestrutura de Orquestração Complexa de Clusters (Kubernetes / GKE).
