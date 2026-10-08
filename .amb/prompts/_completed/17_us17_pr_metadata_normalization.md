# US-17: Normalização de Metadados de Pull Request e Exibição de Título

## 📌 Contexto e Objetivo
Conforme documentado no Quickstart da API oficial do Google Jules (`https://jules.google/docs/api/reference/`), quando um PR é gerado pelo Jules ele é retornado na propriedade `outputs[].pullRequest` com o seguinte formato:
```json
{
  "pullRequest": {
    "url": "https://github.com/bobalover/boba/pull/35",
    "title": "Create a boba app",
    "description": "This change adds the initial implementation of a boba app."
  }
}
```

Observe que a API oficial envia `url`, `title` e `description`, mas **não** inclui o campo numérico `"number"`. Várias rotinas internas do AMB_V2 (como `merge_session_pr`, rastreamento de PRs e notificações) esperam poder acessar `pr.get("number")` diretamente.

Esta US normaliza o objeto de PR extraído garantindo que o campo numérico `"number"` esteja sempre presente (extraído via regex da URL caso omitido) e aprimora a exibição em `amb jules get` para apresentar o título do PR.

---

## 📐 Requisitos Técnicos

### 1. Normalização em `session_helpers.py`
- **Arquivo (`amb_cli/integrations/jules/jules_core/session_helpers.py`):**
  - Na função `extract_pull_request`:
    - Ao encontrar um `pullRequest` em `outputs`, verificar se o campo `"number"` já está presente.
    - Se ausente, extrair o número do PR a partir do campo `"url"` usando a regex `r"/pull/(\d+)"` e atribuir `pr_info["number"] = int(match.group(1))`.
    - Garantir que dicionários imutáveis ou cópias sejam tratados com segurança.
    - Manter compatibilidade com a extração via `activities`.

### 2. Exibição Aprimorada em `get_session.py`
- **Arquivo (`amb_cli/integrations/jules/tools/get_session.py`):**
  - Ao imprimir informações do Pull Request no resumo:
    - Se houver `title` em `pr_info`, exibir junto com a URL de forma amigável:
      `  • Pull Request: <url> ("<title>")`

---

## 🧪 Critérios de Aceite
1. **Suíte de Testes Unitários:**
   - Criar `tests/test_pr_metadata_normalization.py` cobrindo:
     - Extração de `pullRequest` vindo de `outputs` da API sem campo `number`, verificando a injeção correta de `number` como inteiro.
     - Extração de `pullRequest` já com `number`.
     - Extração via fallback de `activities`.
2. **Qualidade de Código e Limites Arquiteturais:**
   - 100% dos testes unitários passando (`pytest -q`).
   - Teto rígido de 300 linhas por arquivo (Regra 02).
   - Tipagem estrita com `typing` (Regra 04).
