from .exceptions import AmbError, ConfigurationError, ApiExecutionError
from .logger import Colors, log, log_error
from .env import (
    load_env_file,
    get_env,
    require_env,
    is_gemini_confirmation_required,
    set_gemini_confirmation,
)
from .bootstrap import (
    ensure_amb_env,
    get_amb_root,
    get_amb_package_dir,
    add_to_sys_path,
    CANONICAL_SUBMODULES,
)


def run_environment_diagnostics(as_json: bool = False):
    """Executa os diagnósticos de ambiente chamando o módulo core.diagnostics sob demanda."""
    from .diagnostics import run_environment_diagnostics as _run
    return _run(as_json=as_json)


__all__ = [
    "AmbError",
    "ConfigurationError",
    "ApiExecutionError",
    "Colors",
    "log",
    "log_error",
    "load_env_file",
    "get_env",
    "require_env",
    "is_gemini_confirmation_required",
    "set_gemini_confirmation",
    "ensure_amb_env",
    "get_amb_root",
    "get_amb_package_dir",
    "add_to_sys_path",
    "CANONICAL_SUBMODULES",
    "run_environment_diagnostics",
]
