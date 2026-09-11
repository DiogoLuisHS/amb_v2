#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
📡 AMB_V2 - Monitoramento: Emissor de Alertas Visuais e Sonoros (SRP)
Localização: amb_v2/dashboard/watchers/alert_notifier.py
Responsabilidade Única: Formatar e emitir alertas destacados no terminal com destaque de atenção e beeps.
"""

import sys
import os

# Bootstrap dinâmico de caminhos amb_v2
_cur = os.path.dirname(os.path.abspath(__file__))
while _cur and os.path.basename(_cur) != "amb_v2":
    _p = os.path.dirname(_cur)
    if _p == _cur:
        break
    _cur = _p
_AMB = _cur
for _sub in [
    "config",
    "agents",
    "pipeline",
    "dashboard",
    "dashboard/watchers",
    "integrations/jules",
    "integrations/jules/tools",
    "integrations/stitch",
    "integrations/stitch/tools",
    "integrations/antigravity",
    "integrations/antigravity/tools",
    "integrations/render",
    "integrations/render/tools",
]:
    _p = os.path.normpath(os.path.join(_AMB, *_sub.split("/")))
    if os.path.exists(_p) and _p not in sys.path:
        sys.path.insert(0, _p)

from config import Colors


def play_beep():
    """Tenta emitir alerta sonoro no terminal."""
    try:
        if sys.platform == "win32":
            import winsound

            winsound.MessageBeep(winsound.MB_ICONEXCLAMATION)
        else:
            print("\a", end="", flush=True)
    except Exception:
        pass


def notify_attention(source: str, title: str, details: str, action_command: str = None):
    """Exibe um banner de alerta urgente no terminal."""
    play_beep()

    border = "!" * 75
    print("\n" + f"{Colors.RED}{Colors.BOLD}{border}{Colors.RESET}")
    print(
        f"🚨 {Colors.BOLD}[ATENÇÃO REQUERIDA] — FONTE: {source.upper()}{Colors.RESET}"
    )
    print(f"📌 {Colors.BOLD}MOTIVO:{Colors.RESET} {title}")
    print("-" * 75)
    print(details.strip())

    if action_command:
        print("-" * 75)
        print(f"👉 {Colors.BOLD}COMANDO PARA RESPONDER/AGIR:{Colors.RESET}")
        print(f"   {Colors.GREEN}{action_command}{Colors.RESET}")

    print(f"{Colors.RED}{Colors.BOLD}{border}{Colors.RESET}\n", flush=True)


def notify_info(message: str):
    """Mensagem de status normal."""
    print(f"{Colors.GREEN}✔ {message}{Colors.RESET}", flush=True)


if __name__ == "__main__":
    notify_attention(
        source="Teste",
        title="Alerta de Exemplo",
        details="Isto é uma demonstração do banner de alerta.",
        action_command="python amb_v2/dashboard/auto_advisor.py",
    )
