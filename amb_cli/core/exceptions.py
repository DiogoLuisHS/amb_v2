from typing import Optional

class AmbError(Exception):
    """Exceção base para o ecossistema amb_v2 com diagnóstico detalhado."""
    def __init__(self, message: str, hint: Optional[str] = None):
        full_msg = f"{message}"
        if hint:
            full_msg += f"\n👉 COMO RESOLVER: {hint}"
        super().__init__(full_msg)
        self.message = message
        self.hint = hint


class ConfigurationError(AmbError):
    """Lançado quando uma chave de API, arquivo ou configuração mandatória está ausente."""
    pass


class ApiExecutionError(AmbError):
    """Lançado quando uma chamada a uma das SDKs/APIs falha explicitamente."""
    pass
