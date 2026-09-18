import os
import json
from typing import Optional

from amb_cli.core.exceptions import ConfigurationError
from amb_cli.core.logger import log_error


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

_PROJECT_METADATA: Optional[dict] = None

def get_project_metadata(reload: bool = False) -> dict:
    global _PROJECT_METADATA
    if _PROJECT_METADATA is None or reload:
        _PROJECT_METADATA = load_project_json()
    return _PROJECT_METADATA

def get_repo_name() -> str:
    """Obtém o nome do repositório configurado no .env (GITHUB_REPOSITORY)."""
    # Usamos os.environ para evitar acoplamento direto com core.env.get_env que será ajustado
    repo = os.environ.get("GITHUB_REPOSITORY")
    if repo and repo.strip():
        return repo.strip()

    p_meta = get_project_metadata()
    if "repository" in p_meta and p_meta["repository"]:
        return p_meta["repository"]

    raise ConfigurationError(
        "Variável GITHUB_REPOSITORY não configurada.",
        hint="Defina GITHUB_REPOSITORY=usuario/repo no seu arquivo .env"
    )

def get_device_type(default: Optional[str] = None) -> Optional[str]:
    """Obtém o tipo de dispositivo alvo configurado pelo usuário para o Stitch."""
    dev = os.environ.get("STITCH_DEVICE_TYPE") or os.environ.get("DEVICE_TYPE")
    if dev and dev.strip():
        return dev.strip().upper()

    p_meta = get_project_metadata()
    stitch_cfg = p_meta.get("stitch", {})
    if isinstance(stitch_cfg, dict) and stitch_cfg.get("device"):
        return str(stitch_cfg["device"]).strip().upper()
    if "device_type" in p_meta and p_meta["device_type"]:
        return str(p_meta["device_type"]).strip().upper()
    return default
