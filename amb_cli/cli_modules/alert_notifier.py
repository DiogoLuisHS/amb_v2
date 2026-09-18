#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
📡 AMB_V2 - Apresentação CLI: Emissor de Alertas Visuais e Sonoros (SRP)
Localização: amb_cli/cli_modules/alert_notifier.py
Responsabilidade Única: Formatar e emitir alertas destacados no terminal com destaque de atenção e beeps.
"""

import sys
from typing import Optional

from core.bootstrap import ensure_amb_env
ensure_amb_env()

from core import Colors


def play_beep() -> None:
    """Tenta emitir alerta sonoro no terminal de forma defensiva."""
    try:
        if sys.platform == "win32":
            import winsound
            winsound.MessageBeep(winsound.MB_ICONEXCLAMATION)
        else:
            print("\a", end="", flush=True)
    except Exception:
        pass


def notify_attention(source: str, title: str, details: str, action_command: Optional[str] = None) -> None:
    """Exibe um banner de alerta urgente no terminal."""
    play_beep()
    
    border = "!" * 75
    print("\n" + f"{Colors.RED}{Colors.BOLD}{border}{Colors.RESET}")
    print(f"🚨 {Colors.BOLD}[ATENÇÃO REQUERIDA] — FONTE: {source.upper()}{Colors.RESET}")
    print(f"📌 {Colors.BOLD}MOTIVO:{Colors.RESET} {title}")
    print("-" * 75)
    print(details.strip())
    
    if action_command:
        print("-" * 75)
        print(f"👉 {Colors.BOLD}COMANDO PARA RESPONDER/AGIR:{Colors.RESET}")
        print(f"   {Colors.GREEN}{action_command}{Colors.RESET}")
        
    print(f"{Colors.RED}{Colors.BOLD}{border}{Colors.RESET}\n", flush=True)


def notify_info(message: str) -> None:
    """Mensagem de status normal."""
    print(f"{Colors.GREEN}✔ {message}{Colors.RESET}", flush=True)


if __name__ == "__main__":
    notify_attention(
        source="Teste",
        title="Alerta de Exemplo",
        details="Isto é uma demonstração do banner de alerta.",
        action_command="amb advisor"
    )
