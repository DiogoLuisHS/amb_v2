#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
⚡ Jules Tool: approve_plan (Facade)
Localização: amb_v2/integrations/jules/tools/approve_plan.py
Responsabilidade Única: Validar guardrails e aprovar planos de execução gerados pelo Google Jules.
"""

import sys
import os
import json
import argparse
from typing import Dict, Any, Optional

from config.bootstrap import ensure_amb_env
ensure_amb_env()

from config import Colors, log, log_error
from integrations.jules.jules_client import JulesClient


def run_approve_plan(
    session_id: str,
    force: bool = False,
    as_json: bool = False,
    client: Optional[JulesClient] = None
) -> Dict[str, Any]:
    """Valida e aprova o plano proposto pelo agente em uma sessão."""
    c = client or JulesClient()
    clean_id = c.normalize_session_id(session_id)

    # Guardrail: Verifica se a sessão está de fato aguardando aprovação de plano
    if not force:
        sess = c.get_session(clean_id)
        state = (sess.get("state") or "").upper()
        
        has_pending_plan = state in ["AWAITING_PLAN_APPROVAL", "AWAITING_PLAN"]
        if not has_pending_plan:
            act_res = c.list_activities(session_id=clean_id, page_size=10)
            acts = act_res.get("activities", []) if isinstance(act_res, dict) else (act_res if isinstance(act_res, list) else [])
            if acts:
                acts_sorted = sorted(
                    acts,
                    key=lambda x: x.get("createTime", "") if isinstance(x, dict) else "",
                    reverse=True
                )
                latest = acts_sorted[0] if isinstance(acts_sorted[0], dict) else {}
                originator = (latest.get("originator") or "").lower()
                if originator == "agent" and "planGenerated" in latest:
                    has_pending_plan = True

        if not has_pending_plan:
            raise ValueError("Error: There is no pending plan to approve. (Use --force para ignorar)")

    res = c.approve_plan(clean_id)

    if as_json:
        print(json.dumps(res, indent=2, ensure_ascii=False))
        return res

    log("JULES", f"✅ Plano da sessão {clean_id} aprovado com sucesso!", Colors.GREEN)
    return res


# Alias retrocompatível
approve_plan = run_approve_plan


def main():
    p = argparse.ArgumentParser(description="Aprova o plano de execução de uma sessão do Google Jules.")
    p.add_argument("session_id", nargs="?", help="ID ou URL da sessão do Jules.")
    p.add_argument("--session-id", "-s", dest="session_id_flag", help="ID ou URL da sessão (flag alternativa).")
    p.add_argument("--force", "-f", action="store_true", help="Força a aprovação ignorando checagem prévia de atividades.")
    p.add_argument("--json", action="store_true", help="Exibe a resposta em formato JSON puro.")
    args = p.parse_args()

    target_id = args.session_id or args.session_id_flag
    if not target_id:
        log_error("JULES", "ID da sessão é obrigatório.")
        sys.exit(1)

    try:
        run_approve_plan(session_id=target_id, force=args.force, as_json=args.json)
    except Exception as e:
        log_error("JULES", str(e))
        sys.exit(1)


if __name__ == "__main__":
    main()
