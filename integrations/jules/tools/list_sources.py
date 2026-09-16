#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""⚡ Jules Tool: list_sources (Facade)"""
import sys
import os

from config.bootstrap import ensure_amb_env
ensure_amb_env()

from config import Colors, log, log_error
from integrations.jules.jules_client import JulesClient

def main():
    try:
        c = JulesClient()
        sources = c.list_sources()
        log("JULES", f"Fontes/Repositórios conectados ({len(sources)}):", Colors.CYAN)
        for s in sources:
            print(f"  • {s.get('name')}")
    except Exception as e:
        log_error("JULES", str(e)); sys.exit(1)

if __name__ == "__main__":
    main()
