# US-14: Simplificação de Usabilidade do Jules (amb jules delete) e Concorrência de Lote (amb agent --concurrency)

## 📌 Contexto e Objetivo
Simplificar a usabilidade e a arquitetura de execução do Google Jules no ecossistema AMB_V2 em dois aspectos complementares:
1. **Comando Direto de Deleção (`amb jules delete <session_id>`):** Substituir a necessidade de comandos longos (`amb jules clean --id <id>`) por um comando direto de primeira classe, com argumento posicional, confirmação rápida (`--force` para bypass) e tratamento resiliente de HTTP 404 (sessão já inexistente).
2. **Execução Concorrente em Lote (`amb agent --concurrency <N>`):** Permitir que lotes de prompts/issues sejam despachados para o Jules com paralelismo controlado (mantendo até N sessões ativas em paralelo na nuvem), acelerando tarefas em lote enquanto preserva a integridade do Git com merge sequencial sem colisões de branch.

---

## 📐 Requisitos Técnicos

### 1. Comando Direto `amb jules delete`
- **Parser (`cli_parsers.py`):**
  - Adicionar comando `delete` (aliases: `del`, `rm`) no subparser `amb jules`.
  - Argumento posicional obrigatório: `session_id` (aceita ID ou URL da sessão).
  - Flag opcional: `--force`, `-f` (não pede confirmação interativa).
- **Handler (`jules_handler.py`):**
  - Invocar `JulesClient.delete_session(session_id)`.
  - Tratar status HTTP 404 de forma amigável: se a sessão já foi excluída, exibir aviso sem lançar stacktrace.
  - Exibir confirmação clara no terminal: `✔ Sessão <id> excluída com sucesso da nuvem Jules.`

### 2. Execução Concorrente no Loop Autônomo
- **Módulo Atômico (`amb_cli/agents/loop_core/concurrent_runner.py`):**
  - Criar o runner atômico para manter `autonomous_loop.py` e outros arquivos abaixo do teto de 300 linhas (Regra 02).
  - Classe `ConcurrentLoopRunner`:
    - Recebe a lista de tarefas/issues, limite de concorrência `max_concurrency: int`, cliente Jules e branch alvo.
    - Utiliza `ThreadPoolExecutor` ou fila de controle para manter até `max_concurrency` sessões ativas no Jules.
    - Conforme cada sessão atinge `COMPLETED`, enfileira o PR para o fluxo sequencial de merge seguro (`handle_pr_merge`) com auto-teste de integridade e fechamento de issue.
- **CLI (`amb agent`):**
  - Adicionar a flag `--concurrency`, `-c` (padrão: 1, inteiro >= 1) no `amb agent`.
  - Se `concurrency == 1`: mantém o fluxo sequencial padrão existente (100% retrocompatível).
  - Se `concurrency > 1`: delega para `ConcurrentLoopRunner`.

---

## 🧪 Critérios de Aceite
1. **Suíte de Testes:**
   - Criar `tests/test_jules_delete.py` e `tests/test_concurrent_runner.py` cobrindo:
     - Deleção bem-sucedida de sessão via CLI.
     - Tratamento gracioso de erro 404 (sessão não encontrada).
     - Execução concorrente de tarefas com merge ordenado e sem conflitos.
2. **Qualidade de Código e Limites Arquiteturais:**
   - 100% dos testes unitários passando (`pytest -q`).
   - **Teto rígido de 300 linhas por arquivo (Regra 02):** Todos os arquivos criados ou modificados (inclusive `cli_parsers.py`, modularizando se necessário) devem ter rigorosamente menos de 300 linhas.
   - Tipagem estrita com `typing` (Regra 04).
