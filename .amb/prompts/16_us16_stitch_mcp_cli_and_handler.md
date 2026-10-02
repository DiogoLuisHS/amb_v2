# 🎯 US-16: Subcomando CLI `amb stitch mcp` e Roteamento de Execução

## 👤 User Story
> **Como** desenvolvedor configurando o AMB no arquivo `mcp_config.json` de uma IDE (Cursor, Jules ou Antigravity),  
> **Quero** poder executar o comando `amb stitch mcp` no terminal,  
> **Para que** o processo inicie o servidor MCP stdio e fique pronto para processar requisições das ferramentas de design.

---

## 📌 Critérios de Aceitação BDD

* **Cenário 1: Presença do subcomando `mcp` na ajuda de `amb stitch`**
  * **Dado** que o desenvolvedor executou `amb stitch --help`;
  * **Quando** a lista de subcomandos for exibida;
  * **Então** o subcomando `mcp` deve constar com a descrição indicando o servidor MCP stdio.

* **Cenário 2: Roteamento para `StitchMCPServer.run()`**
  * **Dado** a execução de `amb stitch mcp`;
  * **Quando** o handler for acionado com `args.stitch_cmd == "mcp"`;
  * **Então** deve instanciar `StitchMCPServer` e chamar o método `.run()`.

---

## 🛠️ Arquivos Alvo & Alterações Necessárias

### 1. `amb_cli/cli_modules/cli_parsers.py`
Localize a seção onde os subcomandos do Stitch são registrados (aproximadamente linha 130 a 160):
Adicione em apenas 1 linha:
```python
_sc(st_subs, "mcp", "Inicia o servidor MCP stdio nativo do Google Stitch para ferramentas de IA.")
```
> ⚠️ **ATENÇÃO:** Mantenha a adição concisa para não estourar o limite de `cli_parsers.py`.

### 2. `amb_cli/cli_modules/handlers_core/stitch_handler.py`
No bloco condicional de despacho dos subcomandos (`handle_cmd_stitch`):
Adicione o tratamento para `mcp`:
```python
    elif sub == "mcp":
        from integrations.stitch.stitch_core.mcp_server import StitchMCPServer
        server = StitchMCPServer(client=client)
        server.run()
        return
```
> ⚠️ **ATENÇÃO:** Mantenha `stitch_handler.py` abaixo de 160 linhas (atualmente tem 133 linhas).

---

## 🔍 Comandos de Verificação Local
```bash
# Validar help do subcomando na CLI
python -m amb_cli.cli stitch --help

# Validar conformidade de tamanho dos arquivos tocados
python -m amb_cli.cli validate amb_cli/cli_modules/cli_parsers.py
python -m amb_cli.cli validate amb_cli/cli_modules/handlers_core/stitch_handler.py

# Garantir integridade da suíte pytest
pytest -q
```

---

## 📋 Definition of Done (DoD)
- [ ] Subcomando `mcp` registrado no parser de `stitch`.
- [ ] Handler em `stitch_handler.py` instanciando e executando `StitchMCPServer().run()`.
- [ ] Nenhum arquivo ultrapassa 280 linhas.
- [ ] Suíte global `pytest` continua 100% verde.
