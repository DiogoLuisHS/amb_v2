# ⚙️ Correção de Segurança: Executor Seguro de QA com Resolução de Executáveis

Agente responsável por tornar a execução dos comandos de validação de QA segura contra injeções e 100% compatível com sistemas Windows e Unix.

## 🎯 Missão Principal
Substituir a invocação ingênua com `shell=True` dentro da função interna `_run_qa_cmd`, resolvendo o executável/script de forma segura via `shutil.which` para permitir a execução com `shell=False` sem causar `FileNotFoundError` no Windows ao rodar scripts como `npm`, `yarn` ou `npx`.

## 📂 Arquivos Alvos
1. `integrations/jules/tools/merge_session_pr.py`
2. `pipeline/pipeline.py`

## 📋 Regras de Implementação
1. **Importação:**
   - Garantir importação de `shutil` e `shlex`.

2. **Na função `_run_qa_cmd(cmd_str: str, label: str)`:**
   - Realizar o parse seguro dos comandos usando `shlex.split(cmd_str, posix=False if sys.platform == "win32" else True)`.
   - Localizar o binário real com `resolved_bin = shutil.which(parts[0])`.
   - Se `resolved_bin` for localizado:
     - `parts[0] = resolved_bin`
     - Invocar `subprocess.run(parts, cwd=repo_root, capture_output=True, text=True, encoding="utf-8", errors="replace", shell=False)`.
   - Se `resolved_bin` não for localizado (comando embutido do shell ou caminho relativo específico):
     - Usar fallback controlado informando o log.

3. **Validação:**
   - Comandos como `npm run typecheck`, `python -m py_compile` devem continuar executando perfeitamente em ambiente Windows.
