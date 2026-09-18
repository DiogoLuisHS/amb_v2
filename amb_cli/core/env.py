import os
import json
from typing import Optional

from .exceptions import ConfigurationError
from .logger import log_error


def find_repo_root(start_dir: Optional[str] = None) -> str:
    """Localiza a raiz do repositório procurando por .git, .env ou package.json."""
    start = os.path.abspath(start_dir or os.getcwd())
    curr = start
    for _ in range(6):
        has_git = os.path.exists(os.path.join(curr, ".git"))
        has_env = os.path.exists(os.path.join(curr, ".env"))
        has_markers = (
            has_git
            or has_env
            or os.path.exists(os.path.join(curr, "amb_project.json"))
            or os.path.exists(os.path.join(curr, "package.json"))
            or os.path.exists(os.path.join(curr, "pyproject.toml"))
            or os.path.exists(os.path.join(curr, "requirements.txt"))
        )
        if has_markers:
            if os.path.basename(curr) == "amb_v2":
                parent = os.path.dirname(curr)
                parent_has_env = os.path.exists(os.path.join(parent, ".env"))
                parent_has_git = os.path.exists(os.path.join(parent, ".git"))
                if parent_has_env:
                    return parent
                if has_env:
                    return curr
                if parent_has_git and parent_has_env:
                    return parent
            return curr
        parent = os.path.dirname(curr)
        if parent == curr:
            break
        curr = parent
    return start


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


def load_project_json(repo_root: Optional[str] = None) -> dict:
    """Carrega dados contextuais de amb_project.json prioritariamente em .amb/, .jules/ ou na raiz."""
    if repo_root:
        candidates = [
            os.path.join(repo_root, ".amb", "amb_project.json"),
            os.path.join(repo_root, ".amb", "project.json"),
            os.path.join(repo_root, ".jules", "amb_project.json"),
            os.path.join(repo_root, ".jules", "project.json"),
            os.path.join(repo_root, "amb_project.json"),
        ]
    else:
        root = find_repo_root()
        candidates = [
            os.path.join(root, ".amb", "amb_project.json"),
            os.path.join(root, ".amb", "project.json"),
            os.path.join(root, ".jules", "amb_project.json"),
            os.path.join(root, ".jules", "project.json"),
            os.path.join(root, "amb_project.json"),
            os.path.join(root, "amb_v2", "config", "amb_project.json"),
            # Posição original deste arquivo era amb_cli/config/config.py
            os.path.join(os.path.dirname(__file__), "..", "config", "amb_project.json"),
        ]
    for p_path in candidates:
        if os.path.exists(p_path):
            try:
                with open(p_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
    return {}


# Carrega variáveis automaticamente na importação
load_env_file()
_PROJECT_METADATA = load_project_json()


def get_env(key: str, default: Optional[str] = None) -> Optional[str]:
    """Obtém variável de ambiente ou metadata de projeto, retornando default se não existir."""
    if key in os.environ and os.environ[key].strip():
        return os.environ[key].strip()
    if key in _PROJECT_METADATA and str(_PROJECT_METADATA[key]).strip():
        return str(_PROJECT_METADATA[key]).strip()
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
