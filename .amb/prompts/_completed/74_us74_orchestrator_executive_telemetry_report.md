# US-74: Telemetria Executiva e Quadro de Produtividade ao Fim da Orquestração

## 📌 Contexto e Objetivo
Ao concluir o processamento de um lote de prompts (`amb agent -p <pasta>`) ou uma execução completa de pipeline (`amb pipeline`), o terminal apenas exibe a mensagem final da última tarefa e encerra.
Falta um encerramento executivo que sintetize o valor entregue pela rodada: quantas telas foram geradas no Stitch, quantas sessões foram completadas na cloud do Jules, quantos Pull Requests foram abertos/mesclados, tempo total gasto e integridade de QA.

Esta US integra a conclusão de qualquer orquestração com a telemetria local e a apresentação visual:
1. Registra os metadados consolidados da rodada no [`LocalTelemetry`](file:///c:/Users/DiogoHungaro/Desktop/Script/amb_v2/amb_cli/core/local_telemetry.py) (`.amb/telemetry.jsonl`).
2. Renderiza no terminal um quadro executivo de produtividade formatado pelo [`ConsolePresenter`](file:///c:/Users/DiogoHungaro/Desktop/Script/amb_v2/amb_cli/core/console_presenter.py):
```
===========================================================================
🏆 RESUMO EXECUTIVO DE ORQUESTRAÇÃO AMB_V2
===========================================================================
  • Tarefas Executadas:    5 prompts processados
  • Telas Stitch Geradas:  2 interfaces visuais
  • Sessões Jules Cloud:   5 sessões completadas com sucesso
  • Pull Requests:         5 PRs abertos | 5 PRs integrados via Auto-Merge
  • Validação de QA Local: 100% verde (Passou em typecheck, build e tests)
  • Tempo Total de Rodada: 14m 32s
===========================================================================
```

---

## 📐 Requisitos Técnicos

### 1. Atualização do Autonomous Loop e Pipeline
- **Arquivo (`amb_cli/agents/autonomous_loop.py`):**
  - No encerramento de `run_autonomous_loop`:
    - Coletar métricas da rodada (itens processados, sessões geradas, PRs integrados, tempo de início/fim).
    - Registrar na telemetria: `LocalTelemetry.record_session(...)`.
    - Apresentar tabela executiva consolidada.
- **Arquivo (`amb_cli/pipeline/pipeline.py`):**
  - No encerramento com sucesso do `PipelineOrchestrator.run`:
    - Registrar execução e emitir quadro consolidado de resumo da tarefa.
  - Manter o limite rígido de 300 linhas por arquivo (Regra 02).

---

## 🧪 Critérios de Aceite
1. **Suíte de Testes Unitários:**
   - Criar `tests/test_orchestrator_telemetry_report.py` cobrindo:
     - Registro correto das métricas da rodada em `LocalTelemetry` ao término do lote.
     - Renderização do quadro executivo formatado no terminal ao concluir a orquestração.
     - Suporte a saída estruturada em JSON caso `--json` seja fornecido na CLI.
2. **Qualidade de Código:**
   - 100% dos testes passando (`pytest -q`).
   - Teto rígido de 300 linhas por arquivo (Regra 02).
   - Tipagem estrita com `typing` (Regra 04).
