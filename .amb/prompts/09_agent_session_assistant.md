# 🎯 Tarefa Jules: Auditoria e Alinhamento de `amb_cli/agents/loop_core/session_assistant.py`

## 📌 Arquivo Alvo
- **Caminho:** `amb_cli/agents/loop_core/session_assistant.py`
- **Responsabilidade Única (SRP - Regra 01):** Monitorar ativamente o ciclo de vida de uma sessão no Google Jules, aprovando planos pendentes e despachando respostas cognitivas via Auto-Reply quando o agente demandar feedback.

---

## 📐 Regras Arquiteturais Obrigatórias (`.agents/rules/`)
1. **Regra 01 (SRP):** Foco exclusivo no monitoramento da sessão e no desbloqueio autônomo do agente Jules até o encerramento (`COMPLETED` / `FAILED`).
2. **Regra 02 (Atomização):** Manter o arquivo atômico (entre 100 e 150 linhas, teto máximo 300).
3. **Regra 03 (DRY & Imports Canônicos):**
   - Imports absolutos:
     ```python
     from integrations.jules.jules_client import JulesClient
     from agents.auto_reply import advise_and_reply, get_last_conversation_turn
     ```
4. **Regra 04 (Qualidade e Tipagem):**
   - Assinatura: `monitor_and_assist_session(client: JulesClient, session_id: str, auto_reply_ai: bool = True) -> str`
5. **Regra 05 (Documentação Concisa):** Docstrings concisas e sem ruídos decorativos.
6. **Regra 06 (Segurança e Testes):** Testes unitários 100% verdes.

---

## 🛠️ Itens Críticos de Implementação
1. **Reconhecimento de Todos os Estados de Feedback:**
   - Detectar `AWAITING_USER_FEEDBACK`, `AWAITING_USER_ACTION`, `AWAITING_INPUT`, `AWAITING_PLAN_APPROVAL` ou qualquer estado com `"AWAITING" in state.upper()`.
2. **Diferenciação Estrita entre Plano e Chat:**
   - Se `turn_info.get("has_unapproved_plan") and turn_info.get("last_speaker") == "PLAN"`: invocar `client.approve_plan(session_id)`.
   - Se `auto_reply_ai and turn_info.get("last_speaker") == "AGENT"`: invocar `advise_and_reply(session_id=session_id, auto_approve=True, force=True)`.
3. **Prevenção de Respostas Repetidas:**
   - Rastrear `last_answered_agent_msg_id` para nunca responder a mesma mensagem do agente duas vezes.
4. **Delay de Conclusão para Registro de PR:**
   - Quando `state in ["COMPLETED", "SUCCEEDED"]`, aguardar 10s antes de retornar para garantir que o Jules registre o Pull Request no campo `outputs`.

---

## 🧪 Validação Obrigatória
Antes de abrir o Pull Request:
```bash
python -m py_compile amb_cli/agents/loop_core/session_assistant.py
python -m pytest
```
Todos os 92 testes unitários devem passar (100% green).
