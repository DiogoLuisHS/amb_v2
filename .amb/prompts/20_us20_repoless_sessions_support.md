# US-20: Suporte a Sessões Sem Repositório (Repoless Sessions com --no-repo)

## 📌 Contexto e Objetivo
A documentação da API REST do Google Jules (`https://jules.google/docs/api/reference/sessions`) especifica que o campo `sourceContext` é **opcional para repoless sessions**:
> `sourceContext`: *The source repository and branch context for this session. Optional for repoless sessions.*

No ecossistema AMB_V2, o método `create_session` atualmente força a injeção de `sourceContext` resolvendo o repositório Git local (`sources/github/{owner}/{repo}`). No entanto, os desenvolvedores frequentemente desejam utilizar o Jules para tarefas conceituais, consultas de arquitetura, brainstorming, design de schemas ou scripts avulsos sem vincular a um repositório GitHub ou abrir Pull Request.

Esta US habilita o suporte a sessões repoless no cliente e na CLI do AMB através da flag `--no-repo` (ou `--repoless`).

---

## 📐 Requisitos Técnicos

### 1. Suporte no `JulesClient` e `create_session`
- **Arquivo (`amb_cli/integrations/jules/jules_client.py`):**
  - No método `create_session`:
    - Adicionar parâmetro `repoless: bool = False`.
    - Se `repoless is True` ou `source_name in ("none", "repoless")`:
      - Não incluir o bloco `sourceContext` no payload JSON.
      - Não incluir `automationMode = "AUTO_CREATE_PR"` (já que não há repositório para criação de PR).
    - Caso contrário, manter o comportamento padrão de auto-detecção do repositório ativo.

### 2. Ferramenta de Criação e CLI
- **Arquivo (`amb_cli/integrations/jules/tools/create_session.py`):**
  - Aceitar `repoless: bool = False`.
  - Se repoless, exibir feedback no terminal:
    `  • Modo: Repoless (Sessão livre sem repositório vinculado)`.
- **Arquivo (`amb_cli/cli_modules/cli_parsers.py`):**
  - Adicionar `--no-repo` (alias `--repoless`, `action="store_true"`) ao comando `amb jules create`:
    `help="Cria sessão avulsa no Jules sem vincular repositório Git."`
- **Arquivo (`amb_cli/cli_modules/handlers_core/jules_handler.py`):**
  - Repassar `repoless=getattr(args, "no_repo", False)` para `run_create_session`.

---

## 🧪 Critérios de Aceite
1. **Suíte de Testes Unitários:**
   - Criar `tests/test_repoless_sessions.py` cobrindo:
     - Criação de sessão repoless com payload sem `sourceContext` e sem `AUTO_CREATE_PR`.
     - Repasse correto da flag `--no-repo` a partir do parser e do handler.
     - Criação padrão preservando `sourceContext` quando a flag não é utilizada.
2. **Qualidade de Código e Limites Arquiteturais:**
   - 100% dos testes unitários passando (`pytest -q`).
   - Teto rígido de 300 linhas por arquivo (Regra 02).
   - Tipagem estrita com `typing` (Regra 04).
