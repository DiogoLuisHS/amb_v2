# US-26: Validação Preventiva de Branch Existente antes de Criar Sessão Jules

## 📌 Contexto e Objetivo
A documentação da API REST do Google Jules (`https://jules.google/docs/api/reference/sources`) documenta que o endpoint `GET /v1alpha/sources/{sourceId}` expõe a lista completa de branches sincronizadas do repositório (`branches`) e a branch padrão (`defaultBranch`):
```json
{
  "name": "sources/github-myorg-myrepo",
  "githubRepo": {
    "owner": "myorg",
    "repo": "myrepo",
    "isPrivate": false,
    "defaultBranch": { "displayName": "main" },
    "branches": [
      { "displayName": "main" },
      { "displayName": "develop" }
    ]
  }
}
```

No AMB_V2, quando um desenvolvedor executa `amb jules create -p "..." -b "minha-feature"` ou quando a branch ativa local é auto-detectada, a criação falha com erro 400 (`INVALID_ARGUMENT`) caso a branch ainda não tenha sido enviada ao remoto GitHub ou não esteja sincronizada no Jules.

Esta US implementa uma validação preventiva e amigável da branch antes de submeter a requisição de criação de sessão, alertando o usuário antecipadamente e sugerindo a branch padrão (`defaultBranch`), com opção de ignorar a checagem via `--skip-branch-check`.

---

## 📐 Requisitos Técnicos

### 1. Método Utilitário de Verificação de Branch
- **Arquivo (`amb_cli/integrations/jules/jules_core/session_helpers.py`):**
  - Adicionar a função:
    ```python
    def check_branch_exists_in_source(
        source_data: Dict[str, Any],
        branch_name: str
    ) -> Tuple[bool, Optional[str]]:
        """
        Verifica se a branch informada está presente nas branches da fonte.
        Retorna (existe, default_branch_name).
        Se a lista de branches estiver vazia ou ausente, retorna (True, default_branch)
        para não bloquear de forma restritiva.
        """
    ```
  - Obter `branches = source_data.get("githubRepo", {}).get("branches", [])`.
  - Obter `default_branch = source_data.get("githubRepo", {}).get("defaultBranch", {}).get("displayName")`.
  - Se `branches` for vazio, retornar `(True, default_branch)`.
  - Verificar se `any(b.get("displayName") == branch_name for b in branches)`. Retornar `(True, default_branch)` ou `(False, default_branch)`.

### 2. Validação Preventiva em `create_session.py`
- **Arquivo (`amb_cli/integrations/jules/tools/create_session.py`):**
  - No método `run_create_session(..., skip_branch_check: bool = False)`:
    - Se `not skip_branch_check` e `source` não for nulo/repoless:
      - Tentar obter os metadados da fonte via `source_info = client.get_source(resolved_source)`.
      - Se obtido com sucesso, invocar `exists, default_branch = check_branch_exists_in_source(source_info, base_branch)`.
      - Se `not exists`:
        - Emitir alerta no terminal:
          `⚠️ Aviso: A branch '{base_branch}' não foi encontrada nas branches sincronizadas da fonte '{resolved_source}'.`
          `   Branch padrão detectada: '{default_branch}'. Certifique-se de ter feito 'git push' da branch.`
      - Tratar qualquer exceção em `get_source` (ex: 404 ou sem permissão) silenciosamente com log em debug, para que a validação nunca impeça a tentativa normal de criação de sessão.

### 3. Suporte na Camada CLI
- **Arquivo (`amb_cli/cli_modules/cli_parsers.py`):**
  - No subparser `create`:
    ```python
    j.add_argument("--skip-branch-check", action="store_true", help="Ignora a validação preventiva de existência da branch na fonte do Jules.")
    ```
- **Arquivo (`amb_cli/cli_modules/handlers_core/jules_handler.py`):**
  - No bloco `sub == "create"`:
    - Repassar `skip_branch_check=getattr(args, "skip_branch_check", False)` para `run_create_session(...)`.

---

## 🧪 Critérios de Aceite
1. **Suíte de Testes Unitários:**
   - Criar `tests/test_source_branch_validation.py` cobrindo:
     - `check_branch_exists_in_source` com branch existente na lista (retorna `(True, ...)`).
     - `check_branch_exists_in_source` com branch ausente (retorna `(False, ...)` com default branch).
     - Comportamento resiliente quando `branches` é lista vazia (retorna `(True, ...)`).
     - Execução de `run_create_session` exibindo alerta preventivo sem quebrar a execução.
     - Funcionamento da flag `--skip-branch-check`.
2. **Qualidade de Código e Limites Arquiteturais:**
   - 100% dos testes unitários passando (`pytest -q`).
   - Teto rígido de 300 linhas por arquivo (Regra 02).
   - Tipagem estrita com `typing` (Regra 04).
