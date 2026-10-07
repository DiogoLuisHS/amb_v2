# 🎯 US-02: Máquina de Estados Finita e Persistência do Loop (LoopStateMachine)

## 👤 User Story
> **Como** operador de agentes autônomos no AMB_V2,  
> **Quero** uma máquina de estados finita persistida em `.amb/loop_state.json` com comandos de controle (`amb loop status`, `amb loop pause`, `amb loop resume`),  
> **Para que** interrupções de terminal ou falhas de rede permitam retomar exatamente do ponto onde o ciclo parou sem perder o progresso do desenvolvimento.

---

## 📌 Critérios de Aceitação BDD

* **Cenário 1: Transição e Persistência de Estados**
  * **Dado** a classe `LoopStateMachine` em `amb_cli/agents/loop_core/loop_state_machine.py`;
  * **Quando** uma transição for registrada (ex: `transition_to(LoopState.DISPATCHING_JULES, details={...})`);
  * **Então** o arquivo `.amb/loop_state.json` deve ser gravado atomicamente com: `state`, `current_cycle`, `total_cycles`, `active_item`, `session_id`, `updated_at`;
  * **E** o estado persistido deve ser recuperável via `load_state()`.

* **Cenário 2: Estados do Loop Suportados**
  * **Dado** o enum `LoopState`;
  * **Quando** consultado;
  * **Então** deve incluir: `IDLE`, `SELECTING_PERSONA`, `DISPATCHING_JULES`, `MONITORING_SESSION`, `RUNNING_LOCAL_QA`, `MERGING_PR`, `CYCLE_COMPLETED`, `PAUSED`, `FAILED`.

* **Cenário 3: Comandos CLI de Controle (amb loop)**
  * **Dado** o comando `amb loop status`;
  * **Quando** executado;
  * **Então** deve exibir o status do ciclo atual, persona/prompt em processamento e sessão do Jules associada;
  * **E** os comandos `amb loop pause` e `amb loop resume` devem alterar o estado em `.amb/loop_state.json` para controlar a execução em tempo de execução.

---

## 🛠️ Arquivos Alvo & Alterações Necessárias

### 1. `amb_cli/agents/loop_core/loop_state_machine.py` (Novo)
Implementar `LoopStateMachine`:
- Enum `LoopState`
- Gravação atômica em `.amb/loop_state.json` (usando arquivo temporário `.tmp` e substituição atômica `os.replace`)
- Métodos: `get_current_state()`, `transition_to(state, **kwargs)`, `pause()`, `resume()`, `reset()`
- Garantir que não levanta exceções não tratadas em caso de arquivo JSON corrompido (recuperação graciosa).

### 2. `amb_cli/cli_modules/handlers_core/loop_handler.py` (Novo)
Handler CLI para tratar `amb loop status`, `amb loop pause`, `amb loop resume`.

### 3. `amb_cli/cli_modules/cli_parsers.py` e `amb_cli/cli_modules/cli_dispatch.py`
Registrar o parser `amb loop` com as opções `status`, `pause`, `resume` e rotear para `loop_handler.py`.

### 4. `tests/test_loop_state_machine.py` (Novo)
Testes unitários cobrindo ciclo de vida completo, transições válidas/inválidas, persistência e recuperação do JSON.

---

## 🔍 Comandos de Verificação Local
```bash
# Validar testes unitários da máquina de estados
pytest tests/test_loop_state_machine.py -v

# Validar suíte completa
pytest -q

# Testar comandos CLI de loop
python -m amb_cli.cli loop status
```

---

## 📋 Definition of Done (DoD)
- [ ] `loop_state_machine.py` implementado com persistência atômica e recuperação graciosa.
- [ ] Subcomando `amb loop status|pause|resume` operacional na CLI.
- [ ] Testes unitários dedicados em `tests/test_loop_state_machine.py` 100% passando.
- [ ] Todos os arquivos abaixo de 250 linhas e conformes com a Regra 02.
