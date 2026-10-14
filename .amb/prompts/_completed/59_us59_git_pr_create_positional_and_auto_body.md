# US-59: Argumento Posicional e Auto-Body em amb git pr create

## 📌 Contexto e Objetivo
Atualmente, no comando `amb git pr create`, a flag `--title` / `-t` é obrigatória (`required=True`):
```bash
amb git pr create -t "feat: autenticação JWT"
```
Se o desenvolvedor não fornecer a descrição com `--body`, o Pull Request é aberto sem corpo, deixando os revisores sem contexto sobre o que foi implementado.

Esta US adota uma abordagem moderna e ergonômica:
1. **Título Posicional Direto:** Permite `amb git pr create "feat: autenticação JWT"` sem exigir `-t`.
2. **Auto-Geração de Corpo (Auto-Body):** Se `--body` não for informado, inspeciona os commits da branch atual em relação à branch base (`git log --oneline base..HEAD`) e auto-gera um sumário com a lista de commits e alterações da branch.
3. **Preservação:** A flag `--title` (`-t`) continua aceita caso fornecida.

---

## 📐 Requisitos Técnicos

### 1. Atualização do Parser CLI
- **Arquivo (`amb_cli/cli_modules/cli_parsers.py`):**
  - No subparser `create` de PR:
    - Adicionar argumento posicional `title`:
      ```python
      pr.add_argument("title", nargs="?", help="Título do Pull Request (opcional se fornecido via -t).")
      ```
    - Tornar `--title` (`-t`) opcional (`required=False`).

### 2. Atualização do PR Manager
- **Arquivo (`amb_cli/integrations/git/tools/pr_manager.py`):**
  - Na função de criação de PR:
    - Resolver título: `resolved_title = kwargs.get("title") or getattr(args, "title_pos", None)`.
    - Se nenhum título for fornecido, extrair a mensagem do commit mais recente (`git log -1 --pretty=%B`).
    - Se `body` for vazio ou não fornecido:
      - Obter commits da branch:
        ```bash
        git log --oneline {base_branch}..HEAD
        ```
      - Estruturar o corpo markdown:
        ```markdown
        ### 📋 Resumo das Alterações
        Pull Request gerado automaticamente pelo AMB_V2.

        ### 📦 Commits Integrados:
        - {commit_1}
        - {commit_2}
        ```
  - Manter o limite rígido de 300 linhas por arquivo (Regra 02).

---

## 🧪 Critérios de Aceite
1. **Suíte de Testes Unitários:**
   - Criar `tests/test_git_pr_create_positional.py` cobrindo:
     - Criação de PR passando o título diretamente como argumento posicional.
     - Auto-geração do corpo do PR com base no log de commits quando `--body` for omitido.
     - Preservação da flag explícita `--title` e do `--body` customizado quando fornecidos.
     - Tratamento gracioso caso não seja possível determinar o título.
2. **Qualidade de Código:**
   - 100% dos testes passando (`pytest -q`).
   - Teto rígido de 300 linhas por arquivo (Regra 02).
   - Tipagem estrita com `typing` (Regra 04).
