# US-21: Exibição de Timestamps de Criação e Atualização em amb jules get

## 📌 Contexto e Objetivo
A documentação da API REST do Google Jules (`https://jules.google/docs/api/reference/sessions`) documenta que todo objeto `Session` retornado pelos endpoints `GET /v1alpha/sessions/{id}` e `POST /v1alpha/sessions` contém os campos temporais:
- `createTime`: Timestamp ISO 8601 do momento em que a sessão foi enfileirada.
- `updateTime`: Timestamp ISO 8601 da última alteração de estado ou atividade da sessão.

No AMB_V2, a ferramenta `amb jules get <id>` (em `amb_cli/integrations/jules/tools/get_session.py`) exibe ID, título, estado, PR e repositório, mas omite as informações temporais. Para auditoria e acompanhamento de tarefas em execução ou históricas, é fundamental que o desenvolvedor saiba com precisão quando a tarefa foi criada e quando ocorreu sua última atividade na nuvem.

---

## 📐 Requisitos Técnicos

### 1. Formatação e Exibição em `get_session.py`
- **Arquivo (`amb_cli/integrations/jules/tools/get_session.py`):**
  - No método `run_get_session`:
    - Extrair `create_time = data.get("createTime")` e `update_time = data.get("updateTime")`.
    - Se presentes, exibir de forma limpa e destacada antes do link para o painel web:
      `  • Criada em:     <create_time>`
      `  • Atualizada em: <update_time>`
    - Manter a saída em JSON intacta quando `as_json=True`.
    - Manter o limite rígido de 300 linhas por arquivo (Regra 02).

---

## 🧪 Critérios de Aceite
1. **Suíte de Testes Unitários:**
   - Criar `tests/test_session_timestamps_display.py` cobrindo:
     - Formatação e exibição de `createTime` e `updateTime` no output textual de `run_get_session`.
     - Execução graciosa quando os campos não estiverem presentes no payload da sessão.
2. **Qualidade de Código e Limites Arquiteturais:**
   - 100% dos testes unitários passando (`pytest -q`).
   - Teto rígido de 300 linhas por arquivo (Regra 02).
   - Tipagem estrita com `typing` (Regra 04).
