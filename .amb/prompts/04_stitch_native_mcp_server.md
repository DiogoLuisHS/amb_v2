# 🎯 Task: Expor o Google Stitch como Servidor MCP Nativo (`amb stitch mcp`)

## 📌 Contexto & Responsabilidade Única (SRP)
O Google Stitch possui suporte a Model Context Protocol (MCP), permitindo que agentes de código consumam suas ferramentas de design generativo diretamente pelo protocolo MCP (JSON-RPC sobre stdio).
Atualmente, o AMB expõe comandos de linha de comando (`amb stitch generate`, `refine`, etc.). Criar um subcomando `amb stitch mcp` que inicia um servidor MCP stdio oficial permitirá que ferramentas como **Antigravity, Cursor, Claude Code ou o próprio Jules** configurem o AMB no arquivo `mcp_config.json` e chamem o Stitch como um conjunto de ferramentas nativas.

Sua missão é criar o servidor MCP do Stitch em `amb_cli/integrations/stitch/stitch_core/mcp_server.py` e expô-lo via comando `amb stitch mcp`.

---

## 🛠️ Arquivos Alvo & Alterações Necessárias

### 1. Novo Módulo: `amb_cli/integrations/stitch/stitch_core/mcp_server.py`
- Crie a classe `StitchMCPServer`:
  - Implementa o protocolo MCP básico sobre `sys.stdin` e `sys.stdout` (JSON-RPC 2.0).
  - Responde aos métodos padrão do MCP:
    - `initialize`: Retorna capacidades do servidor e metadados (`name: "amb-stitch-mcp"`, `version: "1.0.0"`).
    - `tools/list`: Lista as ferramentas oficiais do Stitch (`generate_screen`, `refine_screen`, `get_screen`, `list_screens`, `sync_design_tokens`).
    - `tools/call`: Despacha a execução para as funções já existentes em `amb_cli/integrations/stitch/stitch_client.py`.
  - Tratamento de erros robusto com retorno no formato JSON-RPC de erro (`isError: true`).
  - Mantenha o arquivo estritamente <= 250 linhas.

### 2. Integrar na CLI do AMB
- `amb_cli/cli_modules/cli_parsers.py`:
  - Adicione o subcomando `mcp` em `stitch_parser` (`amb stitch mcp`).
- `amb_cli/cli_modules/handlers_core/stitch_handler.py`:
  - Adicione a rota para invocar `StitchMCPServer.run()` quando `args.stitch_command == "mcp"`.

### 3. Testes Unitários
- `tests/test_stitch_integration.py`:
  - Teste a inicialização do `StitchMCPServer` simulando requests JSON-RPC de `initialize` e `tools/list`.
  - Verifique que as chamadas a `tools/call` são roteadas corretamente para o cliente Stitch.
  - Garanta 100% de sucesso na suíte de testes.

---

## 📋 Critérios de Aceite (DoD)
1. `amb stitch mcp` inicia um loop stdio respondendo a mensagens JSON-RPC compatíveis com MCP.
2. Ferramentas essenciais (`generate_screen`, `get_screen`, `list_screens`) são expostas com schemas JSON válidos.
3. Arquivo modular com menos de 300 linhas.
4. Suíte `pytest` 100% verde.
