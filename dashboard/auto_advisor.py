#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🤖 AMB_V2 - Auto Advisor (Facade)
Localização: amb_v2/dashboard/auto_advisor.py
Encaminha diretamente para a implementação centralizada em agents/auto_reply.py
"""

from config.bootstrap import ensure_amb_env
ensure_amb_env()

from auto_reply import main  # noqa: E402

if __name__ == "__main__":
    main()
