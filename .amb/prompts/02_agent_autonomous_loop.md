# 🎯 Tarefa Jules: Auditoria e Alinhamento de `amb_cli/agents/autonomous_loop.py`

## 📌 Arquivo Alvo
- **Caminho:** `amb_cli/agents/autonomous_loop.py`
- **Responsabilidade Única (SRP - Regra 01):** Orquestrador de alto nível dos ciclos de desenvolvimento autônomo contínuo, delegando despacho e preparação de contexto para `amb_cli/agents/loop_core/cycle_dispatcher.py` e monitoramento/assistência cognitiva para `amb_cli/agents/loop_core/session_assistant.py`.

---

## 📐 Regras Arquiteturais Obrigatórias (`.agents/rules/`)
1. **Regra 01 (SRP):** Manter o arquivo estritamente como orquestrador do loop (`run_autonomous_loop`, `load_persona_content`, `main`). Não incorporar lógica direta de REST API ou polling de turnos de baixo nível neste arquivo.
2. **Regra 02 (Atomização):** Limite estrito de linhas: manter entre 150 e 280 linhas (teto máximo 300).
3. **Regra 03 (DRY & Imports Canônicos):**
   - Utilizar os submódulos de `loop_core`:
     ```python
     from agents.loop_core.session_assistant import monitor_and_assist_session
     from agents.loop_core.cycle_dispatcher import build_ai_context, dispatch_jules_session, handle_pr_merge
     ```
   - Imports absolutos de serviços e clients (`from integrations.git.git_service import GitService`, `from integrations.jules.jules_client import JulesClient`).
4. **Regra 04 (Qualidade e Tipagem):** Tipagem explícita de argumentos e retornos (`Optional[str]`, `Optional[List[str]]`, `-> None`, `-> tuple[str, str]`).
5. **Regra 05 (Documentação Concisa):** Cabeçalho conciso declarando a Responsabilidade Única, sem separadores visuais repetitivos ou comentários redundantes.
6. **Regra 06 (Segurança e Testes):** Testes unitários do projeto devem rodar com 100% de sucesso.

---

## 🛠️ Itens Específicos a Verificar / Refatorar
1. **Delegação Limpa:**
   - Assegurar que `run_autonomous_loop` invoca `build_ai_context(...)`, `dispatch_jules_session(...)`, `monitor_and_assist_session(...)` e `handle_pr_merge(...)`.
2. **Tratamento de Argumentos CLI:**
   - Garantir que `argparse` em `main()` suporte todas as opções: `--role`, `--all`, `--prompt`, `--modules`, `--max-cycles`, `--delay`, `--branch`, `--no-auto-merge`.
3. **Resiliência a Interrupção:**
   - Preservar captura graciosa de `KeyboardInterrupt` sem quebra de estado ou corrupção de arquivos.

---

## 🧪 Validação Obrigatória
Antes de abrir o Pull Request:
```bash
python -m py_compile amb_cli/agents/autonomous_loop.py
python -m pytest
```
Todos os 92 testes unitários devem passar (100% green).
