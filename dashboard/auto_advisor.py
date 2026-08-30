#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🤖 AMB_V2 - Auto Advisor (Facade)
Localização: amb_v2/dashboard/auto_advisor.py
Encaminha diretamente para a implementação centralizada em agents/auto_reply.py
"""

import sys
import os

_cur = os.path.dirname(os.path.abspath(__file__))
while _cur and os.path.basename(_cur) != "amb_v2":
    _p = os.path.dirname(_cur)
    if _p == _cur:
        break
    _cur = _p
for _sub in ["config", "agents", "dashboard", "integrations/jules", "integrations/antigravity"]:
    _p = os.path.normpath(os.path.join(_cur, *_sub.split("/")))
    if os.path.exists(_p) and _p not in sys.path:
        sys.path.insert(0, _p)

from auto_reply import run_auto_advisor, auto_reply_all_pending, interactive_advisor_menu, main

if __name__ == "__main__":
    main()
