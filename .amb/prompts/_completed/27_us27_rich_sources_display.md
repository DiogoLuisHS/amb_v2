# US-27: Exibição Enriquecida de Fontes Conectadas com Visibilidade e Branch Padrão

## 📌 Contexto e Objetivo
A documentação da API REST do Google Jules (`https://jules.google/docs/api/reference/sources`) especifica os atributos de metadados retornados para cada fonte do GitHub:
```json
{
  "name": "sources/github-myorg-myrepo",
  "id": "github-myorg-myrepo",
  "githubRepo": {
    "owner": "myorg",
    "repo": "myrepo",
    "isPrivate": true,
    "defaultBranch": {
      "displayName": "main"
    }
  }
}
```

No AMB_V2, a ferramenta `run_list_sources` (`amb jules sources`) exibe apenas o identificador da fonte e `(owner/repo)`:
```
  1. sources/github-owner-repo (owner/repo)
```
Informações cruciais como a visibilidade do repositório (`isPrivate`) e a branch padrão configurada (`defaultBranch.displayName`) são descartadas na renderização textual, obrigando o desenvolvedor a inspecionar o JSON bruto com `--json` para checar se a fonte aponta para a branch padrão esperada ou se o repositório é público ou privado.

Esta US enriquece a formatação visual do comando `amb jules sources` para exibir de forma elegante os selos de visibilidade e branch padrão.

---

## 📐 Requisitos Técnicos

### 1. Enriquecimento da Renderização Textual
- **Arquivo (`amb_cli/integrations/jules/tools/list_sources.py`):**
  - No loop de iteração sobre as fontes em `run_list_sources`:
    - Extrair:
      ```python
      github_repo = s.get("githubRepo", {})
      owner = github_repo.get("owner", "")
      repo = github_repo.get("repo", "")
      is_private = github_repo.get("isPrivate")
      default_branch = (github_repo.get("defaultBranch") or {}).get("displayName", "")
      ```
    - Montar tags informativas:
      - Visibilidade: `f"{Colors.YELLOW}[🔒 Privado]{Colors.RESET}"` se `is_private is True`, `f"{Colors.BLUE}[🌐 Público]{Colors.RESET}"` se `is_private is False`, ou string vazia se indefinido.
      - Default Branch: `f"{Colors.DIM}[🌿 Default: {default_branch}]{Colors.RESET}"` se `default_branch` existir.
    - Exibir a linha formatada:
      `  {idx}. {Colors.BOLD}{name}{Colors.RESET} {Colors.GREEN}{repo_str}{Colors.RESET} {tags_str}`
  - Garantir que a saída em formato JSON (`as_json=True`) continue inalterada e retornando o payload bruto integral da API.
  - Manter o limite rígido de 300 linhas por arquivo (Regra 02).

---

## 🧪 Critérios de Aceite
1. **Suíte de Testes Unitários:**
   - Criar `tests/test_sources_display.py` cobrindo:
     - Formatação de repositório privado exibindo tag `[🔒 Privado]`.
     - Formatação de repositório público exibindo tag `[🌐 Público]`.
     - Formatação com `defaultBranch` exibindo `[🌿 Default: main]`.
     - Resiliência contra repositórios sem metadados ou campos ausentes.
     - Chamada com `as_json=True` retornando os dados sem formatação ANSI.
2. **Qualidade de Código e Limites Arquiteturais:**
   - 100% dos testes unitários passando (`pytest -q`).
   - Teto rígido de 300 linhas por arquivo (Regra 02).
   - Tipagem estrita com `typing` (Regra 04).
