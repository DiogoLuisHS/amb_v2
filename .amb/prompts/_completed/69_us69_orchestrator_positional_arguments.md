# US-69: Argumento Posicional Direto e Inteligente em amb agent e amb pipeline

## 📌 Contexto e Objetivo
Atualmente, para disparar qualquer um dos dois grandes orquestradores do AMB_V2, o desenvolvedor é obrigado a memorizar e digitar flags prolixas:
- Em `amb agent`: exige `--role <nome>` ou `-p <pasta_ou_arquivo>`.
- Em `amb pipeline`: exige `-s <stitch.md> -j <jules.md>` ou `-f <arquivo_unificado.md>`.

Seguindo o princípio de usabilidade de alto nível:
1. **`amb agent <alvo>`:** Aceita o alvo diretamente como argumento posicional:
   - Se for o nome de uma persona existente (ex: `amb agent engineer`), despacha a persona.
   - Se for um arquivo ou pasta de prompts (ex: `amb agent .amb/prompts/`), executa o desenvolvimento em lote sequencial.
2. **`amb pipeline <arquivo_ou_ideia>`:** Aceita o arquivo de especificação como argumento posicional direto:
   - `amb pipeline specs/nova_tela.md`: lê o arquivo e auto-divide as seções de Design e Engenharia via `parse_single_prompt`.
   - Se for uma descrição informal (ex: `amb pipeline "Dashboard de Vendas"`), aciona a síntese antes do pipeline.
3. As flags explícitas (`-p`, `-r`, `-f`, `-s`, `-j`) continuam aceitas para scripts de automação.

---

## 📐 Requisitos Técnicos

### 1. Atualização do Parser CLI
- **Arquivo (`amb_cli/cli_modules/cli_parsers.py`):**
  - No subparser `agent`:
    - Adicionar argumento posicional `target`:
      ```python
      p.add_argument("target", nargs="?", help="Nome da persona (ex: engineer) OU caminho de pasta/arquivo de prompts (.amb/prompts/).")
      ```
    - Tornar `--role` e `--prompt` opcionais.
  - No subparser `pipeline`:
    - Adicionar argumento posicional `spec`:
      ```python
      p.add_argument("spec", nargs="?", help="Arquivo markdown com divisões de tela/código OU descrição visual da tarefa.")
      ```
    - Tornar `--stitch-prompt`, `--jules-prompt` e `--prompt-file` opcionais.

### 2. Atualização dos Handlers
- **Arquivo (`amb_cli/cli_modules/cli_handlers.py`):**
  - No handler `cmd_agent(args)`:
    - Se `args.target`:
      - Se apontar para um arquivo ou pasta existente (`os.path.exists(args.target)`): tratar como `prompt_file = args.target`.
      - Caso contrário: tratar como `args.role = args.target`.
  - No handler `cmd_pipeline(args)`:
    - Se `args.spec`:
      - Se for arquivo existente: tratar como `args.prompt_file = args.spec`.
      - Se for texto livre: tratar como `args.stitch_prompt = args.spec` e `args.jules_prompt = args.spec`.

---

## 🧪 Critérios de Aceite
1. **Suíte de Testes Unitários:**
   - Criar `tests/test_orchestrator_positional.py` cobrindo:
     - `amb agent engineer` executando a persona sem a flag `--role`.
     - `amb agent .amb/prompts/` detectando pasta e iniciando lote sem a flag `-p`.
     - `amb pipeline specs/login.md` iniciando o pipeline com arquivo posicional direto.
     - Preservação da execução passando flags explícitas.
2. **Qualidade de Código:**
   - 100% dos testes passando (`pytest -q`).
   - Teto rígido de 300 linhas por arquivo (Regra 02).
   - Tipagem estrita com `typing` (Regra 04).
