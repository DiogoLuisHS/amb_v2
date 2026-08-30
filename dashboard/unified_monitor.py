#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
📡 AMB_V2 - Monitoramento Unificado e Contínuo em Tempo Real
Localização: amb_v2/dashboard/unified_monitor.py
Responsabilidade Única: Executar o loop de vigilância concorrente dos 4 módulos (Jules, Render,
Stitch, Antigravity) e notificar instantaneamente o desenvolvedor sobre erros ou dúvidas.
"""

import os
import sys
import time
import argparse
from datetime import datetime

# Bootstrap dinâmico de caminhos amb_v2
_cur = os.path.dirname(os.path.abspath(__file__))
while _cur and os.path.basename(_cur) != "amb_v2":
    _p = os.path.dirname(_cur)
    if _p == _cur:
        break
    _cur = _p
_AMB = _cur
for _sub in [
    "config", "agents", "pipeline", "dashboard", "dashboard/watchers",
    "integrations/jules", "integrations/jules/tools",
    "integrations/stitch", "integrations/stitch/tools",
    "integrations/antigravity", "integrations/antigravity/tools",
    "integrations/render", "integrations/render/tools",
]:
    _p = os.path.normpath(os.path.join(_AMB, *_sub.split("/")))
    if os.path.exists(_p) and _p not in sys.path:
        sys.path.insert(0, _p)

from config import Colors, log, log_error, get_env
from jules_watcher import JulesWatcher
from render_watcher import RenderWatcher
from alert_notifier import notify_info


def run_monitor(interval_seconds: int = 15, check_once: bool = False, auto_approve: bool = False):
    """Loop principal de monitoramento unificado."""
    print("\n" + "=" * 75)
    mode_text = f"{Colors.BOLD}{Colors.GREEN}[MODO AUTO-APPROVE ATIVO ⚡]{Colors.RESET}" if auto_approve else "[MODO MONITOR DE ALERTA]"
    print(f"{Colors.BOLD}{Colors.CYAN}📡 AMB_V2 — SENTINELA E MONITOR UNIFICADO DE ATENÇÃO (EM TEMPO REAL) {mode_text}{Colors.RESET}")
    print("=" * 75)
    print(f"Intervalo de Polling: {interval_seconds}s")
    print(f"Jules API Key:       {'Configurada ✅' if get_env('JULES_API_KEY') else 'Não configurada ⚠️'}")
    print(f"Render API Key:      {'Configurada ✅' if get_env('RENDER_API_KEY') else 'Não configurada ⚠️'}")
    print(f"Stitch API Key:      {'Configurada ✅' if get_env('STITCH_API_KEY') else 'Não configurada ⚠️'}")
    print(f"Gemini/Antigravity:  {'Configurada ✅' if get_env('GEMINI_API_KEY') else 'Não configurada ⚠️'}")
    print("-" * 75)
    print(f"{Colors.DIM}Pressione Ctrl+C para encerrar o monitoramento a qualquer momento.{Colors.RESET}\n")

    jules_w = JulesWatcher()
    render_w = RenderWatcher()

    cycle = 1
    while True:
        try:
            now_str = datetime.now().strftime("%H:%M:%S")
            print(f"[{now_str}] 🔄 Rodada #{cycle}: Checando chats e status...", flush=True)

            # 1. Jules
            jules_alerts = jules_w.check()

            # Se estiver em modo auto_approve e houver chats aguardando feedback
            if auto_approve and jules_alerts:
                from auto_reply import advise_and_reply
                for alt in jules_alerts:
                    if alt.get("type") in ["awaiting_feedback", "message"]:
                        sid = alt.get("session_id")
                        log("AUTO-PILOT", f"⚡ Auto-respondendo à sessão {sid} via Antigravity SDK...", Colors.CYAN)
                        try:
                            advise_and_reply(session_id=sid, auto_approve=True)
                        except Exception as e:
                            log_error("AUTO-PILOT", f"Falha no auto-reply da sessão {sid}: {e}")

            # 2. Render
            render_alerts = render_w.check()

            if not jules_alerts and not render_alerts:
                notify_info("Tudo operando normalmente. Nenhuma pendência humana ou erro detectado.\n")

            if check_once:
                log("MONITOR", "Checagem única concluída.", Colors.CYAN)
                break

            cycle += 1
            time.sleep(interval_seconds)

        except KeyboardInterrupt:
            print(f"\n{Colors.YELLOW}Monitoramento finalizado pelo usuário.{Colors.RESET}")
            break
        except Exception as e:
            log_error("MONITOR", f"Erro no ciclo de monitoramento: {e}")
            if check_once:
                break
            time.sleep(interval_seconds)


def main():
    parser = argparse.ArgumentParser(description="Monitor unificado de atenção para Jules, Render, Stitch e Antigravity.")
    parser.add_argument("--interval", "-i", type=int, default=15, help="Intervalo em segundos entre verificações (padrão: 15s).")
    parser.add_argument("--check-once", action="store_true", help="Executa apenas uma verificação e encerra.")
    parser.add_argument("--auto-approve", "-y", action="store_true", help="Piloto automático: gera respostas com Antigravity e envia sozinho para todas as dúvidas.")

    args = parser.parse_args()
    run_monitor(interval_seconds=args.interval, check_once=args.check_once, auto_approve=args.auto_approve)


if __name__ == "__main__":
    main()
