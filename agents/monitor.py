#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
📡 AMB_V2 - Agentes: Monitor e Sentinela Unificado em Tempo Real (SRP)
Localização: amb_v2/agents/monitor.py
Responsabilidade Única: Executar o loop de vigilância das sessões do ecossistema Google (Jules,
Stitch, Antigravity) e notificar instantaneamente o desenvolvedor ou auto-responder dúvidas no piloto automático.
"""

import os
import sys
import time
import argparse
from datetime import datetime

from config.bootstrap import ensure_amb_env
ensure_amb_env()

from config import Colors, log, log_error, get_env
from integrations.jules.jules_watcher import JulesWatcher
from cli_modules.alert_notifier import notify_info


def run_monitor(interval_seconds: int = 15, check_once: bool = False, auto_approve: bool = False):
    """Loop principal de monitoramento e vigilância unificada."""
    print("\n" + "=" * 75)
    mode_text = f"{Colors.BOLD}{Colors.GREEN}[MODO AUTO-APPROVE ATIVO ⚡]{Colors.RESET}" if auto_approve else "[MODO MONITOR DE ALERTA]"
    print(f"{Colors.BOLD}{Colors.CYAN}📡 AMB_V2 — SENTINELA E MONITOR UNIFICADO DE ATENÇÃO (EM TEMPO REAL) {mode_text}{Colors.RESET}")
    print("=" * 75)
    print(f"Intervalo de Polling: {interval_seconds}s")
    print(f"Jules API Key:       {'Configurada ✅' if get_env('JULES_API_KEY') else 'Não configurada ⚠️'}")
    print(f"Stitch API Key:      {'Configurada ✅' if get_env('STITCH_API_KEY') else 'Não configurada ⚠️'}")
    print(f"Gemini/Antigravity:  {'Configurada ✅' if get_env('GEMINI_API_KEY') else 'Não configurada ⚠️'}")
    print("-" * 75)
    print(f"{Colors.DIM}Pressione Ctrl+C para encerrar o monitoramento a qualquer momento.{Colors.RESET}\n")

    jules_w = JulesWatcher()
    cycle = 1

    while True:
        try:
            now_str = datetime.now().strftime("%H:%M:%S")
            print(f"[{now_str}] 🔄 Rodada #{cycle}: Checando chats e status...", flush=True)

            # 1. Checagem do Jules
            jules_alerts = jules_w.check()

            # Se estiver em modo auto_approve e houver sessões aguardando feedback
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

            if not jules_alerts:
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


class UnifiedMonitor:
    """Classe orientada a objetos para o Sentinela Unificado AMB_V2."""

    def __init__(self, interval: int = 15, auto_approve: bool = False):
        self.interval = interval
        self.auto_approve = auto_approve

    def run(self, check_once: bool = False):
        run_monitor(interval_seconds=self.interval, check_once=check_once, auto_approve=self.auto_approve)


def main():
    parser = argparse.ArgumentParser(description="Sentinela unificado de atenção para Jules, Stitch e Antigravity.")
    parser.add_argument("--interval", "-i", type=int, default=15, help="Intervalo em segundos entre verificações (padrão: 15s).")
    parser.add_argument("--check-once", action="store_true", help="Executa apenas uma verificação e encerra.")
    parser.add_argument("--auto-approve", "-y", action="store_true", help="Piloto automático: gera respostas com Antigravity e envia sozinho para todas as dúvidas.")

    args = parser.parse_args()
    monitor = UnifiedMonitor(interval=args.interval, auto_approve=args.auto_approve)
    monitor.run(check_once=args.check_once)


if __name__ == "__main__":
    main()
