# 🎯 US-15: Despacho e Execução de Ferramentas `tools/call` no Stitch MCP

## 👤 User Story
> **Como** cliente MCP executando uma ação de geração de tela,  
> **Quero** enviar requisições `tools/call` para o servidor MCP do Stitch e receber o conteúdo retornado ou mensagem estruturada de erro,  
> **Para que** o AMB interaja com o StitchClient e retorne resultados sem quebrar a conexão JSON-RPC em caso de falha.

---

## 📌 Critérios de Aceitação BDD

* **Cenário 1: Despacho bem-sucedido de ferramenta (`generate_screen`)**
  * **Dado** que o cliente invocou `tools/call` para `generate_screen` com `{"prompt": "Login UI"}`;
  * **Quando** o `StitchClient` executar com sucesso;
  * **Então** a resposta deve conter `"isError": false` e `content: [{"type": "text", "text": "..."}]` contendo os dados da tela em JSON.

* **Cenário 2: Tratamento defensivo de exceções de API**
  * **Dado** que a chamada ao Stitch falhou por erro de rede ou chave inválida;
  * **Quando** o erro for capturado pelo servidor;
  * **Então** deve responder com `"isError": true` e mensagem de erro explicativa no `content`;
  * **E** o loop do servidor NÃO deve encerrar.

* **Cenário 3: Tentativa de invocar ferramenta desconhecida**
  * **Dado** uma chamada para ferramenta inexistente `tools/call` com nome `"ferramenta_inexistente"`;
  * **Quando** for processada;
  * **Então** deve responder com `"isError": true` informando que a ferramenta é desconhecida.

---

## 🛠️ Arquivos Alvo & Alterações Necessárias

### `amb_cli/integrations/stitch/stitch_core/mcp_server.py`
Adicionar o método privado `_dispatch_tool` e a rota `tools/call` no `handle_request`:
```python
        if method == "tools/call":
            tool_name = params.get("name")
            arguments = params.get("arguments", {})
            return self._dispatch_tool(msg_id, tool_name, arguments)
```
E implementar o despacho:
```python
    def _dispatch_tool(self, msg_id: Any, name: str, args: Dict[str, Any]) -> Dict[str, Any]:
        """Despacha a chamada para o método correspondente do StitchClient."""
        try:
            if name == "generate_screen":
                res = self.client.generate_screen(prompt=args.get("prompt"), device=args.get("device", "DESKTOP"))
            elif name == "refine_screen":
                res = self.client.edit_screen(screen_id=args.get("screen_id"), prompt=args.get("prompt"))
            elif name == "get_screen":
                res = self.client.get_screen(screen_id=args.get("screen_id"))
            elif name == "list_screens":
                res = self.client.list_screens()
            else:
                return {
                    "jsonrpc": "2.0",
                    "id": msg_id,
                    "result": {
                        "isError": True,
                        "content": [{"type": "text", "text": f"Ferramenta desconhecida: '{name}'"}]
                    }
                }

            return {
                "jsonrpc": "2.0",
                "id": msg_id,
                "result": {
                    "isError": False,
                    "content": [{"type": "text", "text": json.dumps(res, ensure_ascii=False)}]
                }
            }
        except Exception as exc:
            return {
                "jsonrpc": "2.0",
                "id": msg_id,
                "result": {
                    "isError": True,
                    "content": [{"type": "text", "text": f"Falha na execução de {name}: {str(exc)}"}]
                }
            }
```
Teto do arquivo: <= 220 linhas.

---

## 🔍 Comandos de Verificação Local
```bash
# Validar despacho de chamada de ferramenta com mock
python -c "from unittest.mock import MagicMock; from amb_cli.integrations.stitch.stitch_core.mcp_server import StitchMCPServer; m = MagicMock(); m.generate_screen.return_value = {'id': 'tela-1'}; s = StitchMCPServer(client=m); res = s.handle_request({'jsonrpc': '2.0', 'id': 1, 'method': 'tools/call', 'params': {'name': 'generate_screen', 'arguments': {'prompt': 'UI'}}}); print('Resultado:', res['result']['isError'] == False)"

# Garantir integridade da suíte pytest
pytest -q

# Validar conformidade de tamanho
python -m amb_cli.cli validate amb_cli/integrations/stitch/stitch_core/mcp_server.py
```

---

## 📋 Definition of Done (DoD)
- [ ] Método `_dispatch_tool` implementado e roteando para as 4 ferramentas do Stitch.
- [ ] Resposta com `isError: False` e payload serializado em JSON.
- [ ] Captura de exceções retornando `isError: True` sem interrupção do processo.
- [ ] Arquivo mantido abaixo de 220 linhas.
- [ ] Suíte global `pytest` continua 100% verde.
