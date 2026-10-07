# 🎯 US-04: Gerenciador Central de Configurações com Cache em Memória (ConfigManager)

## 👤 User Story
> **Como** desenvolvedor do AMB_V2,  
> **Quero** um `ConfigManager` singleton com carregamento atômico e cache em memória,  
> **Para que** centenas de leituras concorrentes de disco do `.env` e de `amb_project.json` sejam eliminadas durante o loop autônomo, acelerando a execução e permitindo recarga sob demanda via `amb config reload`.

---

## 📌 Critérios de Aceitação BDD

* **Cenário 1: Padrão Singleton com Cache em Memória**
  * **Dado** a classe `ConfigManager` em `amb_cli/core/config_manager.py`;
  * **Quando** `ConfigManager.get_instance()` for chamado múltiplas vezes;
  * **Então** deve retornar a mesma instância em memória;
  * **E** as leituras de disco só devem ocorrer na primeira inicialização ou quando `reload()` for explicitamente chamado.

* **Cenário 2: Validação Fail-Fast e Acesso Tipado**
  * **Dado** que uma configuração obrigatória está ausente (ex: `JULES_API_KEY`);
  * **Quando** `config.require("JULES_API_KEY")` for executado;
  * **Então** deve lançar `AmbError` com mensagem clara e dica de resolução.

* **Cenário 3: Comando de Recarga na CLI (amb config reload)**
  * **Dado** o comando `amb config reload`;
  * **Quando** executado no terminal;
  * **Então** deve limpar o cache em memória, reler o `.env` e `amb_project.json` e exibir resumo das chaves carregadas com sucesso.

---

## 🛠️ Arquivos Alvo & Alterações Necessárias

### 1. `amb_cli/core/config_manager.py` (Novo)
Implementar `ConfigManager`:
```python
import os
import threading
from typing import Any, Dict, Optional
from workspace import find_repo_root, load_project_json
from core.env import get_env
from core.exceptions import AmbError

class ConfigManager:
    _instance: Optional["ConfigManager"] = None
    _lock = threading.Lock()

    def __init__(self) -> None:
        self._cached_env: Dict[str, str] = {}
        self._cached_project: Dict[str, Any] = {}
        self._loaded = False

    @classmethod
    def get_instance(cls) -> "ConfigManager":
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = cls()
                    cls._instance.reload()
        return cls._instance

    def reload(self) -> None:
        # Carrega .env e amb_project.json para a memória
        ...
```

### 2. `amb_cli/cli_modules/handlers_core/config_handler.py`
Adicionar suporte ao subcomando `reload`:
`amb config reload` -> invoca `ConfigManager.get_instance().reload()` e exibe confirmação.

### 3. `amb_cli/cli_modules/cli_parsers.py`
Adicionar flag/subcomando `--reload` ou ação `reload` no parser do comando `amb config`.

### 4. `tests/test_config_manager.py` (Novo)
Testes cobrindo:
- Garantia de instância única (singleton).
- Eficiência de cache (mocking de I/O de arquivo para garantir zero leituras repetidas).
- Comportamento de `reload()`.
- Lançamento de erro em `require()` com chaves ausentes.

---

## 🔍 Comandos de Verificação Local
```bash
# Validar testes unitários do ConfigManager
pytest tests/test_config_manager.py -v

# Validar suíte completa
pytest -q

# Testar comando na CLI
python -m amb_cli.cli config reload
```

---

## 📋 Definition of Done (DoD)
- [ ] `ConfigManager` implementado com thread-safety e cache em memória.
- [ ] `amb config reload` operacional na CLI.
- [ ] Testes unitários dedicados em `tests/test_config_manager.py` 100% passando.
- [ ] Todos os arquivos abaixo de 200 linhas e conformes com a Regra 02.
