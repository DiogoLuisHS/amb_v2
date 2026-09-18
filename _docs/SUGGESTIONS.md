# 💡 AMB_V2 — Backlog de Sugestões e Melhorias Futuras

Este documento contém exclusivamente as propostas técnicas, novas funcionalidades e melhorias arquiteturais que **ainda não foram implementadas** no ecossistema AMB_V2.

---

## 🏛️ 1. Core Local & Robustez de Ciclo de Vida

### 1.1. Orquestrador de Estados do Loop Autônomo com Persistência Local (`LoopStateMachine`)
- **Objetivo:** Adicionar persistência de estado para o loop contínuo de agentes (`amb agent --loop`).
- **Escopo:**
  - Persistir o estado atual da execução em `.amb/loop_state.json`.
  - Estados modelados: `IDLE`, `SELECTING_PERSONA`, `DISPATCHING_JULES`, `MONITORING_SESSION`, `RUNNING_LOCAL_QA`, `MERGING_PR`, `CYCLE_COMPLETED`, `PAUSED`, `FAILED`.
  - Adicionar comandos na CLI: `amb loop status`, `amb loop pause` e `amb loop resume`.
  - Permitir a recuperação transparente do ciclo ativo após interrupções de terminal, reinicializações ou quedas de rede.

### 1.2. Unificação de Polling e Monitoramento de Sessões (`SessionMonitor` & `SessionState`)
- **Objetivo:** Eliminar checagens paralelas de estados de sessão entre o loop autônomo, pipeline e sentinela.
- **Escopo:**
  - Criar enum tipado `SessionState` (`IDLE`, `IN_PROGRESS`, `AWAITING_INPUT`, `AWAITING_PLAN_APPROVAL`, `COMPLETED`, `FAILED`).
  - Implementar métodos utilitários: `is_awaiting_feedback()`, `is_terminal()`, `is_success()`.
  - Unificar a rotina de polling em uma classe reutilizável `SessionMonitor`.

### 1.3. Gerenciador Central de Configurações com Cache em Memória (`ConfigManager`)
- **Objetivo:** Reduzir leituras redundantes de disco das variáveis de `.env` e `.amb/amb_project.json`.
- **Escopo:**
  - Implementar Singleton `ConfigManager` com carregamento único na inicialização da aplicação.
  - Imutabilidade dos valores carregados durante o ciclo de vida do processo.
  - Método `reload()` acionável via comando `amb config reload`.

### 1.4. Telemetria Local Estruturada & Comando `amb stats` (`LocalTelemetry`)
- **Objetivo:** Oferecer visibilidade sobre o desempenho e histórico das execuções de agentes sem depender de serviços externos.
- **Escopo:**
  - Armazenamento local append-only em `.amb/telemetry.jsonl` (zero envio para internet).
  - Métricas registradas: duração por sessão, taxa de sucesso de testes no QA pós-merge, contagem de PRs integrados e tokens consumidos.
  - Novo comando `amb stats` exibindo tabela consolidada de métricas no terminal.

### 1.5. Engine Unificada de Templates de Persona (`PersonaEngine`)
- **Objetivo:** Padronizar a resolução, validação e interpolação de personas.
- **Escopo:**
  - Criar validador de sintaxe de personas (`amb persona validate`).
  - Suporte a interpolação de variáveis dinâmicas de contexto no markdown da persona (`{repo_name}`, `{stack}`, `{rules}`, `{qa_command}`).
  - Centralização dos fallbacks nativos e do carregamento customizado.

---

## 🛠️ 2. Ferramentas de Linha de Comando (DX) & Resiliência

### 2.1. Camada Centralizada de Apresentação de Terminal (`ConsolePresenter`)
- **Objetivo:** Padronizar a renderização visual da CLI em todos os módulos.
- **Escopo:**
  - Módulo utilitário para exibição de tabelas com largura dinâmica adaptada ao terminal.
  - Suporte global e consistente às flags `--json` (dados estruturados puros) e `--quiet` / `-q` (apenas códigos de retorno).

### 2.2. Sandbox Local e Sanitizador de Logs de QA (`LocalQASandbox`)
- **Objetivo:** Melhorar o diagnóstico de erros de compilação e testes enviados aos agentes cognitivos.
- **Escopo:**
  - Gravação dos logs integrais de execução de QA em `.amb/logs/qa/qa_<timestamp>.log`.
  - Parser inteligente para extrair apenas as 20-30 linhas mais relevantes de stacktrace ou falha, evitando prompts inchados ou cortes acidentais de erros.

### 2.3. Validador Pré-Commit de Regras Locais (`amb validate --staged`)
- **Objetivo:** Prevenir commits com violações de regras arquiteturais diretamente no Git local.
- **Escopo:**
  - Adicionar flag `--staged` ao comando `amb validate` para auditar somente arquivos preparados para commit.
  - Script gerador de Git Hook (`amb hooks install`) para integração direta no `.git/hooks/pre-commit`.

---

## ☁️ 3. Integrações Futuras no Ecossistema Google Cloud

### 3.1. Deploy Serverless Contínuo no Google Cloud Run (`amb cloudrun`)
- **Objetivo:** Orquestrar o deploy de aplicações após o merge automático de PRs.
- **Escopo:**
  - Novo comando `amb cloudrun deploy` disparando builds via Cloud Build ou containers locais.
  - Monitoramento de URL ativa, checagem de saúde e suporte a Scale-to-Zero.

### 3.2. Notificações e Cards Interativos no Google Chat (Workspace Webhooks)
- **Objetivo:** Permitir interação em equipe durante a execução dos agentes autônomos.
- **Escopo:**
  - Integração via Webhooks do Google Chat para envio de mensagens com Cards estruturados.
  - Notificações de planos pendentes de aprovação e dúvidas que exigem resposta humana.

### 3.3. Sincronização com Google Secret Manager (`amb secret`)
- **Objetivo:** Aumentar a segurança no gerenciamento de chaves e segredos em monorepos.
- **Escopo:**
  - Comando `amb secret pull` para sincronizar segredos remotos com o `.env` local.
  - Comando `amb secret push` para atualizar chaves na nuvem de forma centralizada.

### 3.4. Exportação de Métricas para Google Sheets
- **Objetivo:** Gerar relatórios e dashboards executivos de produtividade da esteira de automação.
- **Escopo:**
  - Exportação periódica dos dados de `.amb/telemetry.jsonl` para uma planilha do Google Sheets.
  - Compatibilidade com dashboards do Google Looker Studio.

### 3.5. Pipeline Visual Stitch ➔ Gemini Multimodal ➔ Jules
- **Objetivo:** Automatizar a validação de design antes da geração de código.
- **Escopo:**
  - Envio de screenshots gerados pelo Stitch diretamente para a API Gemini multimodal.
  - Auditoria de contraste, tipografia e layout com geração de feedback visual antes de despachar a tarefa para a Cloud VM do Jules.
