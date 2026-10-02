# 🎯 US-21: Expor Flags `--live` e `--uri` no Comando `amb schema`

## 👤 User Story
> **Como** desenvolvedor utilizando a CLI do AMB_V2,  
> **Quero** poder executar `amb schema --live` (ou `amb schema -l [tabela]`),  
> **Para que** eu possa alternar com facilidade entre a inspeção estática de schemas em código e a inspeção dinâmica de bancos ativos.

---

## 📌 Critérios de Aceitação BDD

* **Cenário 1: Presença das flags `--live` e `--uri` no help de `amb schema`**
  * **Dado** que o desenvolvedor executou `amb schema --help`;
  * **Quando** o parser exibir as opções;
  * **Então** as flags `--live` (`-l`) e `--uri` devem estar documentadas.

* **Cenário 2: Roteamento para `reader.inspect_live` quando `--live` está ativo**
  * **Dado** a execução de `amb schema --live`;
  * **Quando** o handler for executado;
  * **Então** deve chamar `reader.inspect_live(...)` e exibir o resultado no terminal.

---

## 🛠️ Arquivos Alvo & Alterações Necessárias

### 1. `amb_cli/cli_modules/cli_parsers.py`
Localize o parser do comando `schema` (aproximadamente linha 205):
```python
p = _c("schema", "Inspeciona tabelas e colunas de schemas do banco de dados (Read-Only).", cmd_schema, ["db"])
p.add_argument("target", nargs="?", default=None, help="Nome da tabela ou módulo a filtrar (ex: kanban, agenda, projects).")
# Adicionar as novas flags:
p.add_argument("--live", "-l", action="store_true", help="Inspeciona banco de dados ativo em tempo de execução (Read-Only).")
p.add_argument("--uri", help="Caminho ou URI explícita de conexão.")
```
> ⚠️ **ATENÇÃO:** Mantenha a adição em apenas 2 linhas concisas.

### 2. Handler do comando (`amb_cli/cli_modules/cli_handlers.py` ou `handlers_core/schema_handler.py`)
No handler que executa `cmd_schema`:
```python
if getattr(args, "live", False):
    res = reader.inspect_live(target_table=getattr(args, "target", None), explicit_path=getattr(args, "uri", None))
    # Exibir resultado formatado
    return
```

---

## 🔍 Comandos de Verificação Local
```bash
# Validar help do comando na CLI
python -m amb_cli.cli schema --help

# Validar conformidade de tamanho de cli_parsers.py (<= 300 linhas)
python -m amb_cli.cli validate amb_cli/cli_modules/cli_parsers.py

# Garantir integridade da suíte pytest
pytest -q
```

---

## 📋 Definition of Done (DoD)
- [ ] Flags `--live` (`-l`) e `--uri` registradas no parser de `schema`.
- [ ] Roteamento para `reader.inspect_live` no handler.
- [ ] `amb schema --help` exibe as opções corretamente.
- [ ] Arquivo `cli_parsers.py` mantido abaixo de 275 linhas.
- [ ] Suíte global `pytest` continua 100% verde.
