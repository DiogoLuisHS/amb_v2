import sys
from datetime import datetime
from typing import Optional

# Garante suporte adequado a UTF-8 no terminal Windows
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass


class Colors:
    """Paleta ANSI para logs padronizados no terminal."""
    HEADER = "\033[95m"
    BLUE = "\033[94m"
    CYAN = "\033[96m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    RESET = "\033[0m"


def log(tag: str, message: str, color: str = Colors.RESET) -> None:
    """Imprime mensagem com timestamp e tag colorida."""
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] [{color}{Colors.BOLD}{tag}{Colors.RESET}] {message}", flush=True)


def log_error(tag: str, message: str, hint: Optional[str] = None) -> None:
    """Imprime erro com formatação de alerta e dica de resolução."""
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] [{Colors.RED}{Colors.BOLD}ERRO::{tag}{Colors.RESET}] {message}", file=sys.stderr, flush=True)
    if hint:
        print(f"[{timestamp}] [{Colors.YELLOW}{Colors.BOLD}DICA DE RESOLUÇÃO{Colors.RESET}] {hint}", file=sys.stderr, flush=True)
