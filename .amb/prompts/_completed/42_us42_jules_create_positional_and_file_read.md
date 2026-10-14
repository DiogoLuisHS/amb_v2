# US-42: Argumento Posicional e Auto-Leitura de Arquivo em amb jules create

## 📌 Contexto e Objetivo
Atualmente, o comando `amb jules create` exige a flag `--prompt` ou `-p` como obrigatória (`required=True`):
```bash
amb jules create -p "Refatorar componente de formulário"
```
Se o desenvolvedor passar o prompt diretamente como argumento posicional (`amb jules create "Refatorar componente"`), o parser falha com erro de argumento obrigatório ausente.
Além disso, ao apontar para um arquivo de prompt existente (ex: `.amb/prompts/01_tarefa.md`), o usuário precisa de ferramentas auxiliares (`cat` / `type`) ou usar scripts externos.

Esta US aprimora a ergonomia do comando:
1. **Argumento Posicional Direto:** Permite `amb jules create "Meu prompt"` ou `amb jules create caminho/prompt.md` sem exigir a flag `-p`.
2. **Auto-Leitura de Arquivo:** Se o valor informado apontar para um arquivo existente no sistema de arquivos, seu conteúdo é automaticamente lido com `encoding="utf-8", errors="replace"`.
3. **Auto-Inferência de Título:** Se `--title` não for fornecido e o prompt veio de um arquivo, infere o título automaticamente a partir da primeira linha `# H1` do markdown ou do nome do arquivo.
4. **Retrocompatibilidade:** A flag `--prompt` / `-p` continua funcionando normalmente.

---

## 📐 Requisitos Técnicos

### 1. Atualização do Parser CLI
- **Arquivo (`amb_cli/cli_modules/cli_parsers.py`):**
  - No subparser `create`:
    - Tornar `--prompt` (`-p`) opcional (`required=False`).
    - Adicionar argumento posicional `prompt_pos`:
      ```python
      j.add_argument("prompt_pos", nargs="?", help="Instruções da tarefa ou caminho do arquivo .md (opcional se informado via -p).")
      ```

### 2. Atualização do Handler
- **Arquivo (`amb_cli/cli_modules/handlers_core/jules_handler.py`):**
  - No bloco `sub == "create"`:
    - Resolver o prompt: `raw_prompt = getattr(args, "prompt_pos", None) or getattr(args, "prompt", None)`.
    - Se nenhum prompt for fornecido, exibir erro amigável via `log_error` e retornar.
    - Repassar `raw_prompt` para `run_create_session`.

### 3. Leitura Transparente e Inferência de Título
- **Arquivo (`amb_cli/integrations/jules/tools/create_session.py`):**
  - No início de `create_session`:
    - Verificar se `os.path.isfile(prompt)`:
      - Se verdadeiro, ler o conteúdo:
        ```python
        with open(prompt, "r", encoding="utf-8", errors="replace") as f:
            file_content = f.read()
        ```
      - Se `title` não foi informado:
        - Tentar extrair do cabeçalho `# Título` do arquivo.
        - Se não houver `#`, utilizar o nome base do arquivo limpo (ex: `01_tarefa.md` -> `01 Tarefa`).
      - Substituir `prompt = file_content`.
  - Manter o limite rígido de 300 linhas por arquivo (Regra 02).

---

## 🧪 Critérios de Aceite
1. **Suíte de Testes Unitários:**
   - Criar `tests/test_jules_create_positional.py` cobrindo:
     - Criação passando prompt direto posicional (`amb jules create "texto"`).
     - Criação passando caminho de arquivo `.md` existente com leitura automática do conteúdo.
     - Auto-inferência de título a partir do arquivo quando `--title` não é fornecido.
     - Preservação da retrocompatibilidade com `--prompt` / `-p`.
     - Tratamento gracioso quando nenhum prompt é fornecido.
2. **Qualidade de Código:**
   - 100% dos testes passando (`pytest -q`).
   - Teto rígido de 300 linhas por arquivo (Regra 02).
   - Tipagem estrita com `typing` (Regra 04).
