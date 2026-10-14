# US-49: Padronização de screen_id e Instruções Posicionais em amb stitch get e refine

## 📌 Contexto e Objetivo
Atualmente, as ações `amb stitch get` e `amb stitch refine` exigem a flag obrigatória `--screen-id` ou `-s`:
```bash
amb stitch get -s SCREEN_123
amb stitch refine -s SCREEN_123 -p "Ajustar contraste dos botões"
```
Essa sintaxe destoa do restante da CLI (onde `amb jules get <id>`, `amb git pr get <id>`, etc. usam argumentos posicionais limpos).

Esta US padroniza a sintaxe limpa e moderna:
```bash
amb stitch get SCREEN_123
amb stitch refine SCREEN_123 "Ajustar contraste dos botões"
```

---

## 📐 Requisitos Técnicos

### 1. Atualização do Parser CLI
- **Arquivo (`amb_cli/cli_modules/cli_parsers.py`):**
  - No subparser `get`:
    - Adicionar argumento posicional `screen_id` (`nargs="?"`):
      ```python
      s.add_argument("screen_id", nargs="?", help="ID da tela no Stitch.")
      s.add_argument("--screen-id", "-s", dest="screen_id_flag", help="Flag alternativa para ID da tela.")
      ```
  - No subparser `refine`:
    - Adicionar argumentos posicionais `screen_id` e `prompt`:
      ```python
      s.add_argument("screen_id", nargs="?", help="ID da tela a ser refinada.")
      s.add_argument("prompt", nargs="?", help="Instruções de edição e refinamento visual.")
      s.add_argument("--screen-id", "-s", dest="screen_id_flag", help="Flag alternativa para ID da tela.")
      s.add_argument("--prompt", "-p", dest="prompt_flag", help="Flag alternativa para instruções.")
      ```

### 2. Atualização do Handler
- **Arquivo (`amb_cli/cli_modules/handlers_core/stitch_handler.py`):**
  - No bloco `sub == "get"`:
    - Resolver: `sid = getattr(args, "screen_id", None) or getattr(args, "screen_id_flag", None)`.
    - Se `not sid`: log de erro amigável e retorno.
  - No bloco `sub == "refine"`:
    - Resolver: `sid = getattr(args, "screen_id", None) or getattr(args, "screen_id_flag", None)`.
    - Resolver: `prompt_text = _resolve_prompt(getattr(args, "prompt", None) or getattr(args, "prompt_flag", None))`.
    - Se `not sid` ou `not prompt_text`: log de erro amigável e retorno.

---

## 🧪 Critérios de Aceite
1. **Suíte de Testes Unitários:**
   - Criar `tests/test_stitch_positional_ids.py` cobrindo:
     - `amb stitch get <id>` com ID passado diretamente posicional.
     - `amb stitch refine <id> "<prompt>"` com ambos os argumentos posicionais.
     - Validação de mensagens amigáveis caso argumentos obrigatórios sejam omitidos.
2. **Qualidade de Código:**
   - 100% dos testes passando (`pytest -q`).
   - Teto rígido de 300 linhas por arquivo (Regra 02).
   - Tipagem estrita com `typing` (Regra 04).
