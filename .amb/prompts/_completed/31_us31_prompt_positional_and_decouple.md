# US-31: Argumento Posicional Natural e Desacoplamento de Setup em amb prompt

## 📌 Contexto e Objetivo
Atualmente, o comando `amb prompt` possui uma duplicidade semântica:
1. Quando invocado sem argumentos, imprime o texto fixo do *Prompt Mestre de Auto-Configuração de Projeto* (`print_setup_prompt()`), duplicando a funcionalidade de `amb setup --prompt`.
2. Para sintetizar uma funcionalidade de software com IA, o usuário é obrigado a passar a flag prolixa `--synthesize` (ou `-s`):
   ```bash
   amb prompt --synthesize "Criar dashboard de métricas"
   ```
Se o usuário tentar executar a sintaxe natural `amb prompt "Criar dashboard de métricas"`, o CLI falha ou ignora a string posicional.

Esta US desacopla o texto estático de setup do comando `amb prompt` (mantendo-o exclusivamente em `amb setup --prompt`) e habilita argumento posicional direto para a ideia em `amb prompt`, proporcionando uma experiência de uso muito mais fluida e intuitiva.

---

## 📐 Requisitos Técnicos

### 1. Declaração do Argumento no CLI Parser
- **Arquivo (`amb_cli/cli_modules/cli_parsers.py`):**
  - No subparser `prompt`:
    - Adicionar argumento posicional opcional:
      ```python
      p.add_argument("idea", nargs="?", help="Ideia informal a ser estruturada e sintetizada em prompt com IA.")
      ```
    - Preservar a flag `--synthesize` (`-s`) para total retrocompatibilidade.
    - Manter o limite rígido de 300 linhas por arquivo (Regra 02).

### 2. Tratamento no Handler de Execução
- **Arquivo (`amb_cli/cli_modules/cli_handlers.py`):**
  - No método `cmd_prompt`:
    - Resolver a ideia prioritariamente: `idea = getattr(args, "idea", None) or getattr(args, "synthesize", None)`.
    - Se `idea` for fornecida (ou se houver imagem via `--image`):
      - Disparar a síntese cognitiva.
    - Se nenhuma ideia ou imagem for passada e o terminal for interativo (`sys.stdin.isatty()`):
      - Solicitar via input interativo: `Qual funcionalidade ou ideia deseja sintetizar em prompt? > `
    - Se não for interativo e não houver argumentos:
      - Exibir instruções amigáveis de uso do `amb prompt` com exemplos práticos.
    - Remover a importação e invocação de `print_setup_prompt()` dentro de `cmd_prompt`.

---

## 🧪 Critérios de Aceite
1. **Suíte de Testes Unitários:**
   - Criar `tests/test_prompt_positional.py` cobrindo:
     - Invocação de `cmd_prompt` com argumento posicional `args.idea = "Minha Feature"`.
     - Invocação retrocompatível com `args.synthesize = "Minha Feature"`.
     - Verificação de que `print_setup_prompt` não é mais chamado por `cmd_prompt`.
     - Invocação com flag `--image`.
2. **Qualidade de Código e Limites Arquiteturais:**
   - 100% dos testes unitários passando (`pytest -q`).
   - Teto rígido de 300 linhas por arquivo (Regra 02).
   - Tipagem estrita com `typing` (Regra 04).
