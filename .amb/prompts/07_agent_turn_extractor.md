# 🎯 Tarefa Jules: Auditoria e Alinhamento de `amb_cli/agents/auto_reply_core/turn_extractor.py`

## 📌 Arquivo Alvo
- **Caminho:** `amb_cli/agents/auto_reply_core/turn_extractor.py`
- **Responsabilidade Única (SRP - Regra 01):** Extração, decodificação de payloads polimórficos de atividades do Jules REST API e determinação estrita de turnos de conversação (quem falou por último, última pergunta ativa e status de aprovação de plano).

---

## 📐 Regras Arquiteturais Obrigatórias (`.agents/rules/`)
1. **Regra 01 (SRP):** Foco exclusivo no parsing, análise e estruturação de históricos e turnos de conversação. Sem dependência direta de rede ou clientes REST no corpo da análise.
2. **Regra 02 (Atomização):** Manter o arquivo atômico entre 150 e 220 linhas (teto máximo 300).
3. **Regra 03 (DRY & Zero Redundância):**
   - Utilizar o helper `_extract_text_from_node` para evitar duplicação de buscas em dicionários e estruturas aninhadas (`agentMessage`, `userMessage`, `text`, `message`, `question`).
   - Sem imports mortos.
4. **Regra 04 (Qualidade e Tipagem):**
   - Anotações completas: `activity: Dict[str, Any]`, `acts: List[Dict[str, Any]]`, `role: str = "agent"`, retorno `Dict[str, Any]`.
5. **Regra 05 (Documentação Concisa):** Docstrings explicativas e sem banners decorativos.
6. **Regra 06 (Segurança e Testes):** Suíte `pytest` 100% verde.

---

## 🛠️ Itens Críticos de Implementação (Bug #18 Prevenção)
1. **Garantia de Ordem Cronológica Decrescente em `get_last_conversation_turn`:**
   - A API do Jules retorna atividades ordenadas da mais antiga para a mais recente.
   - O método `get_last_conversation_turn` DEVE ordenar as atividades por `createTime` decrescente (mais recente primeiro) antes da iteração.
2. **Priorização de Mensagens do Agente no Chat:**
   - Dúvidas no chat (`agentMessaged` / `extract_activity_text`) devem ser avaliadas antes de planos antigos, garantindo que `last_speaker = 'AGENT'` quando há uma pergunta nova.
3. **Ordem Cronológica Crescente em `get_full_session_history`:**
   - O histórico de chat linear retornado para exibição ao usuário ou envio ao LLM deve ser formatado em ordem cronológica estrita (da mais antiga para a mais recente).

---

## 🧪 Validação Obrigatória
Antes de abrir o Pull Request:
```bash
python -m py_compile amb_cli/agents/auto_reply_core/turn_extractor.py
python -m pytest tests/test_auto_reply.py tests/test_auto_reply_srp.py
python -m pytest
```
Todos os 92 testes unitários devem passar (100% green).

---

## 🚀 Ação Final Obrigatória: Abertura do Pull Request
Ao concluir todas as alterações e validar os testes com sucesso (100% green):
1. Você DEVE submeter/abrir o Pull Request no GitHub imediatamente.
2. Não encerre a sessão apenas no estado "Ready for submission"; confirme a criação do PR diretamente no GitHub com título e descrição claros das alterações.
