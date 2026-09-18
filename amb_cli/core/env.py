import os
import json
from typing import Optional

from .exceptions import ConfigurationError
from .logger import log_error


from amb_cli.workspace.project_context import find_repo_root, get_project_metadata

def load_env_file(path: Optional[str] = None) -> None:
    """Carrega variáveis do arquivo .env localizado na raiz do repositório ou path especificado."""
    if path is None:
        root = find_repo_root()
        env_path = os.path.join(root, ".env")
    else:
        env_path = path

    if os.path.exists(env_path):
        try:
            with open(env_path, "r", encoding="utf-8", errors="replace") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        k, v = line.split("=", 1)
                        k = k.strip()
                        v = v.strip().strip("'").strip('"')
                        if k and k not in os.environ:
                            os.environ[k] = v
        except Exception as e:
            log_error("CONFIG", f"Falha ao ler arquivo .env em {env_path}: {e}")


# Carrega variáveis automaticamente na importação
load_env_file()


def get_env(key: str, default: Optional[str] = None) -> Optional[str]:
    """Obtém variável de ambiente ou metadata de projeto, retornando default se não existir."""
    if key in os.environ and os.environ[key].strip():
        return os.environ[key].strip()
    p_meta = get_project_metadata()
    if key in p_meta and str(p_meta[key]).strip():
        return str(p_meta[key]).strip()
    return default


def require_env(key: str, hint: Optional[str] = None) -> str:
    """Exige a presença de uma variável de ambiente."""
    val = get_env(key)
    if not val:
        default_hints = {
            "STITCH_API_KEY": "Obtenha em https://stitch.withgoogle.com e adicione no arquivo .env (STITCH_API_KEY=...)",
            "STITCH_PROJECT_ID": "Informe via argumento CLI (--project-id) ou configure STITCH_PROJECT_ID no .env",
            "JULES_API_KEY": "Obtenha em https://jules.google.com e adicione no arquivo .env (JULES_API_KEY=...)",
            "GITHUB_REPOSITORY": "Configure GITHUB_REPOSITORY=usuario/repositorio no .env ou execute setup_project.py",
            "GEMINI_API_KEY": "Obtenha em https://aistudio.google.com/app/api-keys e adicione no .env (GEMINI_API_KEY=...)",
        }
        resolved_hint = hint or default_hints.get(key, f"Defina a variável '{key}' no arquivo .env ou execute python amb_v2/config/setup_project.py")
        raise ConfigurationError(f"Variável mandatória ausente: '{key}'", hint=resolved_hint)
    return val
