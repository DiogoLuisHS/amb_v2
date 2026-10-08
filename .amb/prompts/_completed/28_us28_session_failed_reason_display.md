# US-28: Diagnóstico Estruturado de Falha com sessionFailed.reason

## 📌 Contexto e Objetivo
A documentação de tipos da API REST do Google Jules (`https://jules.google/docs/api/reference/types`) define que a atividade de falha de uma sessão traz a estrutura `sessionFailed` com o motivo explícito:
```json
{
  "name": "sessions/12345/activities/67890",
  "originator": "system",
  "sessionFailed": {
    "reason": "Execution timed out after 30 minutes while running test suite"
  }
}
```

No AMB_V2, quando uma sessão falha na nuvem, o [`SessionMonitor`](file:///c:/Users/DiogoHungaro/Desktop/Script/amb_v2/amb_cli/integrations/jules/session_monitor.py) e o comando `amb jules get <session_id>` reportam apenas o estado genérico `FAILED`, sem exibir ao desenvolvedor a razão fornecida pelo motor do Jules. Isso força o usuário a abrir o navegador web para descobrir o motivo real da falha (ex: timeout de VM, falha em dependência, branch incompatível).

Esta US enriquece a extração de falhas e exibe a justificativa canônica (`reason`) diretamente no terminal no `SessionMonitor` e no `run_get_session`.

---

## 📐 Requisitos Técnicos

### 1. Método Utilitário `extract_failure_reason`
- **Arquivo (`amb_cli/integrations/jules/jules_core/session_extractor.py`):**
  - Adicionar o método estático:
    ```python
    @staticmethod
    def extract_failure_reason(activities: Optional[List[Dict[str, Any]]]) -> Optional[str]:
        """Extrai o motivo de falha (reason) a partir dos eventos sessionFailed das atividades."""
    ```
  - Percorrer as atividades recebidas (em ordem reversa ou buscando a mais recente).
  - Verificar se a atividade contém `act.get("sessionFailed", {}).get("reason")`.
  - Retornar a string do motivo limpa com `.strip()` ou `None` se ausente.
  - Manter o limite rígido de 300 linhas por arquivo (Regra 02).

### 2. Integração no `SessionMonitor`
- **Arquivo (`amb_cli/integrations/jules/session_monitor.py`):**
  - Quando a sessão transicionar ou for detectada no estado `SessionState.FAILED`:
    - Consultar as atividades recentes via `client.list_activities(session_id)`.
    - Invocar `failure_reason = SessionExtractor.extract_failure_reason(activities)`.
    - Se presente, incluir no log de falha emitido pelo monitor:
      `❌ Sessão {session_id} falhou. Motivo: "{failure_reason}"`

### 3. Integração na Exibição do `amb jules get`
- **Arquivo (`amb_cli/integrations/jules/tools/get_session.py`):**
  - No método `run_get_session`, se o estado da sessão for `FAILED`:
    - Consultar as atividades da sessão (caso não tenham sido passadas) ou utilizar as atividades listadas.
    - Chamar `failure_reason = SessionExtractor.extract_failure_reason(activities)`.
    - Se encontrado, exibir no bloco de detalhes:
      `  • Motivo da Falha: {Colors.RED}{failure_reason}{Colors.RESET}`

---

## 🧪 Critérios de Aceite
1. **Suíte de Testes Unitários:**
   - Criar `tests/test_session_failure_reason.py` cobrindo:
     - `extract_failure_reason` com atividade contendo `sessionFailed.reason` válida.
     - `extract_failure_reason` quando não há evento de falha (retornando `None`).
     - Integração em `run_get_session` exibindo a mensagem em vermelho quando a sessão é `FAILED`.
     - Resiliência contra payloads malformados ou atividades vazias.
2. **Qualidade de Código e Limites Arquiteturais:**
   - 100% dos testes unitários passando (`pytest -q`).
   - Teto rígido de 300 linhas por arquivo (Regra 02).
   - Tipagem estrita com `typing` (Regra 04).
