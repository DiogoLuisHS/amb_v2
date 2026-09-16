#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""⚡ Jules Tool: create_session (Facade)"""
import sys
import os
import argparse

from config.bootstrap import ensure_amb_env
ensure_amb_env()

from config import Colors, log, log_error
from integrations.jules.jules_client import JulesClient

def create_session(prompt: str, title: str = None, source_name: str = None, client: JulesClient = None):
    if os.path.isfile(prompt):
        try:
            with open(prompt, "r", encoding="utf-8") as f:
                prompt = f.read()
        except Exception:
            pass
    c = client or JulesClient()
    return c.create_session(prompt=prompt, title=title, source_name=source_name)

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--prompt", "-p", required=True)
    p.add_argument("--title", "-t")
    args = p.parse_args()
    try:
        res = create_session(prompt=args.prompt, title=args.title)
        sid = res.get("name", "").split("/")[-1] or res.get("id")
        log("JULES", f"Sessão criada: {sid}", Colors.GREEN)
    except Exception as e:
        log_error("JULES", str(e)); sys.exit(1)

if __name__ == "__main__":
    main()
