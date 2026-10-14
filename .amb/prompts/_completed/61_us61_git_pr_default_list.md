# US-61: Listagem Padrão de Pull Requests em amb git pr

## 📌 Contexto e Objetivo
Atualmente, quando o desenvolvedor executa `amb git pr` no terminal sem fornecer nenhum subcomando, o argparse não lista os Pull Requests e exige a digitação explícita de `amb git pr list`.
No ecossistema de ferramentas modernas, o comando raiz de uma entidade plural deve listar imediatamente os registros abertos.

Esta US padroniza a execução direta:
```bash
amb git pr
```
Listando instantaneamente todos os Pull Requests abertos no repositório ativo com número, título, autor, branch e status de draft.

---

## 📐 Requisitos Técnicos

### 1. Atualização do Handler do Git
- **Arquivo (`amb_cli/cli_modules/handlers_core/git_handler.py`):**
  - No bloco `sub == "pr"`:
    - Obter `pr_action = getattr(args, "pr_cmd", None)`.
    - Se `not pr_action`:
      - Tratar automaticamente como `"list"`:
        ```python
        pr_action = "list"
        ```
    - Chamar `run_pr_manager(action=pr_action, ...)` e exibir a tabela formatada de PRs abertos.
    - Suportar a flag `--json` mesmo na invocação direta de `amb git pr --json`.

---

## 🧪 Critérios de Aceite
1. **Suíte de Testes Unitários:**
   - Criar `tests/test_git_pr_default_list.py` cobrindo:
     - Execução de `amb git pr` sem subcomando disparando a listagem de PRs abertos.
     - Suporte a flags combinadas como `--no-drafts` e `--json`.
     - Preservação da execução explícita de subcomandos (`amb git pr list`, `create`, `merge`, etc.).
2. **Qualidade de Código:**
   - 100% dos testes passando (`pytest -q`).
   - Teto rígido de 300 linhas por arquivo (Regra 02).
   - Tipagem estrita com `typing` (Regra 04).
