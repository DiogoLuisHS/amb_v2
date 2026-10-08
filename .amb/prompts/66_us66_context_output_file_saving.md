# US-66: Gravação Direta do Roteiro Arquitetural em Arquivo (amb context -o)

## 📌 Contexto e Objetivo
O comando `amb context <modulo>` gera um roteiro estruturado em markdown organizando os arquivos essenciais do módulo por camadas de dependência (DB ➔ Repositories ➔ Services ➔ Controllers ➔ UI).
Esse roteiro é ideal para alimentar o contexto de agentes autônomos, compor especificações técnicas ou registrar documentação de arquitetura.
Atualmente, o comando emite o texto apenas no stdout do terminal, exigindo que o usuário faça redirecionamento manual via shell.

Esta US adiciona a flag ergonômica de salvamento em arquivo:
```bash
amb context kanban -o docs/contexto_kanban.md
# ou para alimentar esteiras de agentes:
amb context billing -o .amb/prompts/billing_context.md
```

---

## 📐 Requisitos Técnicos

### 1. Atualização do Parser CLI
- **Arquivo (`amb_cli/cli_modules/cli_parsers.py`):**
  - No subparser `context`:
    - Adicionar a flag `--output` / `-o`:
      ```python
      p.add_argument("--output", "-o", help="Caminho do arquivo para salvar o roteiro markdown gerado.")
      ```

### 2. Atualização do Construtor de Contexto
- **Arquivo (`amb_cli/architecture/ai_context_builder.py`):**
  - Atualizar `generate_context(target: Optional[str] = None, output_json: bool = False, output_file: Optional[str] = None) -> None`:
    - Se `output_file`:
      - Assegurar que o diretório pai existe (`os.makedirs(os.path.dirname(output_file), exist_ok=True)` se houver pasta).
      - Gravar o conteúdo gerado (markdown ou JSON) no arquivo com `encoding="utf-8", errors="replace"`.
      - Exibir confirmação amigável via `print`: `✔ Roteiro arquitetural salvo com sucesso em: {output_file}`.
  - Manter o limite rígido de 300 linhas por arquivo (Regra 02).

### 3. Atualização do Handler
- **Arquivo (`amb_cli/cli_modules/cli_handlers.py`):**
  - No handler `cmd_context`:
    - Repassar `output_file=getattr(args, "output", None)` para `generate_context`.

---

## 🧪 Critérios de Aceite
1. **Suíte de Testes Unitários:**
   - Criar `tests/test_context_output_file.py` cobrindo:
     - Geração de roteiro markdown salvando diretamente em arquivo especificado via `-o`.
     - Gravação de saída JSON em arquivo quando `--json` e `-o` forem combinados.
     - Criação automática de diretórios pais ausentes durante a gravação.
     - Preservação da exibição padrão no terminal quando `-o` for omitido.
2. **Qualidade de Código:**
   - 100% dos testes passando (`pytest -q`).
   - Teto rígido de 300 linhas por arquivo (Regra 02).
   - Tipagem estrita com `typing` (Regra 04).
