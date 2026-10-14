# US-48: Argumento Posicional Direto e Auto-Leitura de Arquivo em amb stitch generate

## 📌 Contexto e Objetivo
Atualmente, `amb stitch generate` exige a flag `--prompt` ou `-p` como obrigatória (`required=True`):
```bash
amb stitch generate -p "Dashboard Dark Mode com cards de KPI"
```
Para máxima fluidez e ergonomia (sem amarras legadas), o comando deve aceitar o prompt como argumento posicional direto:
```bash
amb stitch generate "Dashboard Dark Mode com cards de KPI"
# ou apontando para arquivo:
amb stitch generate specs/dashboard_ui.md
```
Se o argumento for um arquivo existente no disco, seu conteúdo é automaticamente lido com `utf-8`.

---

## 📐 Requisitos Técnicos

### 1. Atualização do Parser CLI
- **Arquivo (`amb_cli/cli_modules/cli_parsers.py`):**
  - No subparser `generate` do Stitch:
    - Adicionar argumento posicional direto `prompt`:
      ```python
      s.add_argument("prompt", nargs="?", help="Descrição visual da tela ou caminho de arquivo markdown com especificações.")
      ```
    - Manter `--prompt` (`-p`) opcional para scripts automatizados.

### 2. Atualização do Handler
- **Arquivo (`amb_cli/cli_modules/handlers_core/stitch_handler.py`):**
  - No bloco `sub == "generate"`:
    - Resolver o texto:
      ```python
      raw_prompt = getattr(args, "prompt", None) or getattr(args, "prompt_flag", None)
      ```
    - Se `not raw_prompt`:
      - Exibir mensagem amigável via `log_error` e retornar.
    - Se `os.path.isfile(raw_prompt)`:
      - Ler o conteúdo usando `encoding="utf-8", errors="replace"`.
    - Repassar o texto resolvido para `client.generate_screen`.

---

## 🧪 Critérios de Aceite
1. **Suíte de Testes Unitários:**
   - Criar `tests/test_stitch_generate_positional.py` cobrindo:
     - Geração passando string descritiva diretamente no argumento posicional.
     - Geração passando caminho de arquivo `.md` existente com leitura automática do conteúdo.
     - Tratamento gracioso quando nenhum prompt for fornecido.
2. **Qualidade de Código:**
   - 100% dos testes passando (`pytest -q`).
   - Teto rígido de 300 linhas por arquivo (Regra 02).
   - Tipagem estrita com `typing` (Regra 04).
