# 💡 AMB_V2 — Backlog de Sugestões e Priorização MoSCoW

Este documento consolida exclusivamente as propostas técnicas, novas funcionalidades e melhorias arquiteturais que **ainda não foram implementadas** no ecossistema AMB_V2, categorizadas pela metodologia de priorização **MoSCoW** (Must Have, Should Have, Could Have e Won't Have).

---

## 📊 Matriz Resumida de Priorização MoSCoW

| Prioridade | Itens Planejados | Foco Principal |
| :--- | :--- | :--- |
| 🔴 **MUST HAVE** | • `LoopStateMachine` com persistência local (`.amb/loop_state.json`)<br>• `SessionMonitor` e enum `SessionState`<br>• Validador Pré-Commit de Regras (`amb validate --staged`) | Estabilidade do loop contínuo e resiliência a falhas/interrupções |
| 🟡 **SHOULD HAVE** | • `ConfigManager` Singleton com cache em memória<br>• `LocalTelemetry` em `.amb/telemetry.jsonl` e comando `amb stats`<br>• `PersonaEngine` unificado com interpolação e validação | Otimização de performance local e observabilidade de execução |
| 🟢 **COULD HAVE** | • `ConsolePresenter` centralizado (`--json` e `--quiet`)<br>• `LocalQASandbox` e sanitizador de logs de QA<br>• Notificações no Google Chat via Webhooks<br>• Deploy serverless no Google Cloud Run (`amb cloudrun`)<br>• Sincronização com Google Secret Manager (`amb secret`)<br>• Exportação de telemetria para Google Sheets / Looker Studio<br>• Pipeline visual Stitch ➔ Gemini Multimodal ➔ Jules | Refinamentos de DX e expansão de integrações no ecossistema Google |
| 🔵 **WON'T HAVE** | • Reescrita do core em TypeScript ou Rust<br>• Frameworks pesados de injeção de dependência (DI)<br>• Bancos de dados relacionais externos para persistência local<br>• Orquestração complexa de clusters Kubernetes (GKE) | Decisões arquiteturais deliberadas fora do escopo desta fase |

---

## 🔴 1. MUST HAVE — Estabilidade Crítica & Ciclo de Vida do Loop

Itens de implementação imediata fundamentais para a tolerância a falhas e controle do loop autônomo.

### 1.1. Orquestrador de Estados do Loop Autônomo com Persistência Local (`LoopStateMachine`)
* **Problema Atual:** O comando `amb agent --loop` executa em memória volátil. Interrupções acidentais de terminal, reinicializações ou falhas de rede perdem a contagem de ciclos, persona ativa e rastreamento do PR.
* **Solução Proposta:**
  * Implementar máquina de estados finitos persistente em `.amb/loop_state.json`.
  * Estados suportados: `IDLE`, `SELECTING_PERSONA`, `DISPATCHING_JULES`, `MONITORING_SESSION`, `RUNNING_LOCAL_QA`, `MERGING_PR`, `CYCLE_COMPLETED`, `PAUSED`, `FAILED`.
  * Novos comandos na CLI: `amb loop status`, `amb loop pause` e `amb loop resume`.
  * Recuperação transparente do ponto exato onde o ciclo foi interrompido.

### 1.2. Unificação de Polling e Monitoramento de Sessões (`SessionMonitor` & `SessionState`)
* **Problema Atual:** Rotinas paralelas de polling coexistem em `autonomous_loop.py`, `pipeline.py` e sentinelas, checando strings literais de estado da API do Jules.
* **Solução Proposta:**
  * Criar enum canônico `SessionState` (`IDLE`, `IN_PROGRESS`, `AWAITING_INPUT`, `AWAITING_PLAN_APPROVAL`, `COMPLETED`, `FAILED`).
  * Implementar helpers unificados: `is_awaiting_feedback()`, `is_terminal()`, `is_success()`.
  * Centralizar a rotina de polling em uma classe reutilizável `SessionMonitor`.

### 1.3. Validador Pré-Commit de Regras Locais (`amb validate --staged`)
* **Problema Atual:** Violações das regras arquiteturais (como arquivos com mais de 300 linhas) só são detectadas durante a execução do pipeline ou auditorias manuais.
* **Solução Proposta:**
  * Adicionar a flag `--staged` ao comando `amb validate` para auditar exclusivamente arquivos preparados para commit.
  * Adicionar comando gerador de Git Hook (`amb hooks install`) integrando a validação ao `.git/hooks/pre-commit`.

---

## 🟡 2. SHOULD HAVE — Performance Local, Configurações & Observabilidade

Melhorias de alta relevância técnica para eficiência de I/O, governança de templates e telemetria.

### 2.1. Gerenciador Central de Configurações com Cache em Memória (`ConfigManager`)
* **Problema Atual:** Chamadas repetidas a `get_env()` e `load_project_json()` realizam dezenas de leituras síncronas de disco por minuto durante a execução contínua de agentes e sentinelas.
* **Solução Proposta:**
  * Implementar `ConfigManager` (Singleton) com carregamento atômico e imutabilidade em memória durante o processo.
  * Validação antecipada (fail-fast) com tipos estritos e diagnóstico instantâneo.
  * Método `reload()` exposto via comando `amb config reload`.

### 2.2. Telemetria Local Estruturada & Comando `amb stats` (`LocalTelemetry`)
* **Problema Atual:** O desenvolvedor não possui histórico analítico local sobre tempo de build de QA, taxa de sucesso de auto-respostas ou quantidade de PRs integrados.
* **Solução Proposta:**
  * Registrador estruturado append-only em `.amb/telemetry.jsonl` (armazenamento 100% local, zero chamadas à internet).
  * Métricas coletadas: duração por sessão, taxa de sucesso no QA pós-merge, contagem de PRs integrados e tokens consumidos.
  * Novo comando `amb stats` exibindo relatório consolidado e métricas no terminal.

### 2.3. Engine Unificada de Templates de Persona (`PersonaEngine`)
* **Problema Atual:** O carregamento de personas em `.amb/personas/` possui fallbacks hardcoded em `autonomous_loop.py` e descoberta desacoplada em `local_agent_runner.py`.
* **Solução Proposta:**
  * Centralizar descoberta, resolução e fallbacks padrão em `PersonaEngine`.
  * Validação de sintaxe e seções mínimas via comando `amb persona validate`.
  * Suporte a interpolação dinâmica de variáveis de contexto nos markdowns (`{repo_name}`, `{stack}`, `{rules}`, `{qa_command}`).

---

## 🟢 3. COULD HAVE — Refinamentos de DX & Extensões Google Cloud

Capacidades complementares de experiência de desenvolvimento e integrações gerenciadas com o ecossistema Google.

### 3.1. Camada Centralizada de Apresentação de Terminal (`ConsolePresenter`)
* Padronizar a formatação de tabelas, cores e logs em um módulo único.
* Suporte universal e consistente às flags globais `--json` (saída estruturada pura) e `--quiet` / `-q` (apenas códigos de saída numéricos).

### 3.2. Sandbox Local e Sanitizador de Logs de QA (`LocalQASandbox`)
* Armazenamento de logs detalhados de execução de QA em `.amb/logs/qa/qa_<timestamp>.log`.
* Parser inteligente para extrair concisamente as 20-30 linhas essenciais de stacktrace em falhas de compilação/teste, evitando limites de contexto ou truncamentos acidentais.

### 3.3. Notificações e Cards Interativos no Google Chat (Workspace Webhooks)
* Notificações estruturadas em salas de equipe no Google Chat para planos aguardando aprovação e alertas de PRs integrados com sucesso.

### 3.4. Deploy Serverless Contínuo no Google Cloud Run (`amb cloudrun`)
* Novo comando `amb cloudrun deploy` orquestrando builds e deploys serverless pós-merge, com monitoramento de URL e Scale-to-Zero.

### 3.5. Sincronização com Google Secret Manager (`amb secret`)
* Comandos `amb secret pull` e `amb secret push` para sincronizar credenciais seguras entre o console GCP e o `.env` local.

### 3.6. Exportação de Métricas para Google Sheets / Looker Studio
* Exportação periódica dos dados de `.amb/telemetry.jsonl` para planilhas do Google Sheets para dashboards corporativos de produtividade.

### 3.7. Pipeline Visual Stitch ➔ Gemini Multimodal ➔ Jules
* Envio automático de screenshots de telas do Stitch para análise de conformidade de layout via Gemini Vision antes do envio de instruções de código ao Jules.

---

## 🔵 4. WON'T HAVE — Fora de Escopo Desta Fase

Decisões de design e limites arquiteturais estabelecidos para preservar a simplicidade, portabilidade e performance local do AMB_V2:

* **W1 — Reescrita do Core em Outras Linguagens (Rust / TypeScript):** O ecossistema Python nativo atende com máxima velocidade, legibilidade e compatibilidade direta com os SDKs de IA.
* **W2 — Frameworks Pesados de Injeção de Dependência (DI Containers com Reflection):** A injeção explícita de dependências via construtores e módulos canônicos mantém o código auditável, testável e sem comportamentos mágicos.
* **W3 — Bancos de Dados Relacionais Externos (Postgres / MySQL) para Estado Local:** A persistência local em arquivos leves (`.amb/loop_state.json`, `.amb/telemetry.jsonl`) e SQLite é versionável, leve e não exige serviços/daemons em background.
* **W4 — Infraestrutura de Orquestração Complexa de Clusters (Kubernetes / GKE):** O ecossistema foca em automação de engenharia no repositório e deploys serverless pontuais (Cloud Run), evitando complexidade desnecessária de orquestração de containers.
