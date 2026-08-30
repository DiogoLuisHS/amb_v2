#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🧠 AMB_V2 - Wrapper de Agentes (SRP)
Localização: amb_v2/agents/local_agent_runner.py
Delega a execução para a ferramenta oficial de runner de personas.
"""
import os
import sys

_p = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "integrations", "antigravity", "tools"))
if os.path.exists(_p) and _p not in sys.path:
    sys.path.insert(0, _p)

import local_agent_runner

if __name__ == "__main__":
    local_agent_runner.main()
