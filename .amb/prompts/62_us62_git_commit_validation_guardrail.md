# US-62: Commit Atômico com Guardrail de Validação Arquitetural (amb git commit)

## 📌 Contexto e Objetivo
Para manter a integridade do repositório antes de cada commit, o desenvolvedor atualmente precisa lembrar de rodar manualmente `amb validate --staged` antes de executar `git commit -m "..."`.
Caso o desenvolvedor não tenha instalado o hook pré-commit em sua máquina, commits que violam as regras canônicas do ecossistema (ex: arquivos ultrapassando o teto de 300 linhas ou quebrando convenções do AGENTS.md) acabam sendo gravados e enviados, quebrando os pipelines e a esteira do Jules.

Esta US cria o comando de commit protegido e atômico:
```bash
amb git commit "feat: novo parser modular"
```
Ele executa a auditoria das regras nos arquivos preparados no stage e, somente se todos estiverem 100% em conformidade, realiza o commit no Git.

---

## 📐 Requisitos Técnicos

### 1. Atualização do Parser CLI
- **Arquivo (`amb_cli/cli_modules/cli_parsers.py`):**
  - No subparser `git`:
    - Adicionar o subcomando `commit`:
      ```python
      gc = _sc(gs, "commit", "Valida a conformidade arquitetural do stage e realiza o commit com segurança.")
      gc.add_argument("message", help="Mensagem do commit.")
      gc.add_argument("--no-verify", action="store_true", help="Ignora a validação das regras arquiteturais.")
      ```

### 2. Atualização do Handler do Git
- **Arquivo (`amb_cli/cli_modules/handlers_core/git_handler.py`):**
  - No bloco `sub == "commit"`:
    - Obter `message = getattr(args, "message", None)`.
    - Se `not getattr(args, "no_verify", False)`:
      - Executar `from workspace import get_rules_manager`.
      - Instanciar `mgr = get_rules_manager()` e validar os arquivos em stage.
      - Se houver arquivos violando as regras canônicas (ex: > 300 linhas):
        - Exibir aviso de bloqueio em vermelho e abortar o commit.
    - Se a validação passar (ou `--no-verify`):
      - Invocar `git.commit(message=message)` via `GitService`.
      - Imprimir confirmação com o hash gerado: `✔ Commit realizado com sucesso!`.
  - Manter o limite rígido de 300 linhas por arquivo (Regra 02).

---

## 🧪 Critérios de Aceite
1. **Suíte de Testes Unitários:**
   - Criar `tests/test_git_commit_guardrail.py` cobrindo:
     - Execução de `amb git commit` com stage limpo e válido realizando o commit com sucesso.
     - Bloqueio imediato do commit quando um arquivo em stage viola as regras arquiteturais.
     - Bypass de validação com a flag `--no-verify`.
2. **Qualidade de Código:**
   - 100% dos testes passando (`pytest -q`).
   - Teto rígido de 300 linhas por arquivo (Regra 02).
   - Tipagem estrita com `typing` (Regra 04).
