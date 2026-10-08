# US-63: Saída JSON Estruturada em amb schema (--json)

## 📌 Contexto e Objetivo
O comando `amb schema [filtro]` inspeciona e cataloga arquivos de schema de banco de dados do projeto, exibindo tabelas, colunas, tipos e constraints.
Atualmente, a saída é renderizada apenas como texto/tabela formatada no terminal. Para agentes de IA, pipelines autônomos ou scripts de validação, consultar essas definições em formato JSON estruturado puro (`--json`) é essencial para análise programática sem ruído de formatação ANSI.

Esta US adiciona suporte a `--json`:
```bash
amb schema --json
# ou com filtro:
amb schema kanban --json
```

---

## 📐 Requisitos Técnicos

### 1. Atualização do Parser CLI
- **Arquivo (`amb_cli/cli_modules/cli_parsers.py`):**
  - No subparser `schema`:
    - Adicionar suporte a `--json`:
      ```python
      _j(p)  # Adiciona flag --json
      ```

### 2. Atualização do Leitor de Schema
- **Arquivo (`amb_cli/architecture/db_schema_reader.py`):**
  - Atualizar `show_schema(filter_term: Optional[str] = None, as_json: bool = False) -> None`:
    - Se `as_json`:
      - Montar dicionário com:
        ```json
        {
          "root": "...",
          "total_tables": len(filtered),
          "tables": filtered
        }
        ```
      - Imprimir via `json.dumps(..., indent=2, ensure_ascii=False)`.
      - Retornar sem imprimir banners textuais.
  - Manter o limite rígido de 300 linhas por arquivo (Regra 02).

### 3. Atualização do Handler
- **Arquivo (`amb_cli/cli_modules/cli_handlers.py`):**
  - No handler `cmd_schema(args: Any)`:
    - Repassar `as_json=getattr(args, "json", False)` para `show_schema`.

---

## 🧪 Critérios de Aceite
1. **Suíte de Testes Unitários:**
   - Criar `tests/test_schema_json_output.py` cobrindo:
     - Execução de `amb schema --json` gerando JSON válido contendo lista de tabelas e colunas.
     - Filtragem com `amb schema kanban --json` retornando apenas tabelas correlacionadas em JSON.
     - Preservação da formatação visual padrão no terminal quando `--json` não for informado.
2. **Qualidade de Código:**
   - 100% dos testes passando (`pytest -q`).
   - Teto rígido de 300 linhas por arquivo (Regra 02).
   - Tipagem estrita com `typing` (Regra 04).
