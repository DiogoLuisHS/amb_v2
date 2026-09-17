import re
from typing import Dict, Any

CODE_EXTENSIONS = {
    ".ts",
    ".tsx",
    ".js",
    ".jsx",
    ".mjs",
    ".cjs",
    ".py",
    ".css",
    ".scss",
    ".json",
    ".sql",
}
IGNORE_DIRS = {
    "node_modules",
    "dist",
    "build",
    ".git",
    ".antigravity",
    ".jules",
    ".amb",
    ".husky",
    ".vscode",
    "__pycache__",
    ".next",
    ".cache",
    "coverage",
}

JS_TS_IMPORT_PATTERNS = [
    re.compile(
        r"""(?:import|export)\s+(?:[\w\*\$_\s{},]*\s+from\s+)?['"]([^'"]+)['"]"""
    ),
    re.compile(r"""require\s*\(\s*['"]([^'"]+)['"]\s*\)"""),
    re.compile(r"""import\s*\(\s*['"]([^'"]+)['"]\s*\)"""),
]

LAYERS_CONFIG: Dict[str, Any] = {
    "1_database_schemas": {
        "title": "1. Banco de Dados & Schemas (Drizzle / DB Tables)",
        "icon": "🗄️",
        "files": [],
    },
    "2_repositories": {
        "title": "2. Repositórios de Acesso a Dados (SQL / Queries)",
        "icon": "💾",
        "files": [],
    },
    "3_services": {
        "title": "3. Regras de Negócio & Serviços (Business Logic)",
        "icon": "⚙️",
        "files": [],
    },
    "4_controllers": {
        "title": "4. Controladores & Validações de Entrada (Zod / Schemas)",
        "icon": "🎮",
        "files": [],
    },
    "5_routers_api": {
        "title": "5. Rotas & Endpoints da API (HTTP / Hono / Express)",
        "icon": "🌐",
        "files": [],
    },
    "6_frontend_hooks_api": {
        "title": "6. Frontend Services, Hooks & Chamadas de API",
        "icon": "🪝",
        "files": [],
    },
    "7_frontend_components": {
        "title": "7. Componentes de UI & Modais",
        "icon": "🧩",
        "files": [],
    },
    "8_frontend_pages": {
        "title": "8. Páginas Web & Views Principais",
        "icon": "🖥️",
        "files": [],
    },
    "9_entrypoints_config": {
        "title": "9. Pontos de Entrada & Configurações Globais",
        "icon": "🚀",
        "files": [],
    },
}
