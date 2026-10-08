# US-47: Comportamento Padrão de Listagem de Telas em amb stitch

## 📌 Contexto e Objetivo
Atualmente, quando o desenvolvedor executa `amb stitch` no terminal sem subcomandos, o sistema exibe uma mensagem de erro:
```
Subcomando do Stitch inválido. Use 'amb stitch --help'.
```
Seguindo o princípio de design moderno e direto (sem amarras legadas), a execução de `amb stitch` deve imediatamente listar todas as telas do projeto Stitch ativo (`list`), formatando títulos, IDs, dimensões e descrições no terminal.

---

## 📐 Requisitos Técnicos

### 1. Atualização do Handler Central do Stitch
- **Arquivo (`amb_cli/cli_modules/handlers_core/stitch_handler.py`):**
  - No início de `handle_cmd_stitch(args: Any)`:
    - Se `sub is None` ou `not sub`:
      - Tratar automaticamente como `list`:
        ```python
        sub = "list"
        ```
  - Executar a consulta `client.list_screens(project_id=getattr(args, "project_id", None))` e renderizar o quadro formatado de telas.
  - Suportar a flag `--json` mesmo na invocação direta de `amb stitch --json`.

---

## 🧪 Critérios de Aceite
1. **Suíte de Testes Unitários:**
   - Criar `tests/test_stitch_default_list.py` cobrindo:
     - Execução de `handle_cmd_stitch` com `args.stitch_cmd = None` listando as telas do projeto.
     - Saída formatada no terminal com IDs e títulos.
     - Suporte a saída JSON pura quando `args.json = True`.
2. **Qualidade de Código:**
   - 100% dos testes passando (`pytest -q`).
   - Teto rígido de 300 linhas por arquivo (Regra 02).
   - Tipagem estrita com `typing` (Regra 04).
