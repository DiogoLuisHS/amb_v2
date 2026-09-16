#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
⚡ Jules Tool: send_message (Facade)
Localização: amb_v2/integrations/jules/tools/send_message.py
Responsabilidade Única: Enviar mensagens ao chat de uma sessão do Jules com guardrail anti-duplicação.
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


def run_send_message(
    session_id: str,
    message: str,
    force: bool = False,
    as_json: bool = False,
    client: Optional[JulesClient] = None
) -> Dict[str, Any]:
    """Valida guardrails e envia uma mensagem direta para a sessão do Jules."""
    c = client or JulesClient()
    clean_id = c.normalize_session_id(session_id)

    # Guardrail para evitar envio consecutivo sem resposta do agente
    if not force:
        act_res = c.list_activities(session_id=clean_id, page_size=1)
        activities = act_res.get("activities", []) if isinstance(act_res, dict) else (act_res if isinstance(act_res, list) else [])
        if activities:
            last = activities[0]
            originator = (last.get("originator") or "").lower()
            if originator == "user":
                raise ValueError("Error: Please wait for the agent to reply before sending another message. (Use --force para ignorar)")

    res = c.send_message(session_id=clean_id, message=message)

    if as_json:
        print(json.dumps(res, indent=2, ensure_ascii=False))
        return res

    log("JULES", f"✅ Mensagem enviada com sucesso para a sessão {clean_id}!", Colors.GREEN)
    return res


# Alias retrocompatível
send_message = run_send_message


def main():
    p = argparse.ArgumentParser(description="Envia mensagem para uma sessão do Google Jules.")
    p.add_argument("session_id", nargs="?", help="ID ou URL da sessão do Jules.")
    p.add_argument("--session-id", "-s", dest="session_id_flag", help="ID ou URL da sessão (flag alternativa).")
    p.add_argument("--message", "-m", required=True, help="Texto da mensagem ou arquivo.")
    p.add_argument("--force", "-f", action="store_true", help="Força envio mesmo que a última mensagem já tenha sido do usuário.")
    p.add_argument("--json", action="store_true", help="Exibe a resposta em formato JSON puro.")
    args = p.parse_args()

    target_id = args.session_id or args.session_id_flag
    if not target_id:
        log_error("JULES", "ID da sessão é obrigatório.")
        sys.exit(1)

    try:
        run_send_message(
            session_id=target_id,
            message=args.message,
            force=args.force,
            as_json=args.json
        )
    except Exception as e:
        log_error("JULES", str(e))
        sys.exit(1)


if __name__ == "__main__":
    main()
