# US-22: Implementação do Endpoint get_activity no JulesClient

## 📌 Contexto e Objetivo
A documentação da API REST do Google Jules (`https://jules.google/docs/api/reference/activities`) documenta o endpoint canônico de consulta individual de atividades:
`GET /v1alpha/sessions/{sessionId}/activities/{activityId}`

No ecossistema AMB_V2, o `JulesClient` possui o método `list_activities`, mas não disponibiliza o método direto `get_activity` para inspecionar uma única atividade específica por ID. Ter esse método garante 100% de paridade com a API REST oficial do Jules e permite que ferramentas e sentinelas inspecionem eventos pontuais sem precisar baixar o histórico completo da sessão.

---

## 📐 Requisitos Técnicos

### 1. Método `get_activity` no `JulesClient`
- **Arquivo (`amb_cli/integrations/jules/jules_client.py`):**
  - Implementar o método:
    ```python
    def get_activity(self, session_id: str, activity_id: str) -> Dict[str, Any]:
        """Obtém detalhes de uma atividade específica de uma sessão."""
    ```
  - Normalizar `session_id` com `self.normalize_session_id(session_id)`.
  - Normalizar `activity_id`: se vier com caminho hierárquico (ex: `sessions/.../activities/act1` ou `activities/act1`), extrair apenas o ID da atividade.
  - Executar a requisição `GET` para `sessions/{clean_id}/activities/{clean_act_id}`.
  - Manter o limite rígido de 300 linhas por arquivo (Regra 02).

---

## 🧪 Critérios de Aceite
1. **Suíte de Testes Unitários:**
   - Criar `tests/test_jules_get_activity.py` cobrindo:
     - Chamada bem-sucedida a `get_activity` com IDs simples (`"123"`, `"act1"`).
     - Tratamento e normalização quando `activity_id` vem com caminho completo (`"sessions/123/activities/act1"`).
     - Propagação correta de erros (ex: HTTP 404 quando a atividade não existe).
2. **Qualidade de Código e Limites Arquiteturais:**
   - 100% dos testes unitários passando (`pytest -q`).
   - Teto rígido de 300 linhas por arquivo (Regra 02).
   - Tipagem estrita com `typing` (Regra 04).
