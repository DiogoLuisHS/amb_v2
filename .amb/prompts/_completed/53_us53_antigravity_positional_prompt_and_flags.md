# US-53: Argumento Posicional Direto e Harmonização de Flags em amb agy prompt

## 📌 Contexto e Objetivo
Atualmente, no comando `amb agy prompt`, a especificação da ideia exige a flag obrigatória `--idea` ou `-i`:
```bash
amb agy prompt -i "Refatorar modal de login"
```
Além de obrigar o uso da flag para o propósito primário do comando, existe uma incoerência na CLI: enquanto `amb prompt` usa `-i` para imagens/mockups (`--image`), `amb agy prompt` usava `-i` para texto (`--idea`) e `-m` para imagem.

Seguindo o princípio de design moderno e limpo:
1. **Argumento Posicional Direto:** Permite `amb agy prompt "Refatorar modal de login"` ou `amb agy prompt ideia.md` sem exigir `-i`.
2. **Harmonização de Imagem/Mockup:** Padroniza a flag de mockup visual para `--image` / `-m` (com alias `--mockup`).
3. **Auto-Leitura de Arquivo:** Se o argumento posicional apontar para um arquivo existente, lê seu conteúdo automaticamente com `utf-8`.

---

## 📐 Requisitos Técnicos

### 1. Atualização do Parser CLI
- **Arquivo (`amb_cli/cli_modules/cli_parsers.py`):**
  - No subparser `prompt` do Antigravity (`agy`):
    - Adicionar argumento posicional `idea`:
      ```python
      a.add_argument("idea", nargs="?", help="Ideia informal ou caminho de arquivo de especificação a sintetizar.")
      ```
    - Manter `--idea` (`-i`) opcional para retrocompatibilidade de scripts.
    - Padronizar `--image` (`-m`, `--mockup`) para anexar imagens.

### 2. Atualização do Handler
- **Arquivo (`amb_cli/cli_modules/handlers_core/antigravity_handler.py`):**
  - No bloco `sub in ["prompt", "synthesize", "synth"]`:
    - Resolver ideia:
      ```python
      raw_idea = getattr(args, "idea", None) or getattr(args, "idea_flag", None)
      if raw_idea and os.path.isfile(raw_idea):
          with open(raw_idea, "r", encoding="utf-8", errors="replace") as f:
              raw_idea = f.read().strip()
      ```
    - Se nenhum texto de ideia for fornecido, exibir erro amigável via `log_error` e retornar.
    - Repassar para `run_synthesize_prompt`.

---

## 🧪 Critérios de Aceite
1. **Suíte de Testes Unitários:**
   - Criar `tests/test_antigravity_prompt_positional.py` cobrindo:
     - Síntese com argumento posicional direto de string.
     - Síntese passando caminho de arquivo `.md` existente com leitura automática.
     - Funcionamento da flag harmonizada de imagem/mockup (`--image` / `-m`).
     - Tratamento gracioso quando nenhum texto de ideia é fornecido.
2. **Qualidade de Código:**
   - 100% dos testes passando (`pytest -q`).
   - Teto rígido de 300 linhas por arquivo (Regra 02).
   - Tipagem estrita com `typing` (Regra 04).
