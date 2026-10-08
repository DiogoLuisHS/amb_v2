# US-09: Captura de Métricas do Resumo na Telemetria Local (LocalTelemetry)

## 📌 Contexto e Objetivo
Permitir que o `SessionMonitor` e o `SessionState` extraiam automaticamente as métricas reportadas no encerramento da sessão do Google Jules (`files_changed`, `runtime`, `lines_added`, `lines_removed`) e as registrem no arquivo `.amb/telemetry.jsonl` para exibição detalhada no comando `amb stats`.

## 📐 Requisitos Técnicos
1. **Extração de Métricas (`SessionState`):**
   - Método estático `SessionState.extract_metrics(session_dict, duration_seconds=...)` para deduzir `files_changed`, `lines_added`, `lines_removed`, `runtime` e `pr_url`.
2. **Registro Centralizado (`LocalTelemetry`):**
   - Método de classe `LocalTelemetry.record_session_metrics(...)` gravando evento `SESSION_COMPLETED`.
   - Agregação em `LocalTelemetry.get_summary_metrics()` somando total de arquivos e linhas alteradas.
3. **Disparo no Monitoramento (`SessionMonitor`):**
   - Ao atingir estado terminal em `poll_until_terminal()`, invoca `SessionState.extract_metrics` e persiste na telemetria.
4. **Exibição na CLI (`amb stats`):**
   - Exibir linhas adicionadas/removidas e total de arquivos modificados na tabela de estatísticas.
