# US-19: Enriquecimento Semântico de Erros da API Google com Status Canônico

## 📌 Contexto e Objetivo
A documentação da API REST do Google Jules (`https://jules.google/docs/api/reference/overview`) especifica o formato padrão de resposta para falhas na API:
```json
{
  "error": {
    "code": 400,
    "message": "Invalid session ID format",
    "status": "INVALID_ARGUMENT"
  }
}
```

O campo canônico `"status"` (como `INVALID_ARGUMENT`, `UNAUTHENTICATED`, `PERMISSION_DENIED`, `NOT_FOUND`, `RESOURCE_EXHAUSTED` e `INTERNAL`) é essencial para que os sistemas do ecossistema Google e os agentes autônomos compreendam com precisão cirúrgica a categoria exata da falha.

No AMB_V2, o método `_normalize_error` em `amb_cli/integrations/common/base_google_client.py` extrai apenas a mensagem de texto (`message`), descartando o `status`. Esta US enriquece a normalização semântica de erros incluindo o identificador canônico `status` nas mensagens de exceção (`ApiExecutionError`).

---

## 📐 Requisitos Técnicos

### 1. Captura e Formatação do Status em `base_google_client.py`
- **Arquivo (`amb_cli/integrations/common/base_google_client.py`):**
  - No método `_normalize_error`:
    - Ao decodificar o objeto JSON `error`, extrair tanto `message` quanto `status` (`err_status = err_obj.get("status")`).
    - Se `err_status` estiver presente, formatar o prefixo como:
      `HTTP {status_code} [{err_status}] na API {self.service_name}`.
    - Se `err_status` não estiver presente, manter o prefixo padrão:
      `HTTP {status_code} na API {self.service_name}`.
    - Se houver `detail` (`message`), concatenar: `{prefixo} - {detail}`.
    - Garantir que todos os dados sensíveis permaneçam mascarados via `mask_sensitive_data`.
  - Manter o arquivo estritamente abaixo do teto de 300 linhas (Regra 02).

---

## 🧪 Critérios de Aceite
1. **Suíte de Testes Unitários:**
   - Criar `tests/test_base_google_client_error_enrichment.py` cobrindo:
     - Erro HTTP com payload JSON contendo `code`, `message` e `status` (ex: `INVALID_ARGUMENT`, `RESOURCE_EXHAUSTED`), verificando a mensagem formatada contendo `[STATUS]`.
     - Erro HTTP com payload JSON contendo apenas `message` (sem `status`), verificando retrocompatibilidade.
     - Erro HTTP com corpo não JSON (texto puro ou vazio).
2. **Qualidade de Código e Limites Arquiteturais:**
   - 100% dos testes unitários passando (`pytest -q`).
   - Teto rígido de 300 linhas por arquivo (Regra 02).
   - Tipagem estrita com `typing` (Regra 04).
