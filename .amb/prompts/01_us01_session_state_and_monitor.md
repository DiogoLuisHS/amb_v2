# 🎯 US-01: Unificação de Estados e Polling com SessionState e SessionMonitor

## 👤 User Story
> **Como** desenvolvedor do ecossistema AMB_V2,  
> **Quero** um enum canônico `SessionState` e um monitor reutilizável `SessionMonitor`,  
> **Para que** todas as rotinas de vigília (watcher, loop autônomo, pipeline) compartilhem a mesma lógica de polling sem duplicar checagens de strings literais.

---

## 📌 Critérios de Aceitação BDD

* **Cenário 1: Enum Canônico de Estados**
  * **Dado** o módulo `amb_cli/integrations/jules/jules_core/session_state.py`;
  * **Quando** for importado;
  * **Então** deve exportar o enum `SessionState` com os valores: `IDLE`, `IN_PROGRESS`, `AWAITING_INPUT`, `AWAITING_PLAN_APPROVAL`, `COMPLETED`, `FAILED`;
  * **E** deve expor os métodos auxiliares:
    - `is_terminal() -> bool` (retorna True para COMPLETED e FAILED)
    - `is_awaiting_feedback() -> bool` (retorna True para AWAITING_INPUT e AWAITING_PLAN_APPROVAL)
    - `is_success() -> bool` (retorna True para COMPLETED)
    - `from_api_string(raw: str) -> SessionState` (mapeia strings da API como "SUCCEEDED", "CLOSED" para COMPLETED; "ERROR", "ABORTED" para FAILED).

* **Cenário 2: Polling Unificado no SessionMonitor**
  * **Dado** a classe `SessionMonitor` em `amb_cli/integrations/jules/jules_core/session_monitor.py`;
  * **Quando** instanciada com um cliente `JulesClient` e um `session_id`;
  * **Então** o método `poll_until_terminal(interval_seconds=8, max_wait_seconds=1800, on_state_change=None)` deve vigiar a sessão;
  * **E** deve disparar `on_state_change(state, session_data)` a cada transição de estado;
  * **E** deve retornar `(SessionState, dict)` com o estado final e dados completos da sessão ao atingir estado terminal ou timeout.

* **Cenário 3: Refatoração Limpa do Jules Watcher**
  * **Dado** o arquivo `amb_cli/integrations/jules/jules_watcher.py`;
  * **Quando** for refatorado;
  * **Então** deve delegar a detecção de estados para `SessionState` e `SessionMonitor`, mantendo compatibilidade total com comandos existentes da CLI (`amb jules get <id> --watch`).

---

## 🛠️ Arquivos Alvo & Alterações Necessárias

### 1. `amb_cli/integrations/jules/jules_core/session_state.py` (Novo)
Implementar:
```python
from enum import Enum

class SessionState(str, Enum):
    IDLE = "IDLE"
    IN_PROGRESS = "IN_PROGRESS"
    AWAITING_INPUT = "AWAITING_INPUT"
    AWAITING_PLAN_APPROVAL = "AWAITING_PLAN_APPROVAL"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"

    def is_terminal(self) -> bool:
        return self in (SessionState.COMPLETED, SessionState.FAILED)

    def is_awaiting_feedback(self) -> bool:
        return self in (SessionState.AWAITING_INPUT, SessionState.AWAITING_PLAN_APPROVAL)

    def is_success(self) -> bool:
        return self == SessionState.COMPLETED

    @classmethod
    def from_api_string(cls, raw: str) -> "SessionState":
        normalized = (raw or "").upper().strip()
        if normalized in ("COMPLETED", "SUCCEEDED", "CLOSED"):
            return cls.COMPLETED
        if normalized in ("FAILED", "ERROR", "ABORTED", "CANCELLED"):
            return cls.FAILED
        if normalized in ("AWAITING_INPUT", "AWAITING_USER_INPUT"):
            return cls.AWAITING_INPUT
        if normalized in ("AWAITING_PLAN_APPROVAL", "PLAN_PENDING"):
            return cls.AWAITING_PLAN_APPROVAL
        if normalized in ("IN_PROGRESS", "RUNNING", "PLANNING", "EXECUTING"):
            return cls.IN_PROGRESS
        return cls.IDLE
```

### 2. `amb_cli/integrations/jules/jules_core/session_monitor.py` (Novo)
Implementar `SessionMonitor` utilizando `time.sleep`, checando timeout e invocando callbacks de forma segura com captura de exceções transitórias. Manter o arquivo com menos de 180 linhas.

### 3. `tests/test_session_monitor.py` (Novo)
Testes unitários isolados com mocks do `JulesClient` cobrindo transições de estados, detecção de estado terminal, timeouts e callbacks.

---

## 🔍 Comandos de Verificação Local
```bash
# Validar testes unitários do SessionMonitor
pytest tests/test_session_monitor.py -v

# Validar suíte completa
pytest -q

# Validar conformidade de tamanho e regras
python -m amb_cli.cli validate amb_cli/integrations/jules/jules_core/session_state.py
python -m amb_cli.cli validate amb_cli/integrations/jules/jules_core/session_monitor.py
```

---

## 📋 Definition of Done (DoD)
- [ ] Módulos `session_state.py` e `session_monitor.py` criados em `amb_cli/integrations/jules/jules_core/`.
- [ ] Testes unitários dedicados em `tests/test_session_monitor.py` 100% passando.
- [ ] Suíte completa do pytest 100% verde sem quebras retroativas.
- [ ] Arquivos com menos de 200 linhas cada, com tipagem estrita e sem acoplamento circular.
