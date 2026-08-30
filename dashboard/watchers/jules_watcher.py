#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
📡 AMB_V2 - Monitoramento: Sentinela do Google Jules (SRP)
Localização: amb_v2/dashboard/watchers/jules_watcher.py
Responsabilidade Única: Inspecionar sessões e atividades do Jules em busca de perguntas,
solicitações de aprovação de plano e falhas.
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
    "config", "agents", "pipeline", "dashboard", "dashboard/watchers",
    "integrations/jules", "integrations/jules/tools",
    "integrations/stitch", "integrations/stitch/tools",
    "integrations/antigravity", "integrations/antigravity/tools",
    "integrations/render", "integrations/render/tools",
]:
    _p = os.path.normpath(os.path.join(_AMB, *_sub.split("/")))
    if os.path.exists(_p) and _p not in sys.path:
        sys.path.insert(0, _p)

from config import get_env, Colors, log, log_error, get_repo_name
from jules_client import JulesClient
from alert_notifier import notify_attention


class JulesWatcher:
    """Vigia o estado das sessões do Jules."""

    def __init__(self):
        self.client = JulesClient() if get_env("JULES_API_KEY") else None
        self.notified_events = set()

    def check(self) -> list[dict]:
        """Verifica todas as sessões e retorna alertas detectados."""
        if not self.client:
            return []

        alerts = []
        try:
            repo = get_repo_name()
            sessions = self.client.list_sessions(page_size=30, repo_filter=repo)
            for s in sessions:
                session_id = s.get("name", "").split("/")[-1] or s.get("id")
                state = s.get("state", "UNKNOWN")
                title = s.get("title", "Sem título")

                # 1. Sessão que falhou ou foi cancelada
                if state in ["FAILED", "CANCELLED"]:
                    event_key = f"failed:{session_id}"
                    if event_key not in self.notified_events:
                        self.notified_events.add(event_key)
                        notify_attention(
                            source="Google Jules",
                            title=f"Sessão falhou ou foi cancelada ({session_id})",
                            details=f"Título: {title}\nEstado: {state}\nPainel: https://jules.google.com/session/{session_id}",
                            action_command=f"python amb_v2/integrations/jules/tools/get_session.py --session-id {session_id}"
                        )
                        alerts.append({"type": "failed", "session_id": session_id})
                    continue

                # 2. Sessão com estado explícito de feedback ou aprovação de plano
                if state in ["AWAITING_USER_FEEDBACK", "Awaiting User Feedback", "AWAITING_INPUT", "AWAITING_PLAN_APPROVAL"]:
                    event_key = f"state_feedback:{session_id}"
                    if event_key not in self.notified_events:
                        self.notified_events.add(event_key)
                        
                        last_msg = ""
                        try:
                            act_res = self.client.list_activities(session_id=session_id, page_size=20)
                            acts = act_res.get("activities", [])
                            for a in reversed(acts):
                                for key in ["agentMessage", "agentMessaged", "userFeedbackRequired"]:
                                    if key in a:
                                        val = a[key]
                                        if isinstance(val, str) and val.strip():
                                            last_msg = val.strip()
                                            break
                                        elif isinstance(val, dict):
                                            for subk in ["agentMessage", "text", "message", "question", "prompt", "description"]:
                                                if subk in val and isinstance(val[subk], str) and val[subk].strip():
                                                    last_msg = val[subk].strip()
                                                    break
                                if last_msg:
                                    break
                        except Exception:
                            pass

                        msg_detail = f"❓ Pergunta/Proposta do Agente:\n\"{last_msg.strip()}\"\n" if last_msg else "O agente finalizou o turno/mudança e aguarda sua instrução para prosseguir.\n"

                        notify_attention(
                            source="Google Jules",
                            title=f"Sessão aguardando sua resposta: '{title}' ({session_id})",
                            details=f"{msg_detail}Estado: {state}\nPainel: https://jules.google.com/session/{session_id}",
                            action_command=f"python amb_v2/agents/auto_reply.py --session-id {session_id}"
                        )
                        alerts.append({"type": "awaiting_feedback", "session_id": session_id, "text": last_msg})
                    continue

        except Exception as e:
            log_error("JULES-WATCHER", f"Falha na checagem de sessões: {e}")

        return alerts


if __name__ == "__main__":
    w = JulesWatcher()
    al = w.check()
    print(f"Alertas Jules detectados: {len(al)}")
