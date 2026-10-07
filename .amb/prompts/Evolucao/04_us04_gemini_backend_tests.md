# 🎯 US-04: Suíte de Testes Unitários Dedicada para `GeminiBackend`

## 👤 User Story
> **Como** mantenedor do AMB_V2,  
> **Quero** um novo arquivo de testes `tests/test_gemini_backend.py` cobrindo todos os cenários da integração com o SDK oficial,  
> **Para que** a cobertura de testes permaneça alta e o arquivo `tests/test_antigravity_integration.py` não ultrapasse o teto de 300 linhas.

---

## 📌 Critérios de Aceitação BDD

* **Cenário 1: Teste de geração bem-sucedida com Mock do SDK**
  * **Dado** um mock de `genai.Client` retornando `MagicMock(text="Resposta mockada com sucesso")`;
  * **Quando** `_generate_via_gemini_api` for invocado com `HAS_GENAI_SDK = True`;
  * **Então** o resultado retornado deve ser `"Resposta mockada com sucesso"`.

* **Cenário 2: Teste de fallback para REST quando SDK ausente**
  * **Dado** que `HAS_GENAI_SDK` foi mockado como `False`;
  * **Quando** `_generate_via_gemini_api` for chamado;
  * **Então** deve acionar `google_client.execute_request` retornando a resposta da REST API.

* **Cenário 3: Teste de rotação de modelo em erro 429**
  * **Dado** que a primeira chamada do modelo gera erro 429 de quota;
  * **Quando** o loop de modelos for acionado;
  * **Então** deve tentar o segundo modelo da lista e retornar a resposta se o segundo modelo tiver sucesso.

* **Cenário 4: Teste de chave ausente**
  * **Dado** que `api_key` é None ou vazia e `GEMINI_API_KEY` não está no ambiente;
  * **Quando** for executada a chamada;
  * **Então** deve disparar `ConfigurationError` informando a ausência da chave.

---

## 🛠️ Arquivos Alvo & Alterações Necessárias

### Criar Novo Arquivo: `tests/test_gemini_backend.py`
> ⚠️ **ATENÇÃO:** Não edite `tests/test_antigravity_integration.py` (ele já tem 287 linhas).

Estrutura de testes recomendada:
```python
# -*- coding: utf-8 -*-
"""Testes unitários isolados para o backend cognitivo GeminiBackend."""

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch
import pytest

_root = Path(__file__).resolve().parent.parent
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))
from core.bootstrap import ensure_amb_env
ensure_amb_env()

from core import ApiExecutionError, ConfigurationError
from integrations.antigravity.antigravity_core.gemini_backend import GeminiBackend


def test_generate_via_sdk_success():
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.text = "Conteúdo gerado via SDK"
    mock_client.models.generate_content.return_value = mock_response

    mock_google = MagicMock()
    backend = GeminiBackend(api_key="fake-key", google_client=mock_google)

    with patch("integrations.antigravity.antigravity_core.gemini_backend.HAS_GENAI_SDK", True), \
         patch("integrations.antigravity.antigravity_core.gemini_backend.genai.Client", return_value=mock_client):
        result = backend._generate_via_gemini_api(prompt="Olá", model="gemini-2.5-flash")
        assert result == "Conteúdo gerado via SDK"


def test_generate_fallback_to_rest_when_sdk_missing():
    mock_google = MagicMock()
    mock_google.execute_request.return_value = {
        "candidates": [{"content": {"parts": [{"text": "Resposta via REST legada"}]}}]
    }
    backend = GeminiBackend(api_key="fake-key", google_client=mock_google)

    with patch("integrations.antigravity.antigravity_core.gemini_backend.HAS_GENAI_SDK", False):
        result = backend._generate_via_gemini_api(prompt="Olá", model="gemini-2.5-flash")
        assert result == "Resposta via REST legada"
        assert mock_google.execute_request.called


def test_generate_rate_limit_rotates_model():
    mock_client = MagicMock()
    # Primeiro modelo falha com 429, segundo modelo tem sucesso
    mock_res_ok = MagicMock(text="Sucesso no segundo modelo")
    mock_client.models.generate_content.side_effect = [
        Exception("429 ResourceExhausted"),
        mock_res_ok
    ]

    mock_google = MagicMock()
    backend = GeminiBackend(api_key="fake-key", google_client=mock_google)

    with patch("integrations.antigravity.antigravity_core.gemini_backend.HAS_GENAI_SDK", True), \
         patch("integrations.antigravity.antigravity_core.gemini_backend.genai.Client", return_value=mock_client):
        result = backend._generate_via_gemini_api(prompt="Olá", model="gemini-2.5-flash")
        assert result == "Sucesso no segundo modelo"


def test_missing_api_key_raises_error():
    mock_google = MagicMock()
    backend = GeminiBackend(api_key=None, google_client=mock_google)
    with patch.dict("os.environ", {}, clear=True):
        with pytest.raises((ConfigurationError, Exception)):
            backend._generate_via_gemini_api(prompt="Olá", model="gemini-2.5-flash")
```
Teto do arquivo: <= 180 linhas.

---

## 🔍 Comandos de Verificação Local
```bash
# 1. Executar os novos testes unitários
pytest tests/test_gemini_backend.py -v

# 2. Executar toda a suíte pytest para garantir integridade
pytest -q

# 3. Validar limite de linhas
python -m amb_cli.cli validate tests/test_gemini_backend.py
```

---

## 📋 Definition of Done (DoD)
- [ ] Arquivo `tests/test_gemini_backend.py` criado com 4+ testes unitários.
- [ ] 100% de sucesso na execução com `pytest tests/test_gemini_backend.py`.
- [ ] Suíte global `pytest` passa com 163+ testes sem regressões.
- [ ] Nenhum arquivo tocado ultrapassa 200 linhas.
