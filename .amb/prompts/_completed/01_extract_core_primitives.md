# 🎯 Task: Isolar Primitivas do Framework AMB em `amb_cli/core/`

## 📌 Contexto & Responsabilidade Única (SRP)
Atualmente, o diretório `amb_cli/config/` acumula responsabilidades da infraestrutura interna do AMB com configurações de projetos consumidores.
Nesta primeira etapa, sua missão é **isolar as primitivas de infraestrutura do AMB** em um novo pacote `amb_cli/core/`.

---

## 🛠️ Arquivos Alvo & Alterações Necessárias

### 1. Criar novo pacote `amb_cli/core/`
Crie o diretório `amb_cli/core/` contendo:
- `amb_cli/core/__init__.py`:
  Reexporta:
  - De `exceptions.py`: `AmbError`, `ConfigurationError`, `ApiExecutionError`
  - De `logger.py`: `Colors`, `log`, `log_error`
  - De `env.py`: `load_env_file`, `get_env`, `require_env`
  - De `bootstrap.py`: `ensure_amb_env`, `get_amb_root`, `get_amb_package_dir`, `add_to_sys_path`, `CANONICAL_SUBMODULES`

- `amb_cli/core/exceptions.py`:
  Definição de `AmbError`, `ConfigurationError`, `ApiExecutionError` com formatação ANSI e hints de resolução.

- `amb_cli/core/logger.py`:
  Definição de `Colors` (paleta ANSI) e funções `log(tag, message, color)` e `log_error(tag, message, hint)`. Garanta compatibilidade UTF-8 no Windows.

- `amb_cli/core/env.py`:
  Funções de carregamento de variáveis de ambiente do AMB:
  - `load_env_file(path=None)`: Carrega o arquivo `.env` do repositório/ambiente.
  - `get_env(key, default=None)`: Busca prioritariamente em `os.environ`.
  - `require_env(key, hint=None)`: Exige a chave ou lança `ConfigurationError`.

- `amb_cli/core/bootstrap.py`:
  Mova a lógica de bootstrap de `amb_cli/config/bootstrap.py` para cá:
  - Auto-injeção de `sys.path`.
  - Atualize `CANONICAL_SUBMODULES` para incluir `"core"`, `"core/exceptions"`, `"core/logger"`, `"core/env"`, `"core/bootstrap"`.

---

### 2. Camada de Compatibilidade Reversa (Facade)
- Modifique `amb_cli/config/bootstrap.py` para importar e reexportar todos os símbolos de `amb_cli.core.bootstrap` (ou `core.bootstrap`), garantindo que qualquer chamada legada continue funcionando sem quebra.
- Em `amb_cli/config/config.py`, substitua as implementações originais de `Colors`, `AmbError`, `ConfigurationError`, `ApiExecutionError`, `log`, `log_error` por imports diretos de `amb_cli.core`.

---

## 🛡️ Diretrizes e Regras Mandatórias
1. **Zero Quebra de Contratos**: Nenhum arquivo existente que faça `from config import Colors, log, AmbError` ou `from config.bootstrap import ensure_amb_env` pode falhar.
2. **Tipagem e Docstrings**: Use type annotations completas (`Optional`, `Dict`, `Union`, etc.) e docstrings concisas.
3. **Validação de QA Local**:
   Execute e assegure 100% de sucesso nos testes:
   ```bash
   pytest tests/test_bootstrap.py tests/test_config.py
   python -m py_compile amb_cli/core/*.py
   ```

---

## 🚀 Ação Final Obrigatória: Commit e Abertura do Pull Request
Ao concluir as alterações e validar os testes locais com 100% de sucesso:
1. Você DEVE commitar todos os novos arquivos em `amb_cli/core/` e os arquivos modificados em `amb_cli/config/`.
2. Você DEVE submeter formalmente o Pull Request no GitHub para que o pipeline do AMB realize a validação de QA e o auto-merge na branch `main`.

