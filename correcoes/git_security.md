# 🛡️ Correção de Segurança: Remover shell=True em Comandos Git

Agente responsável por eliminar o risco de command injection nas chamadas de comandos Git no ecossistema amb_v2.

## 🎯 Missão Principal
Substituir todas as invocações de `subprocess.run` que executam comandos Git (`git checkout`, `git pull`, `git commit`, `git add`) com `shell=True`, alterando para `shell=False`.

## 📂 Arquivos Alvos
1. `integrations/jules/tools/merge_session_pr.py`
2. `agents/autonomous_loop.py`

## 📋 Regras de Implementação
1. **Em `integrations/jules/tools/merge_session_pr.py`:**
   - No bloco de commit do patch:
     - `subprocess.run(["git", "add", "."], cwd=repo_root, capture_output=True, shell=False)`
     - `subprocess.run(["git", "commit", "-m", commit_msg], cwd=repo_root, capture_output=True, shell=False)`
   - No bloco de sincronização (git pull):
     - `subprocess.run(["git", "checkout", target_branch], cwd=repo_root, capture_output=True, shell=False)`
     - `subprocess.run(["git", "pull", "origin", target_branch], cwd=repo_root, capture_output=True, text=True, encoding="utf-8", errors="replace", shell=False)`

2. **Em `agents/autonomous_loop.py`:**
   - Na função `_handle_pr_merge`:
     - `subprocess.run(["git", "pull", "origin", branch], cwd=repo_root, capture_output=True, shell=False)`

3. **Validação:**
   - Garantir que todos os argumentos continuam sendo passados como lista (`argv`).
   - Não alterar regras de negócio ou fluxo de execução das ferramentas.
