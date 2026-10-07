# 🎯 US-14: Manifesto de Ferramentas Generativas `tools/list` no Stitch MCP

## 👤 User Story
> **Como** modelo de IA conectado ao servidor MCP do Stitch,  
> **Quero** receber a lista tipada de ferramentas via `tools/list`,  
> **Para que** eu conheça a assinatura e os parâmetros exatos para criar, refinar e ler telas visuais.

---

## 📌 Critérios de Aceitação BDD

* **Cenário 1: Resposta completa ao método `tools/list`**
  * **Dado** que o cliente MCP enviou `{"jsonrpc": "2.0", "id": 2, "method": "tools/list"}`;
  * **Quando** o servidor processar a mensagem;
  * **Então** a resposta deve conter a lista `tools` com 4 ferramentas: `generate_screen`, `refine_screen`, `get_screen` e `list_screens`.

* **Cenário 2: Validação dos JSON Schemas das ferramentas**
  * **Dado** o schema retornado para `generate_screen`;
  * **Quando** inspecionado;
  * **Então** deve exigir `prompt` (string obrigatória) e aceitar `device` (`MOBILE`, `DESKTOP`, `TABLET`).
  * **E** para `refine_screen` deve exigir `screen_id` e `prompt`.
  * **E** para `get_screen` deve exigir `screen_id`.

---

## 🛠️ Arquivos Alvo & Alterações Necessárias

### `amb_cli/integrations/stitch/stitch_core/mcp_server.py`
Adicionar o método auxiliar `get_tools_manifest(self) -> list` e o tratamento de `tools/list` no `handle_request`:
```python
    def get_tools_manifest(self) -> list:
        """Retorna o manifesto de ferramentas compatível com a especificação MCP."""
        return [
            {
                "name": "generate_screen",
                "description": "Gera uma nova tela visual completa no Stitch a partir de uma descrição textual.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "prompt": {"type": "string", "description": "Descrição detalhada do visual e componentes da tela."},
                        "device": {"type": "string", "enum": ["MOBILE", "DESKTOP", "TABLET"], "default": "DESKTOP"}
                    },
                    "required": ["prompt"]
                }
            },
            {
                "name": "refine_screen",
                "description": "Refina e altera uma tela visual existente no Stitch.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "screen_id": {"type": "string", "description": "ID da tela no Stitch a ser modificada."},
                        "prompt": {"type": "string", "description": "Instruções de modificação visual."}
                    },
                    "required": ["screen_id", "prompt"]
                }
            },
            {
                "name": "get_screen",
                "description": "Obtém o DOM HTML, CSS e metadados de uma tela existente no Stitch.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "screen_id": {"type": "string", "description": "ID da tela a exportar."}
                    },
                    "required": ["screen_id"]
                }
            },
            {
                "name": "list_screens",
                "description": "Lista todas as telas criadas no projeto Stitch ativo.",
                "inputSchema": {"type": "object", "properties": {}}
            }
        ]
```
E no `handle_request`:
```python
        if method == "tools/list":
            return {
                "jsonrpc": "2.0",
                "id": msg_id,
                "result": {"tools": self.get_tools_manifest()}
            }
```
Teto do arquivo: <= 160 linhas.

---

## 🔍 Comandos de Verificação Local
```bash
# Validar listagem de ferramentas via JSON-RPC
python -c "from amb_cli.integrations.stitch.stitch_core.mcp_server import StitchMCPServer; s = StitchMCPServer(); res = s.handle_request({'jsonrpc': '2.0', 'id': 1, 'method': 'tools/list'}); print('Tools encontradas:', len(res['result']['tools']))"

# Garantir integridade da suíte pytest
pytest -q

# Validar conformidade de tamanho
python -m amb_cli.cli validate amb_cli/integrations/stitch/stitch_core/mcp_server.py
```

---

## 📋 Definition of Done (DoD)
- [ ] Método `get_tools_manifest` implementado com as 4 ferramentas do Stitch.
- [ ] Resposta ao método `tools/list` implementada no `handle_request`.
- [ ] Schemas JSON estritos com tipagem correta.
- [ ] Arquivo mantido abaixo de 160 linhas.
- [ ] Suíte global `pytest` continua 100% verde.
