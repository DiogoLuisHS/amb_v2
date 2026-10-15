# US-72: Persistência de Estado do Pipeline via LoopStateMachine

## 📌 Contexto e Objetivo
O AMB_V2 possui uma máquina de estados finita robusta com persistência em disco ([`LoopStateMachine`](file:///c:/Users/DiogoHungaro/Desktop/Script/amb_v2/amb_cli/agents/loop_core/loop_state_machine.py)), que grava o estado em `.amb/loop_state.json`.
No entanto, essa máquina era utilizada exclusivamente pelo `autonomous_loop.py`. O pipeline Design-to-Deploy ([`pipeline.py`](file:///c:/Users/DiogoHungaro/Desktop/Script/amb_v2/amb_cli/pipeline/pipeline.py)), que passa por 6 etapas demoradas (Design no Stitch, Síntese, Despacho no Jules, Monitoramento, QA e Merge), **não persistia seu progresso**.
Se o pipeline fosse interrompido por queda de conexão ou `Ctrl+C`, o desenvolvedor perdia o rastreio da sessão ativa e o comando `amb loop status` não tinha conhecimento da execução.

Esta US integra o `PipelineOrchestrator` à `LoopStateMachine`:
1. Cada transição de etapa do pipeline atualiza atomicamente o arquivo `.amb/loop_state.json`:
   - Etapa 2: `DESIGN_GENERATING` (Stitch)
   - Etapa 4: `PROMPT_SYNTHESIZING`
   - Etapa 5: `SESSION_ACTIVE` (gravando o `session_id` do Jules)
   - Etapa 6: `QA_VALIDATING`
   - Conclusão: `CYCLE_COMPLETED`
2. Permite que `amb loop status` exiba o status em tempo real do pipeline.
3. Permite que `amb loop resume` ou `amb pipeline --resume` retome a execução do ponto exato onde foi interrompida sem recriar telas nem sessões.

---

## 📐 Requisitos Técnicos

### 1. Integração no PipelineOrchestrator
- **Arquivo (`amb_cli/pipeline/pipeline.py`):**
  - Instanciar `machine = LoopStateMachine(repo_root=repo_root)`.
  - Atualizar o estado nas etapas correspondentes:
    - Ao iniciar a sessão Jules: `machine.set_active_session(session_id=session_id, item_name=file_label)`.
    - Ao iniciar QA: atualizar estado com metadados da sessão.
    - Ao concluir com sucesso: `machine.transition_to(LoopState.CYCLE_COMPLETED)`.
  - Suportar flag `--resume` sem argumentos no pipeline:
    - Se invocado `amb pipeline --resume`, recupera a sessão ativa direto de `machine.get_current_state()["session_id"]`.
  - Manter o limite rígido de 300 linhas por arquivo (Regra 02).

---

## 🧪 Critérios de Aceite
1. **Suíte de Testes Unitários:**
   - Criar `tests/test_pipeline_state_machine.py` cobrindo:
     - Gravação e transição de estados em `.amb/loop_state.json` durante as etapas do pipeline.
     - Registro do `session_id` da sessão Jules no estado persistido.
     - Retomada do monitoramento via `amb pipeline --resume` recuperando o ID salvo no arquivo de estado.
2. **Qualidade de Código:**
   - 100% dos testes passando (`pytest -q`).
   - Teto rígido de 300 linhas por arquivo (Regra 02).
   - Tipagem estrita com `typing` (Regra 04).
