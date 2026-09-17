# 🎯 Tarefa Jules: Auditoria e Alinhamento de `amb_cli/agents/loop_core/cycle_dispatcher.py`

## 📌 Arquivo Alvo
- **Caminho:** `amb_cli/agents/loop_core/cycle_dispatcher.py`
- **Responsabilidade Única (SRP - Regra 01):** Preparação de contexto arquitetural enriquecido via `ai_context_builder`, despacho de novas sessões para a API do Google Jules e aprovação/integração automática de PRs no repositório Git local.

---

## 📐 Regras Arquiteturais Obrigatórias (`.agents/rules/`)
1. **Regra 01 (SRP):** Concentrar exclusivamente a lógica de preparação de payload de prompt, despacho inicial no Jules e merge de Pull Requests resultantes do ciclo.
2. **Regra 02 (Atomização):** Manter o arquivo atômico (entre 90 e 150 linhas, teto máximo 300).
3. **Regra 03 (DRY & Imports Canônicos):**
   - Imports absolutos:
     ```python
     from integrations.jules.jules_client import JulesClient
     from integrations.jules.tools.merge_session_pr import approve_and_merge_pr
     from integrations.git.git_service import GitService
     ```
4. **Regra 04 (Qualidade e Tipagem):**
   - Assinaturas tipadas:
     - `build_ai_context(base_prompt: str, current_module: Optional[str], role: str) -> str`
     - `dispatch_jules_session(client: JulesClient, full_prompt: str, source_name: str, session_title: str, branch: str) -> str`
     - `handle_pr_merge(session_id: str, branch: str, repo_root: str, completed_cycles: int) -> None`
5. **Regra 05 (Documentação Concisa):** Docstrings concisas e sem ruídos visuais.
6. **Regra 06 (Segurança e Testes):** Testes unitários 100% verdes.

---

## 🛠️ Itens Específicos a Verificar / Refatorar
1. **Integração com `ai_context_builder`:**
   - Garantir import dinâmico/protegido com captura graciosa caso o analisador de contexto encontre dependências ausentes, retornando o `base_prompt` sem quebrar o despacho.
2. **Despacho e Captura de Session ID:**
   - Normalizar a captura do ID da sessão a partir da resposta (`session_resp.get("name")` ou `session_resp.get("id")`).
3. **Merge Git e Sincronização:**
   - Após `approve_and_merge_pr`, garantir que `GitService(repo_root=repo_root).pull(...)` sincronize o estado do git local com a branch de destino.

---

## 🧪 Validação Obrigatória
Antes de abrir o Pull Request:
```bash
python -m py_compile amb_cli/agents/loop_core/cycle_dispatcher.py
python -m pytest
```
Todos os 92 testes unitários devem passar (100% green).
