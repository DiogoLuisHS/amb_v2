# 🎯 US-13: Loop Stdio JSON-RPC 2.0 e Handshake de Inicialização no Stitch MCP

## 👤 User Story
> **Como** cliente MCP (Antigravity, Jules, Cursor ou Claude Code),  
> **Quero** iniciar o servidor MCP do Stitch e executar o handshake `initialize` via stdio,  
> **Para que** a sessão seja estabelecida e declare as capacidades do servidor em conformidade com o protocolo.

---

## 📌 Critérios de Aceitação BDD

* **Cenário 1: Resposta ao método `initialize`**
  * **Dado** que o servidor MCP está aguardando conexões no `sys.stdin`;
  * **Quando** receber uma linha com o JSON `{"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}}`;
  * **Então** deve escrever no `sys.stdout` uma linha com `protocolVersion: "2024-11-05"`, `capabilities: {"tools": {}}` e `serverInfo: {"name": "amb-stitch-mcp", "version": "1.0.0"}`;
  * **E** deve fazer flush imediato do `stdout`.

* **Cenário 2: Tratamento de `notifications/initialized`**
  * **Dado** a notificação `{"jsonrpc": "2.0", "method": "notifications/initialized"}`;
  * **Quando** o servidor processar a linha;
  * **Então** não deve escrever nada no `stdout` nem disparar erro de método desconhecido.

* **Cenário 3: Higiene de Stdio (Logs em stderr)**
  * **Dado** qualquer mensagem de erro ou diagnóstico de execução;
  * **Quando** for emitida;
  * **Então** deve ser gravada estritamente em `sys.stderr`, mantendo o `sys.stdout` 100% puro para mensagens JSON-RPC.

---

## 🛠️ Arquivos Alvo & Alterações Necessárias

### Criar Novo Arquivo: `amb_cli/integrations/stitch/stitch_core/mcp_server.py`
```python
# -*- coding: utf-8 -*-
"""Servidor MCP baseado em stdio para as ferramentas do Google Stitch."""

import sys
import json
from typing import Dict, Any, Optional
from integrations.stitch.stitch_client import StitchClient


class StitchMCPServer:
    """Implementa o protocolo Model Context Protocol sobre stdio para o Google Stitch."""

    def __init__(self, client: Optional[StitchClient] = None):
        self.client = client or StitchClient()

    def handle_request(self, req: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        msg_id = req.get("id")
        method = req.get("method")
        params = req.get("params", {})

        if method == "initialize":
            return {
                "jsonrpc": "2.0",
                "id": msg_id,
                "result": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {"tools": {}},
                    "serverInfo": {"name": "amb-stitch-mcp", "version": "1.0.0"}
                }
            }
        if method == "notifications/initialized":
            return None

        return {
            "jsonrpc": "2.0",
            "id": msg_id,
            "error": {"code": -32601, "message": f"Método ainda não implementado: {method}"}
        }

    def run(self):
        """Loop contínuo de leitura de mensagens JSON-RPC no stdin."""
        for line in sys.stdin:
            line = line.strip()
            if not line:
                continue
            try:
                req = json.loads(line)
                resp = self.handle_request(req)
                if resp is not None:
                    sys.stdout.write(json.dumps(resp, ensure_ascii=False) + "\n")
                    sys.stdout.flush()
            except Exception as e:
                print(f"[amb-stitch-mcp error] {e}", file=sys.stderr)
```
Teto do arquivo: <= 120 linhas.

---

## 🔍 Comandos de Verificação Local
```bash
# Validar resposta do handshake simulando stdin
python -c "import json, subprocess; p = subprocess.Popen(['python', '-c', 'from amb_cli.integrations.stitch.stitch_core.mcp_server import StitchMCPServer; StitchMCPServer().run()'], stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True); out, _ = p.communicate(json.dumps({'jsonrpc': '2.0', 'id': 1, 'method': 'initialize'}) + '\n'); print('Resposta:', out)"

# Garantir integridade da suíte pytest
pytest -q

# Validar conformidade de tamanho
python -m amb_cli.cli validate amb_cli/integrations/stitch/stitch_core/mcp_server.py
```

---

## 📋 Definition of Done (DoD)
- [ ] Arquivo `amb_cli/integrations/stitch/stitch_core/mcp_server.py` criado.
- [ ] Handshake `initialize` e `notifications/initialized` respondendo com sucesso.
- [ ] Redirecionamento estrito de erros para `sys.stderr`.
- [ ] Arquivo com menos de 100 linhas.
- [ ] Suíte global `pytest` continua 100% verde.
