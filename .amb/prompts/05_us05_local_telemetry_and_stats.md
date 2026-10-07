# 🎯 US-05: Telemetria Local Estruturada e Métricas de Produtividade (LocalTelemetry e amb stats)

## 👤 User Story
> **Como** desenvolvedor utilizando o AMB_V2,  
> **Quero** um registrador de telemetria local append-only (`.amb/telemetry.jsonl`) e um comando `amb stats`,  
> **Para que** eu possa acompanhar métricas históricas de tempo de execução, taxa de sucesso de QA, total de PRs integrados e eficiência dos ciclos autônomos sem enviar dados para a internet.

---

## 📌 Critérios de Aceitação BDD

* **Cenário 1: Registro Estruturado Append-Only**
  * **Dado** a classe `LocalTelemetry` em `amb_cli/core/local_telemetry.py`;
  * **Quando** `record_event(event_type: str, data: dict)` for invocado (ex: `SESSION_COMPLETED`, `QA_RUN`, `PR_MERGED`);
  * **Então** uma nova linha no formato JSON deve ser adicionada a `.amb/telemetry.jsonl` com `timestamp`, `event_type` e `data`;
  * **E** o arquivo `.amb/telemetry.jsonl` deve ser criado automaticamente se não existir.

* **Cenário 2: Cálculo Consolidado de Métricas**
  * **Dado** que há eventos registrados em `.amb/telemetry.jsonl`;
  * **Quando** `get_summary_metrics()` for chamado;
  * **Então** deve computar:
    - Total de sessões executadas
    - Taxa de sucesso de QA pós-merge (%)
    - Total de PRs integrados com sucesso
    - Duração média por ciclo de desenvolvimento.

* **Cenário 3: Exibição no Terminal (amb stats)**
  * **Dado** o comando `amb stats`;
  * **Quando** executado;
  * **Então** deve exibir uma tabela formatada no terminal com as métricas consolidadas;
  * **E** deve suportar a flag `--json` retornando o resumo em formato JSON puro.

---

## 🛠️ Arquivos Alvo & Alterações Necessárias

### 1. `amb_cli/core/local_telemetry.py` (Novo)
Implementar `LocalTelemetry`:
- Gravação thread-safe append-only em `.amb/telemetry.jsonl`.
- Leitura e agregações com tratamento de linhas malformadas sem quebrar.
- Métodos: `record_session(...)`, `record_qa(...)`, `record_merge(...)`, `get_metrics() -> dict`.

### 2. `amb_cli/cli_modules/handlers_core/stats_handler.py` (Novo)
Handler para formatar e exibir as métricas de `amb stats` com cores e tabelas limpas.

### 3. `amb_cli/cli_modules/cli_parsers.py` e `amb_cli/cli_modules/cli_dispatch.py`
Registrar comando `amb stats` com opção `--json`.

### 4. `tests/test_local_telemetry.py` (Novo)
Testes unitários cobrindo:
- Gravação de eventos no arquivo JSONL.
- Agregação correta de métricas com dados simulados.
- Resiliência contra arquivos inexistentes ou vazios.

---

## 🔍 Comandos de Verificação Local
```bash
# Validar testes unitários de telemetria
pytest tests/test_local_telemetry.py -v

# Validar suíte completa
pytest -q

# Testar comando de stats
python -m amb_cli.cli stats
python -m amb_cli.cli stats --json
```

---

## 📋 Definition of Done (DoD)
- [ ] `LocalTelemetry` implementado e gravando em `.amb/telemetry.jsonl`.
- [ ] Comando `amb stats` funcional com suporte a `--json`.
- [ ] Testes unitários dedicados em `tests/test_local_telemetry.py` 100% passando.
- [ ] Arquivos novos com menos de 200 linhas cada.
