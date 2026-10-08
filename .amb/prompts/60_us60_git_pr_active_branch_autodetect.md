# US-60: Auto-Detecção de PR pela Branch Ativa em amb git pr get e merge

## 📌 Contexto e Objetivo
Atualmente, comandos como `amb git pr get <id>` e `amb git pr merge <id>` exigem que o usuário digite obrigatoriamente o número do Pull Request.
No entanto, no fluxo comum de desenvolvimento, o engenheiro já está com checkout ativo na branch da feature (`feature/auth`). Ter que abrir o GitHub ou rodar `amb git pr list` apenas para descobrir o número do PR antes de ver detalhes ou fazer merge adiciona passos desnecessários.

Esta US traz inteligência de contexto do Git:
```bash
amb git pr get
# ou para aprovar e mergear a branch atual:
amb git pr merge
```
Se o número do PR for omitido, o sistema consulta os PRs abertos associados à branch ativa (`git branch --show-current`) e executa a operação diretamente.

---

## 📐 Requisitos Técnicos

### 1. Atualização do Parser CLI
- **Arquivo (`amb_cli/cli_modules/cli_parsers.py`):**
  - Na função auxiliar `_pr_num(p)` utilizada pelos comandos `get`, `ready`, `approve`, `merge`, `close`:
    - Tornar o argumento `number` opcional:
      ```python
      p.add_argument("number", nargs="?", type=int, help="Número do Pull Request (opcional se executado na branch do PR).")
      ```

### 2. Auto-Detecção no GitService / PR Manager
- **Arquivo (`amb_cli/integrations/git/tools/pr_manager.py`):**
  - Se `not pr_number`:
    - Obter a branch ativa do repositório:
      ```python
      current_branch = git.get_current_branch()
      ```
    - Se a branch for `main`, `master` ou `develop`:
      - Exibir erro amigável informando que não há PR em branch base, solicitando informar o número explicitamente.
    - Listar os PRs abertos no repositório (`git.list_open_prs`) e localizar o PR onde `headRefName == current_branch`.
    - Se encontrado, utilizar o número localizado e prosseguir com a operação.
    - Se não encontrado, exibir erro orientando o usuário a abrir um PR com `amb git pr create`.
  - Manter o limite rígido de 300 linhas por arquivo (Regra 02).

---

## 🧪 Critérios de Aceite
1. **Suíte de Testes Unitários:**
   - Criar `tests/test_git_pr_active_branch.py` cobrindo:
     - Execução de `amb git pr get` sem número em branch com PR aberto associado.
     - Execução de `amb git pr merge` sem número mesclando o PR da branch ativa.
     - Validação de erro claro caso executado na branch padrão (`main`/`develop`) sem número.
     - Preservação da execução passando número explicitamente.
2. **Qualidade de Código:**
   - 100% dos testes passando (`pytest -q`).
   - Teto rígido de 300 linhas por arquivo (Regra 02).
   - Tipagem estrita com `typing` (Regra 04).
