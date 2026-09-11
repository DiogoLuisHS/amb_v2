#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
📡 AMB_V2 - Monitoramento: Sentinela do Render Cloud (SRP)
Localização: amb_v2/dashboard/watchers/render_watcher.py
Responsabilidade Única: Inspecionar o status dos deploys do Render e alertar em caso de falha de build.
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

from config import get_env, log, log_error
from render_client import RenderClient
from alert_notifier import notify_attention


class RenderWatcher:
    """Vigia a saúde dos deploys no Render."""

    def __init__(self):
        self.client = RenderClient() if get_env("RENDER_API_KEY") else None
        self.notified_deploys = set()

    def check(self) -> list[dict]:
        """Varre os serviços e verifica o último deploy de cada um."""
        if not self.client:
            return []

        alerts = []
        try:
            services = self.client.list_services(limit=20)
            for item in services:
                srv = item.get("service", item)
                service_id = srv.get("id")
                service_name = srv.get("name", "Serviço Render")

                deploys = self.client.list_deploys(service_id=service_id, limit=1)
                if not deploys:
                    continue

                dep_obj = deploys[0]
                dep = dep_obj.get("deploy", dep_obj)
                deploy_id = dep.get("id")
                status = dep.get("status", "UNKNOWN").lower()

                if "fail" in status or "error" in status or "canceled" in status:
                    event_key = f"deploy:{deploy_id}:{status}"
                    if event_key not in self.notified_deploys:
                        self.notified_deploys.add(event_key)

                        commit_msg = dep.get("commit", {}).get("message", "N/A")
                        created_at = dep.get("createdAt", "")

                        notify_attention(
                            source="Render Cloud",
                            title=f"Falha de Deploy no serviço '{service_name}' ({service_id})",
                            details=(
                                f"Deploy ID: {deploy_id}\n"
                                f"Status: {status.upper()}\n"
                                f"Commit: {commit_msg}\n"
                                f"Data: {created_at}\n"
                                f"Logs: https://dashboard.render.com/web/{service_id}/deploys/{deploy_id}"
                            ),
                            action_command=f"python amb_v2/integrations/render/tools/fetch_logs.py --service-id {service_id}",
                        )
                        alerts.append(
                            {
                                "type": "deploy_failed",
                                "service_id": service_id,
                                "deploy_id": deploy_id,
                                "status": status,
                            }
                        )

        except Exception as e:
            log_error("RENDER-WATCHER", f"Falha na checagem do Render: {e}")

        return alerts


if __name__ == "__main__":
    w = RenderWatcher()
    al = w.check()
    print(f"Alertas Render detectados: {len(al)}")
