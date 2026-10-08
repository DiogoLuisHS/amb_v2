# 🎯 US-07: Camada de Apresentação Centralizada e Sandbox de QA (ConsolePresenter e LocalQASandbox)

## 👤 User Story
> **Como** engenheiro operando o AMB_V2 em pipelines ou scripts automatizados,  
> **Quero** um `ConsolePresenter` universal para suporte padronizado a `--json` e `--quiet` e um `LocalQASandbox` com salvamento de logs em `.amb/logs/qa/` e sanitização de stacktraces,  
> **Para que** comandos de terminal possam ser consumidos programaticamente e erros de QA forneçam diagnósticos cirúrgicos aos agentes sem estourar limites de contexto.

---

## 📌 Critérios de Aceitação BDD

* **Cenário 1: Apresentação Padronizada e Suporte a Flags Globais**
  * **Dado** a classe `ConsolePresenter` em `amb_cli/core/console_presenter.py`;
  * **Quando** instanciada em modo `json_mode=True`;
  * **Então** chamadas a `present_data(data)` devem emitir exclusivamente JSON válido no stdout;
  * **E** em modo `quiet_mode=True`, logs verbosos devem ser silenciados, retornando apenas status ou código numérico.

* **Cenário 2: Gravação Isolada de Logs de QA**
  * **Dado** a execução de um comando de QA pelo `QualityGatekeeper`;
  * **Quando** o teste ou build for concluído;
  * **Então** o output completo deve ser gravado em `.amb/logs/qa/qa_<timestamp>.log`;
  * **E** a pasta `.amb/logs/qa/` deve ser criada automaticamente se não existir.

* **Cenário 3: Sanitização de Stacktraces em Caso de Falha**
  * **Dado** um comando de QA que falhou com centenas de linhas de logs;
  * **Quando** `LocalQASandbox.extract_sanitized_failure(log_text)` for chamado;
  * **Então** deve filtrar o ruído e retornar as 25-30 linhas mais essenciais do erro/stacktrace (linhas com "Error", "FAIL", "Traceback", etc.), otimizadas para envio a agentes cognitivos.

---

## 🛠️ Arquivos Alvo & Alterações Necessárias

### 1. `amb_cli/core/console_presenter.py` (Novo)
Implementar `ConsolePresenter`:
- Métodos: `print_message()`, `print_table()`, `print_json()`, `print_error()`.
- Respeito às variáveis de ambiente ou flags de `--json` e `--quiet`.

### 2. `amb_cli/pipeline/pipeline_core/qa_sandbox.py` (Novo)
Implementar `LocalQASandbox`:
- `save_run_log(command: str, output: str, success: bool) -> str` (retorna caminho do arquivo salvo).
- `extract_sanitized_failure(output: str, max_lines: int = 30) -> str`.

### 3. `amb_cli/pipeline/quality_gatekeeper.py`
Integrar com `LocalQASandbox` para persistir o histórico de QA e sanitizar o log retornado em falhas.

### 4. `tests/test_console_presenter_and_sandbox.py` (Novo)
Testes unitários cobrindo:
- Formatação de saída do `ConsolePresenter` em modo normal, json e quiet.
- Gravação correta em disco de `.amb/logs/qa/`.
- Extração de falhas com logs simulados de pytest, npm e cargo.

---

## 🔍 Comandos de Verificação Local
```bash
# Validar testes unitários do presenter e sandbox
pytest tests/test_console_presenter_and_sandbox.py -v

# Validar suíte completa
pytest -q
```

---

## 📋 Definition of Done (DoD)
- [ ] `ConsolePresenter` e `LocalQASandbox` implementados e testados.
- [ ] `QualityGatekeeper` persistindo logs em `.amb/logs/qa/`.
- [ ] Suíte de testes unitários dedicada 100% verde.
- [ ] Arquivos novos com menos de 200 linhas cada.
