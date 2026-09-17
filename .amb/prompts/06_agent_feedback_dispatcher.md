# 🎯 Tarefa Jules: Auditoria e Alinhamento de `amb_cli/agents/auto_reply_core/feedback_dispatcher.py`

## 📌 Arquivo Alvo
- **Caminho:** `amb_cli/agents/auto_reply_core/feedback_dispatcher.py`
- **Responsabilidade Única (SRP - Regra 01):** Coordenação do despacho de mensagens e aprovações de plano para a API REST do Google Jules, gestão do catálogo de sessões pendentes e condução de fluxos de auto-resposta (interativo e em lote).

---

## 📐 Regras Arquiteturais Obrigatórias (`.agents/rules/`)
1. **Regra 01 (SRP):** Manter a separação entre despacho/interação com o Jules e a inteligência cognitiva (delegada ao `CognitiveAdvisor`) e o parsing de turnos (delegado ao `TurnHistoryExtractor`).
2. **Regra 02 (Atomização):** Manter o arquivo coeso (em torno de 250 a 300 linhas).
3. **Regra 03 (DRY & Imports Canônicos):**
   - Importações absolutas de core: `from integrations.jules.jules_client import JulesClient`, `from .turn_extractor import TurnHistoryExtractor`, `from .cognitive_advisor import CognitiveAdvisor`.
4. **Regra 04 (Qualidade e Tipagem):**
   - Assinaturas tipadas: `send_reply(session_id: str, message: str) -> None`, `approve_plan(session_id: str) -> None`, `get_pending_sessions() -> List[Dict[str, Any]]`, `advise_and_reply(...) -> Optional[str]`.
5. **Regra 05 (Documentação Concisa):** Docstrings declarativas e limpas.
6. **Regra 06 (Segurança e Testes):** Testes unitários 100% verdes.

---

## 🛠️ Itens Específicos a Verificar / Refatorar
1. **Reconhecimento Abrangente de Estados de Espera:**
   - Em `get_pending_sessions`, verificar estados canônicos do Jules:
     `AWAITING_USER_FEEDBACK`, `AWAITING_USER_ACTION`, `AWAITING_INPUT`, `AWAITING_PLAN_APPROVAL` e correspondência genérica `"AWAITING" in state.upper()`.
2. **Proteção Anti-Looping e Anti-Duplicação:**
   - Garantir que a verificação `not turn_info.get("is_awaiting_user_action", True)` impeça o envio de mensagens redundantes quando o último turno já foi do usuário.
3. **Apoio a Modo Automático e Interativo:**
   - Suporte completo às flags `auto_approve: bool = False` e `force: bool = False` no fluxo `advise_and_reply`.

---

## 🧪 Validação Obrigatória
Antes de abrir o Pull Request:
```bash
python -m py_compile amb_cli/agents/auto_reply_core/feedback_dispatcher.py
python -m pytest tests/test_auto_reply_srp.py
python -m pytest
```
Todos os 92 testes unitários devem passar (100% green).

---

## 🚀 Ação Final Obrigatória: Abertura do Pull Request
Ao concluir todas as alterações e validar os testes com sucesso (100% green):
1. Você DEVE submeter/abrir o Pull Request no GitHub imediatamente.
2. Não encerre a sessão apenas no estado "Ready for submission"; confirme a criação do PR diretamente no GitHub com título e descrição claros das alterações.
