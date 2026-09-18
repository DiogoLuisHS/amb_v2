#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Script utilitário de validação rápida (smoke check) do ambiente e bootstrap."""
import amb_bootstrap
from ai_context_builder import generate_context
from workspace import get_repo_name, find_repo_root

if __name__ == "__main__":
    print(f"✅ Bootstrap inicializado com sucesso.")
    print(f"📁 Repositório: {get_repo_name()} ({find_repo_root()})")
    print(f"🧩 ai_context_builder: {generate_context.__name__}")

