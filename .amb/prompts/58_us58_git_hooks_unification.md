# US-58: Unificação de Hooks de Governança sob o Git (amb git hooks [install|status])

## 📌 Contexto e Objetivo
Atualmente, os hooks do Git são gerenciados por um comando isolado de primeiro nível (`amb hooks install`), enquanto todas as demais operações de controle de versão residem sob o namespace `amb git`.
Essa fragmentação dispersa a experiência do desenvolvedor e não oferece um mecanismo para verificar se os hooks estão ativos.

Esta US unifica a governança de hooks sob o namespace canônico do Git:
1. **`amb git hooks install`:** Instala o hook de pré-commit (`.git/hooks/pre-commit`) que executa a validação arquitetural dos arquivos no stage (`amb validate --staged`).
2. **`amb git hooks status` (ou `check`):** Audita se o hook de pré-commit existe, está com permissão de execução e contém o script correto do AMB_V2.
3. **Atalho Transparente:** O comando raiz `amb hooks` delega de forma direta para `amb git hooks`, mantendo sintaxe limpa.

---

## 📐 Requisitos Técnicos

### 1. Atualização do Parser CLI
- **Arquivo (`amb_cli/cli_modules/cli_parsers.py`):**
  - No subparser `git`:
    - Adicionar o subcomando `hooks`:
      ```python
      hs = _sc(gs, "hooks", "Gerencia e audita hooks do Git no repositório.").add_subparsers(dest="hooks_action", help="Ações de hooks")
      _sc(hs, "install", "Instala o pre-commit hook de validação do AMB_V2.")
      _sc(hs, "status", "Verifica se o pre-commit hook está instalado e ativo.", ["check"])
      ```

### 2. Atualização dos Handlers
- **Arquivo (`amb_cli/cli_modules/handlers_core/hooks_handler.py`):**
  - Implementar verificação em `sub == "status"`:
    - Checa existência de `.git/hooks/pre-commit`.
    - Verifica se o conteúdo contém `amb_cli.cli validate --staged`.
    - Imprime status visual colorido:
      `✅ Hook pre-commit: Ativo e configurado.` ou `⚠️ Hook pre-commit: Não instalado.`
- **Arquivo (`amb_cli/cli_modules/handlers_core/git_handler.py`):**
  - No bloco `sub == "hooks"`:
    - Repassar para `handle_cmd_hooks(args)`.

---

## 🧪 Critérios de Aceite
1. **Suíte de Testes Unitários:**
   - Criar `tests/test_git_hooks_unification.py` cobrindo:
     - Instalação via `amb git hooks install` gerando o arquivo com permissões adequadas.
     - Checagem via `amb git hooks status` detectando hook instalado vs. ausente.
     - Invocação através do atalho raiz `amb hooks install`.
2. **Qualidade de Código:**
   - 100% dos testes passando (`pytest -q`).
   - Teto rígido de 300 linhas por arquivo (Regra 02).
   - Tipagem estrita com `typing` (Regra 04).
