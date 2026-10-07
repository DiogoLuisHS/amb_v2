import os
import threading
from typing import Any, Dict, Optional

from amb_cli.core.env import load_env_file, get_env as core_get_env
from amb_cli.core.exceptions import ConfigurationError
from amb_cli.workspace.project_context import load_project_json


class ConfigManager:
    """
    Gerenciador Central de Configurações com cache em memória (Singleton).
    """
    _instance: Optional["ConfigManager"] = None
    _lock = threading.RLock()

    def __init__(self) -> None:
        self._cached_env: Dict[str, str] = {}
        self._cached_project: Dict[str, Any] = {}
        self._loaded = False

    @classmethod
    def get_instance(cls) -> "ConfigManager":
        """Retorna a instância única do ConfigManager, inicializando se necessário."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = cls()
                    cls._instance.reload()
        return cls._instance

    def reload(self) -> None:
        """Limpa o cache e recarrega os dados a partir de disco (.env e amb_project.json)."""
        with self._lock:
            # 1. Recarregar o arquivo .env
            load_env_file()
            self._cached_env = dict(os.environ)

            # 2. Recarregar amb_project.json
            self._cached_project = load_project_json()

            self._loaded = True

    def get(self, key: str, default: Optional[str] = None) -> Optional[str]:
        """Obtém o valor do cache (ambiente ou projeto)."""
        if not self._loaded:
            self.reload()

        # Prioridade 1: Variáveis de ambiente (cache)
        if key in self._cached_env and self._cached_env[key].strip():
            return self._cached_env[key].strip()

        # Prioridade 2: Metadata do projeto (cache)
        if key in self._cached_project and str(self._cached_project[key]).strip():
            return str(self._cached_project[key]).strip()

        return default

    def require(self, key: str, hint: Optional[str] = None) -> str:
        """Obtém a chave obrigatória. Lança ConfigurationError se ausente."""
        val = self.get(key)
        if not val:
            default_hints = {
                "STITCH_API_KEY": "Obtenha em https://stitch.withgoogle.com e adicione no arquivo .env (STITCH_API_KEY=...)",
                "STITCH_PROJECT_ID": "Informe via argumento CLI (--project-id) ou configure STITCH_PROJECT_ID no .env",
                "JULES_API_KEY": "Obtenha em https://jules.google.com e adicione no arquivo .env (JULES_API_KEY=...)",
                "GITHUB_REPOSITORY": "Configure GITHUB_REPOSITORY=usuario/repositorio no .env ou execute setup_project.py",
                "GEMINI_API_KEY": "Obtenha em https://aistudio.google.com/app/api-keys e adicione no .env (GEMINI_API_KEY=...)",
            }
            resolved_hint = hint or default_hints.get(key, f"Defina a variável '{key}' no arquivo .env ou execute amb setup")
            raise ConfigurationError(f"Variável mandatória ausente: '{key}'", hint=resolved_hint)
        return val
