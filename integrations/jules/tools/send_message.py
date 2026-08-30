#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
⚡ AMB_V2 - Jules SDK: Envio Direto de Mensagem para o Chat (SRP)
Localização: amb_v2/integrations/jules/tools/send_message.py
Responsabilidade Única: Despachar uma mensagem ou resposta textual direta para uma sessão Jules.
"""

import os
import sys
import json
import argparse

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

from config import Colors, log, log_error
from jules_client import JulesClient


def main():
    parser = argparse.ArgumentParser(description="Envia uma mensagem de resposta para o agente em uma sessão Jules.")
    parser.add_argument("--session-id", "-s", required=True, help="ID da sessão Jules.")
    parser.add_argument("--text", "-t", required=True, help="Texto da mensagem/orientação para o agente.")
    parser.add_argument("--json", action="store_true", help="Retorna saída JSON.")

    args = parser.parse_args()

    try:
        client = JulesClient()
        log("JULES-CHAT", f"Enviando mensagem para sessão {args.session_id}...", Colors.CYAN)
        res = client.send_message(session_id=args.session_id, message=args.text)

        if args.json:
            print(json.dumps(res, indent=2))
        else:
            log("JULES-CHAT", "✅ Mensagem enviada com sucesso ao chat do agente!", Colors.GREEN)
    except Exception as e:
        log_error("JULES-CHAT", str(e))
        sys.exit(1)


if __name__ == "__main__":
    main()
