# 🎯 Tarefa Jules: Auditoria e Alinhamento de `amb_cli/agents/auto_reply.py`

## 📌 Arquivo Alvo
- **Caminho:** `amb_cli/agents/auto_reply.py`
- **Responsabilidade Única (SRP - Regra 01):** Fachada pública de conveniência e CLI delegando chamadas para os submódulos especializados de `amb_cli/agents/auto_reply_core/` (`TurnHistoryExtractor`, `CognitiveAdvisor`, `JulesFeedbackDispatcher`).

---

## 📐 Regras Arquiteturais Obrigatórias (`.agents/rules/`)
1. **Regra 01 (SRP):** O arquivo deve atuar puramente como façade e despachante CLI. Lógica de baixo nível (parsing de turnos, inferência LLM, chamadas HTTP REST) deve permanecer nos módulos especializados do `auto_reply_core/`.
2. **Regra 02 (Atomização):** O arquivo deve ter menos de 200 linhas (teto máximo 300 linhas).
3. **Regra 03 (DRY & Imports Canônicos):** Utilizar sempre imports absolutos (`from config.bootstrap import ensure_amb_env`, `from integrations.jules.jules_client import JulesClient`, `from agents.auto_reply_core import ...`). Proibido imports planos legados.
4. **Regra 04 (Qualidade e Tipagem):** 100% das funções públicas e auxiliares devem possuir type hints completos (`Dict[str, Any]`, `List[Dict[str, Any]]`, `Optional[str]`, `Tuple[...]`).
5. **Regra 05 (Documentação Concisa):** Proibido banners decorativos gigantes ASCII (`# ======...`). Docstrings declarativas de 1 a 3 linhas focadas no propósito da função.
6. **Regra 06 (Segurança Git & Testes):** Nenhuma alteração deve quebrar os testes unitários (`pytest` 100% verde).

---

## 🛠️ Itens Específicos a Verificar / Refatorar
1. **Assinaturas & Type Hints:**
   - Garantir que `extract_activity_text`, `get_last_conversation_turn`, `get_full_session_history`, `advise_and_reply`, `get_pending_sessions` possuam anotações estritas de parâmetros e retornos.
2. **Eliminação de Código Morto:**
   - Garantir que não existam imports não utilizados ou variáveis órfãs.
3. **Delegação Segura:**
   - Assegurar que os aliases de retrocompatibilidade (como `auto_reply_session = advise_and_reply`) continuem preservados para não quebrar módulos externos e testes legados.

---

## 🧪 Validação Obrigatória
Antes de abrir o Pull Request:
```bash
python -m py_compile amb_cli/agents/auto_reply.py
python -m pytest tests/test_auto_reply.py tests/test_auto_reply_srp.py
python -m pytest
```
Todos os 92 testes unitários devem passar (100% green).

---

## 🚀 Ação Final Obrigatória: Abertura do Pull Request
Ao concluir todas as alterações e validar os testes com sucesso (100% green):
1. Você DEVE submeter/abrir o Pull Request no GitHub imediatamente.
2. Não encerre a sessão apenas no estado "Ready for submission"; confirme a criação do PR diretamente no GitHub com título e descrição claros das alterações.
