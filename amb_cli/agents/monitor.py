#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
📡 AMB_V2 - Agentes: Monitor e Sentinela Unificado em Tempo Real (SRP)
Localização: amb_cli/agents/monitor.py
Responsabilidade Única: Executar o loop de vigilância das sessões do ecossistema Google (Jules,
Stitch, Antigravity) e notificar instantaneamente o desenvolvedor ou auto-responder dúvidas no piloto automático.
"""

import time
from datetime import datetime

from config.bootstrap import ensure_amb_env
ensure_amb_env()

from config import Colors, log, log_error, get_env
# Regra 03: Imports Limpos e organizados (Sem imports mortos ou tardios)
from agents.auto_reply import advise_and_reply
from integrations.jules.jules_watcher import JulesWatcher
from cli_modules.alert_notifier import notify_info


def run_monitor(interval_seconds: int = 15, check_once: bool = False, auto_approve: bool = False) -> None:
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

    try:
        while True:
            try:
                now_str = datetime.now().strftime("%H:%M:%S")
                print(f"[{now_str}] 🔄 Rodada #{cycle}: Checando chats e status...", flush=True)

                try:
                    jules_alerts = jules_w.check()
                except Exception as e:
                    log_error("MONITOR", f"Falha transiente na checagem do Jules: {e}")
                    jules_alerts = None

                if auto_approve and jules_alerts:
                    for alt in jules_alerts:
                        if alt.get("type") in ["awaiting_feedback", "message"]:
                            sid = alt.get("session_id")
                            log("AUTO-PILOT", f"⚡ Auto-respondendo à sessão {sid} via Antigravity SDK...", Colors.CYAN)
                            try:
                                advise_and_reply(session_id=sid, auto_approve=True)
                            except Exception as e:
                                log_error("AUTO-PILOT", f"Falha no auto-reply da sessão {sid}: {e}")

                if jules_alerts is not None and not jules_alerts:
                    notify_info("Tudo operando normalmente. Nenhuma pendência humana ou erro detectado.\n")

                if check_once:
                    log("MONITOR", "Checagem única concluída.", Colors.CYAN)
                    break

                cycle += 1
                time.sleep(interval_seconds)

            except Exception as e:
                log_error("MONITOR", f"Erro no ciclo de monitoramento: {e}")
                if check_once:
                    break
                time.sleep(interval_seconds)
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Monitoramento finalizado pelo usuário.{Colors.RESET}")


class UnifiedMonitor:
    """Classe orientada a objetos para o Sentinela Unificado AMB_V2."""

    def __init__(self, interval: int = 15, auto_approve: bool = False) -> None:
        self.interval = interval
        self.auto_approve = auto_approve

    def run(self, check_once: bool = False) -> None:
        """Executa o loop do monitoramento."""
        run_monitor(interval_seconds=self.interval, check_once=check_once, auto_approve=self.auto_approve)


def main() -> None:
    """Ponto de entrada simplificado (sem parse de args, que agora fica na camada CLI)."""
    monitor = UnifiedMonitor()
    monitor.run()


if __name__ == "__main__":
    main()
