# -*- coding: utf-8 -*-
"""Unit tests for architecture/ai_context_builder.py."""

import sys
from pathlib import Path

# Add project root to sys.path
_root = Path(__file__).resolve().parent.parent
for sub in ["config", "agents", "architecture", "pipeline", "integrations"]:
    p = str(_root / sub)
    if p not in sys.path:
        sys.path.insert(0, p)
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))

from ai_context_builder import AIContextBuilder


def test_determine_file_layer():
    builder = AIContextBuilder(_root)

    assert builder._determine_file_layer("apps/api/src/db/schema/users.ts") == "1_database_schemas"
    assert builder._determine_file_layer("apps/api/src/repositories/user.repo.ts") == "2_repositories"
    assert builder._determine_file_layer("apps/api/src/services/user.service.ts") == "3_services"
    assert builder._determine_file_layer("apps/api/src/controllers/auth.controller.ts") == "4_controllers"
    assert builder._determine_file_layer("apps/api/src/routes/auth.routes.ts") == "5_routers_api"
    assert builder._determine_file_layer("apps/web/src/components/Header.tsx") == "7_frontend_components"
    assert builder._determine_file_layer("apps/web/src/pages/Dashboard.tsx") == "8_frontend_pages"
    assert builder._determine_file_layer("package.json") == "9_entrypoints_config"


def test_classify_and_order_files_isolation():
    builder = AIContextBuilder(_root)

    files_call1 = {"apps/api/src/db/schema/users.ts", "apps/api/src/services/user.service.ts"}
    layers1 = builder.classify_and_order_files(files_call1, query="user")

    assert len(layers1["1_database_schemas"]["files"]) == 1
    assert len(layers1["3_services"]["files"]) == 1

    # Segunda chamada com conjunto diferente de arquivos: não deve conter os arquivos da chamada anterior
    files_call2 = {"apps/web/src/pages/Dashboard.tsx"}
    layers2 = builder.classify_and_order_files(files_call2, query="")

    assert len(layers2["1_database_schemas"]["files"]) == 0
    assert len(layers2["3_services"]["files"]) == 0
    assert len(layers2["8_frontend_pages"]["files"]) == 1
