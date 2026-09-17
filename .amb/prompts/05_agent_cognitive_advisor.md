# 🎯 Tarefa Jules: Auditoria e Alinhamento de `amb_cli/agents/auto_reply_core/cognitive_advisor.py`

## 📌 Arquivo Alvo
- **Caminho:** `amb_cli/agents/auto_reply_core/cognitive_advisor.py`
- **Responsabilidade Única (SRP - Regra 01):** Formulação contextual e geração cognitiva de respostas técnicas para sessões do Google Jules, integrando regras arquiteturais ativas via `RulesManager` e o modelo LLM via `AntigravityClient` com fallback resiliente.

---

## 📐 Regras Arquiteturais Obrigatórias (`.agents/rules/`)
1. **Regra 01 (SRP):** Foco exclusivo na síntese de prompts, filtragem de regras para o Jules e geração cognitiva via IA.
2. **Regra 02 (Atomização):** Manter o arquivo atômico entre 140 e 200 linhas (teto máximo 300 linhas).
3. **Regra 03 (DRY & Single Source of Truth):**
   - Utilizar `pathlib.Path` para manipulação de arquivos e diretórios de regras.
   - Resolução canônica de regras em `.agents/rules/` com fallback para `.antigravity/rules/` e `.gemini/rules/`.
   - Proibido imports não utilizados (`Colors`, `get_rules_manager`).
4. **Regra 04 (Qualidade e Tipagem):**
   - Tipagem completa: `Optional[Union[str, Path]]`, `Tuple[str, str]`, `Optional[AntigravityClient]`.
   - Observabilidade: captura de erros com logging explícito via `log_error`, proibindo `except Exception: pass` silencioso.
5. **Regra 05 (Documentação Concisa):** Docstrings concisas e técnicas, sem ruídos decorativos.
6. **Regra 06 (Segurança e Testes):** 100% de aprovação na suíte `pytest`.

---

## 🛠️ Itens Específicos a Verificar / Refatorar
1. **Filtragem de Regras para o Jules (`filter_rules_for_jules`):**
   - Garantir que seções de Git/VCS Safety Lock continuem sendo omitidas para não bloquear a capacidade de escrita e commits do Jules na VM de desenvolvimento.
2. **Cache LRU:**
   - Preservar o cache com `@functools.lru_cache(maxsize=128)` para evitar I/O redundante em consultas consecutivas de regras.
3. **Resiliência e Fallback Contextual:**
   - Garantir que `generate_suggestion` capture eventuais falhas de cota ou rede da API Gemini e utilize fallback contextualizado baseado na intenção da pergunta (`open the pr`, `plan`, etc.).

---

## 🧪 Validação Obrigatória
Antes de abrir o Pull Request:
```bash
python -m py_compile amb_cli/agents/auto_reply_core/cognitive_advisor.py
python -m pytest tests/test_auto_reply_srp.py
python -m pytest
```
Todos os 92 testes unitários devem passar (100% green).

---

## 🚀 Ação Final Obrigatória: Abertura do Pull Request
Ao concluir todas as alterações e validar os testes com sucesso (100% green):
1. Você DEVE submeter/abrir o Pull Request no GitHub imediatamente.
2. Não encerre a sessão apenas no estado "Ready for submission"; confirme a criação do PR diretamente no GitHub com título e descrição claros das alterações.
