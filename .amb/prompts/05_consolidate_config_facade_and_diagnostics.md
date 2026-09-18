# 🎯 Task: Consolidar a Camada Facade em `amb_cli/config/` e Ajustar Diagnósticos

## 📌 Contexto & Responsabilidade Única (SRP)
Com a extração do núcleo do AMB para `amb_cli/core/` e do contexto do projeto consumidor para `amb_cli/workspace/`, a pasta `amb_cli/config/` passa a ter um papel unificado e de alto nível: ser a **Fachada de Compatibilidade Reversa (Facade)** e ponto central de diagnóstico do ambiente (`amb check`).

---

## 🛠️ Arquivos Alvo & Alterações Necessárias

### 1. Refatorar `amb_cli/config/config.py`
Transforme o arquivo em uma fachada concisa e limpa (menos de 80 linhas):
- Importa e reexporta símbolos de `amb_cli.core`:
  - `Colors`, `AmbError`, `ConfigurationError`, `ApiExecutionError`, `log`, `log_error`, `load_env_file`, `require_env`
- Importa e reexporta símbolos de `amb_cli.workspace`:
  - `find_repo_root`, `load_project_json`, `get_repo_name`, `get_device_type`, `parse_design_tokens_from_text`, `get_design_system_config`
- Refatora `get_env(key, default=None)`:
  - Consulta `amb_cli.core.env.get_env(key)` e, se ausente, faz fallback defensivo para `load_project_json().get(key)`.
- Reexporta `main(as_json)` chamando `run_environment_diagnostics`.

### 2. Aperfeiçoar `amb_cli/config/config_core/env_diagnostics.py`
Ajuste os relatórios visuais gerados por `amb check` para que o terminal evidencie com clareza as duas seções:
1. **Credenciais do AMB Framework (Plataforma)**:
   - `JULES_API_KEY`, `GEMINI_API_KEY`, `STITCH_API_KEY`.
2. **Contexto do Workspace Alvo (Projeto Consumidor)**:
   - Raiz do projeto (`find_repo_root`), `GITHUB_REPOSITORY`, branch ativa, stack técnica, regras ativas e comandos de QA.

### 3. Criar Teste de Regressão e Contratos (`tests/test_config_facade.py`)
Crie um novo teste unitário que valida explicitamente:
1. Importações limpas via `amb_cli.core` e `amb_cli.workspace`.
2. Importações legadas via `amb_cli.config` e `config`.
3. Garanta que classes como `RulesManager` e exceções sejam referências idênticas (`is`) entre as duas camadas.

---

## 🛡️ Diretrizes e Regras Mandatórias
1. **Execução Global de QA**: Toda a suíte de testes do repositório deve passar com 0 falhas:
   ```bash
   pytest tests/
   python amb_cli/cli.py check
   ```
2. **Tipagem e Sintaxe Estrita**: Zero erros de compilação em `python -m py_compile cli.py amb_cli/cli.py`.

