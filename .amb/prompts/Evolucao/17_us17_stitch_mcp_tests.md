# 🎯 US-17: Suíte de Testes Unitários Dedicada para `StitchMCPServer`

## 👤 User Story
> **Como** mantenedor do AMB_V2,  
> **Quero** um novo arquivo de testes `tests/test_stitch_mcp.py` cobrindo o ciclo completo do servidor MCP do Stitch,  
> **Para que** a integridade do protocolo stdio seja validada sem adicionar linhas ao arquivo `test_stitch_integration.py` (que já possui 333 linhas).

---

## 📌 Critérios de Aceitação BDD

* **Cenário 1: Teste do método `initialize` e versão de protocolo**
  * **Dado** o servidor `StitchMCPServer`;
  * **Quando** receber requisição de handshake `initialize`;
  * **Então** a resposta deve declarar versão `"2024-11-05"` e metadados `"amb-stitch-mcp"`.

* **Cenário 2: Teste de `tools/list` confirmando schemas**
  * **Dado** a solicitação de listagem de ferramentas;
  * **Quando** o servidor responder;
  * **Então** as 4 ferramentas do Stitch devem estar presentes com propriedades válidas.

* **Cenário 3: Teste de `tools/call` com despacho correto**
  * **Dado** um mock de `StitchClient`;
  * **Quando** `tools/call` for executado para `generate_screen`;
  * **Então** `mock_client.generate_screen` deve ser chamado com os argumentos fornecidos e o retorno deve ter `"isError": false`.

* **Cenário 4: Teste de erro estruturado em falhas**
  * **Dado** que o client disparou exceção durante a chamada da ferramenta;
  * **Quando** o retorno for inspecionado;
  * **Então** a resposta JSON-RPC deve conter `"isError": true` sem quebrar a execução.

---

## 🛠️ Arquivos Alvo & Alterações Necessárias

### Criar Novo Arquivo: `tests/test_stitch_mcp.py`
> ⚠️ **ATENÇÃO:** Não edite `tests/test_stitch_integration.py` para não violar a Regra 02.

```python
# -*- coding: utf-8 -*-
"""Testes unitários dedicados para o servidor MCP do Google Stitch."""

import sys
import json
from pathlib import Path
from unittest.mock import MagicMock
import pytest

_root = Path(__file__).resolve().parent.parent
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))
from core.bootstrap import ensure_amb_env
ensure_amb_env()

from integrations.stitch.stitch_core.mcp_server import StitchMCPServer


def test_mcp_initialize():
    server = StitchMCPServer(client=MagicMock())
    req = {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}}
    resp = server.handle_request(req)
    assert resp["id"] == 1
    assert resp["result"]["protocolVersion"] == "2024-11-05"
    assert resp["result"]["serverInfo"]["name"] == "amb-stitch-mcp"


def test_mcp_notifications_initialized_returns_none():
    server = StitchMCPServer(client=MagicMock())
    req = {"jsonrpc": "2.0", "method": "notifications/initialized"}
    resp = server.handle_request(req)
    assert resp is None


def test_mcp_tools_list_contains_canonical_tools():
    server = StitchMCPServer(client=MagicMock())
    req = {"jsonrpc": "2.0", "id": 2, "method": "tools/list"}
    resp = server.handle_request(req)
    tools = resp["result"]["tools"]
    tool_names = [t["name"] for t in tools]
    assert "generate_screen" in tool_names
    assert "refine_screen" in tool_names
    assert "get_screen" in tool_names
    assert "list_screens" in tool_names


def test_mcp_tools_call_success():
    mock_client = MagicMock()
    mock_client.generate_screen.return_value = {"screen_id": "scr_123", "title": "Dashboard"}
    server = StitchMCPServer(client=mock_client)

    req = {
        "jsonrpc": "2.0",
        "id": 3,
        "method": "tools/call",
        "params": {
            "name": "generate_screen",
            "arguments": {"prompt": "Modern Dashboard", "device": "DESKTOP"}
        }
    }
    resp = server.handle_request(req)
    assert resp["result"]["isError"] is False
    content_text = resp["result"]["content"][0]["text"]
    assert "scr_123" in content_text
    mock_client.generate_screen.assert_called_once_with(prompt="Modern Dashboard", device="DESKTOP")


def test_mcp_tools_call_error_handling():
    mock_client = MagicMock()
    mock_client.get_screen.side_effect = Exception("Tela não encontrada na API Stitch")
    server = StitchMCPServer(client=mock_client)

    req = {
        "jsonrpc": "2.0",
        "id": 4,
        "method": "tools/call",
        "params": {
            "name": "get_screen",
            "arguments": {"screen_id": "invalid_id"}
        }
    }
    resp = server.handle_request(req)
    assert resp["result"]["isError"] is True
    assert "Tela não encontrada" in resp["result"]["content"][0]["text"]


def test_mcp_unknown_method():
    server = StitchMCPServer(client=MagicMock())
    req = {"jsonrpc": "2.0", "id": 5, "method": "non_existent_method"}
    resp = server.handle_request(req)
    assert "error" in resp
    assert resp["error"]["code"] == -32601
```
Teto do arquivo: <= 140 linhas.

---

## 🔍 Comandos de Verificação Local
```bash
# 1. Executar os novos testes dedicados do servidor MCP
pytest tests/test_stitch_mcp.py -v

# 2. Executar toda a suíte de testes do Stitch
pytest tests/test_stitch_mcp.py tests/test_stitch_integration.py -v

# 3. Executar toda a suíte pytest
pytest -q

# 4. Validar limites de linhas
python -m amb_cli.cli validate tests/test_stitch_mcp.py
```

---

## 📋 Definition of Done (DoD)
- [ ] Arquivo `tests/test_stitch_mcp.py` criado com 6+ testes unitários.
- [ ] 100% de aprovação em `pytest tests/test_stitch_mcp.py`.
- [ ] Arquivo `tests/test_stitch_integration.py` mantido intacto.
- [ ] Suíte global `pytest` continua 100% verde.
