import os
import json
from typing import Optional

from .exceptions import ConfigurationError
from .logger import log_error


def _resolve_root() -> str:
    """Helper interno para localizar a raiz do repositório sem causar import circular."""
    try:
        from amb_cli.workspace.project_context import find_repo_root
        return find_repo_root()
    except Exception:
        pass
    # Fallback seguro procurando por .env ou .git
    curr = os.path.abspath(os.getcwd())
    for _ in range(6):
        if os.path.exists(os.path.join(curr, ".git")) or os.path.exists(os.path.join(curr, ".env")):
            return curr
        parent = os.path.dirname(curr)
        if parent == curr:
            break
        curr = parent
    return os.path.abspath(os.getcwd())


def load_env_file(path: Optional[str] = None) -> None:
    """Carrega variáveis do arquivo .env localizado na raiz do repositório ou path especificado."""
    if path is None:
        root = _resolve_root()
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
    try:
        from amb_cli.workspace.project_context import get_project_metadata
        p_meta = get_project_metadata()
        if key in p_meta and str(p_meta[key]).strip():
            return str(p_meta[key]).strip()
    except Exception:
        pass
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
        resolved_hint = hint or default_hints.get(key, f"Defina a variável '{key}' no arquivo .env ou execute amb setup")
        raise ConfigurationError(f"Variável mandatória ausente: '{key}'", hint=resolved_hint)
    return val


def is_gemini_confirmation_required() -> bool:
    """Verifica se a confirmação manual antes de cada chamada ao Gemini está ativada (padrão: False)."""
    val = get_env("REQUIRE_GEMINI_CONFIRMATION") or get_env("GEMINI_REQUIRE_CONFIRMATION")
    if val is not None:
        return str(val).lower() in ["true", "1", "yes", "sim", "on"]
    try:
        from amb_cli.workspace.project_context import get_project_metadata
        p_meta = get_project_metadata()
        if "require_gemini_confirmation" in p_meta:
            return bool(p_meta["require_gemini_confirmation"])
    except Exception:
        pass
    return False


def set_gemini_confirmation(enabled: bool) -> None:
    """Ativa ou desativa a exigência de confirmação prévia a cada chamada ao Gemini no .env e amb_project.json."""
    root = _resolve_root()
    env_path = os.path.join(root, ".env")
    lines = []
    found = False
    if os.path.exists(env_path):
        with open(env_path, "r", encoding="utf-8", errors="replace") as f:
            for line in f:
                if line.strip().startswith("REQUIRE_GEMINI_CONFIRMATION=") or line.strip().startswith("GEMINI_REQUIRE_CONFIRMATION="):
                    lines.append(f"REQUIRE_GEMINI_CONFIRMATION={'true' if enabled else 'false'}\n")
                    found = True
                else:
                    lines.append(line)
    if not found:
        lines.append(f"\n# Controle de Cota e Autorização do Gemini\nREQUIRE_GEMINI_CONFIRMATION={'true' if enabled else 'false'}\n")

    with open(env_path, "w", encoding="utf-8") as f:
        f.writelines(lines)
    os.environ["REQUIRE_GEMINI_CONFIRMATION"] = "true" if enabled else "false"

    p_json_path = os.path.join(root, ".amb", "amb_project.json")
    if os.path.exists(p_json_path):
        try:
            with open(p_json_path, "r", encoding="utf-8") as pf:
                data = json.load(pf)
            data["require_gemini_confirmation"] = enabled
            with open(p_json_path, "w", encoding="utf-8") as pf:
                json.dump(data, pf, indent=2, ensure_ascii=False)
        except Exception:
            pass
