# US-24: Extração e Exibição de suggestedCommitMessage em amb jules extract

## 📌 Contexto e Objetivo
A documentação da API REST do Google Jules (`https://jules.google/docs/api/reference/activities`) documenta que todo artefato `changeSet` com alterações de código contém metadados do patch Git:
```json
{
  "changeSet": {
    "source": "sources/github-myorg-myrepo",
    "gitPatch": {
      "baseCommitId": "a1b2c3d4e5f6",
      "unidiffPatch": "diff --git a/src/auth.js b/src/auth.js...",
      "suggestedCommitMessage": "Add authentication tests"
    }
  }
}
```

No AMB_V2, o comando `amb jules extract <session_id>` extrai o `unidiffPatch` e salva o arquivo `.patch` (ou aplica via `git apply`), mas atualmente descarta a mensagem de commit sugerida pelo Jules (`suggestedCommitMessage`). Essa mensagem é extremamente útil para que o desenvolvedor crie o commit Git local com uma mensagem de alta qualidade e semântica gerada diretamente pela IA do Jules.

Esta US enriquece o `SessionExtractor` e o comando `amb jules extract` para capturar e exibir a mensagem de commit sugerida.

---

## 📐 Requisitos Técnicos

### 1. Método `extract_commit_message` em `SessionExtractor`
- **Arquivo (`amb_cli/integrations/jules/jules_core/session_extractor.py`):**
  - Adicionar o método estático:
    ```python
    @staticmethod
    def extract_commit_message(session_data: dict) -> Optional[str]:
        """Extrai a suggestedCommitMessage do gitPatch se presente nos outputs."""
    ```
  - Percorrer `outputs` procurando `out.get("changeSet", {}).get("gitPatch", {}).get("suggestedCommitMessage")`.
  - Retornar a string limpa ou `None` caso não esteja presente.
  - Manter o limite rígido de 300 linhas por arquivo (Regra 02).

### 2. Exibição no Comando de Extração
- **Arquivo (`amb_cli/integrations/jules/tools/extract_session.py`):**
  - No método `run_extract_session`:
    - Chamar `suggested_msg = SessionExtractor.extract_commit_message(session_data)`.
    - Se presente, exibir logo após o tamanho do patch:
      `  • Commit sugerido: "<suggested_msg>"`

---

## 🧪 Critérios de Aceite
1. **Suíte de Testes Unitários:**
   - Criar `tests/test_extract_suggested_commit.py` cobrindo:
     - Extração correta de `suggestedCommitMessage` a partir dos outputs da sessão.
     - Comportamento quando o campo está ausente (retornando `None`).
     - Exibição da mensagem no terminal em `run_extract_session`.
2. **Qualidade de Código e Limites Arquiteturais:**
   - 100% dos testes unitários passando (`pytest -q`).
   - Teto rígido de 300 linhas por arquivo (Regra 02).
   - Tipagem estrita com `typing` (Regra 04).
