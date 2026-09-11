#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🧭 AMB_V2 - Construtor de Contexto e Roteiro de Arquivos para IA (Agnóstico)
Localização: amb_v2/architecture/ai_context_builder.py
Responsabilidade Única: Rastrear dependências de um módulo/arquivo e gerar a ordem
exata de leitura por camadas arquiteturais (DB -> Repos -> Services -> Controllers -> UI).
"""

import os
import sys
import re
import json
import argparse
from pathlib import Path
from collections import defaultdict
from typing import Set, Dict, List, Any, Optional

# Bootstrap dinâmico de caminhos amb_v2
_cur = os.path.dirname(os.path.abspath(__file__))
while _cur and os.path.basename(_cur) != "amb_v2":
    _p = os.path.dirname(_cur)
    if _p == _cur:
        break
    _cur = _p
_AMB = _cur

for _sub in ["config", "agents", "architecture", "pipeline", "integrations"]:
    _p = os.path.normpath(os.path.join(_AMB, *_sub.split("/")))
    if os.path.exists(_p) and _p not in sys.path:
        sys.path.insert(0, _p)

from config import Colors, find_repo_root

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


class AIContextBuilder:
    def __init__(self, root_dir: Path):
        self.root_dir = root_dir.resolve()
        self.file_map = set()
        self.edges = []
        self.nodes = set()
        self.adj_down = defaultdict(list)
        self.adj_up = defaultdict(list)

    def scan_files(self):
        for root, dirs, files in os.walk(self.root_dir):
            dirs[:] = [
                d for d in dirs if d not in IGNORE_DIRS and not d.startswith(".")
            ]
            for file in files:
                ext = Path(file).suffix.lower()
                if ext in CODE_EXTENSIONS:
                    full_path = Path(root) / file
                    rel_path = full_path.relative_to(self.root_dir).as_posix()
                    self.file_map.add(rel_path)

    def resolve_import_path(
        self, current_file: str, import_str: str
    ) -> tuple[str, bool]:
        import_str = import_str.strip()
        current_dir = Path(current_file).parent

        if import_str.startswith("./") or import_str.startswith("../"):
            target_candidate = current_dir / import_str
            resolved = self._find_matching_file(target_candidate)
            if resolved:
                return resolved, False
            return (current_dir / import_str).as_posix(), False

        if import_str.startswith("@/"):
            alias_path = import_str[2:]
            candidates = [
                Path("apps/api/src") / alias_path,
                Path("apps/api") / alias_path,
                Path("apps/web/src") / alias_path,
                Path("apps/web") / alias_path,
                Path("src") / alias_path,
            ]
            for candidate in candidates:
                resolved = self._find_matching_file(candidate)
                if resolved:
                    return resolved, False
            return f"@{alias_path}", False

        return import_str, True

    def _find_matching_file(self, base_path) -> Optional[str]:
        norm = os.path.normpath(str(base_path)).replace("\\", "/")
        if norm.startswith("./"):
            norm = norm[2:]

        if norm in self.file_map:
            return norm

        stem = norm
        for ext in [".js", ".jsx", ".mjs", ".cjs", ".ts", ".tsx", ".json", ".css"]:
            if norm.endswith(ext):
                stem = norm[: -len(ext)]
                break

        for ext in [".ts", ".tsx", ".js", ".jsx", ".mjs", ".cjs", ".css", ".json"]:
            candidate = f"{stem}{ext}"
            if candidate in self.file_map:
                return candidate

        for ext in [".ts", ".tsx", ".js", ".jsx", ".mjs", ".cjs"]:
            candidate = f"{norm}/index{ext}"
            if candidate in self.file_map:
                return candidate
            candidate_stem = f"{stem}/index{ext}"
            if candidate_stem in self.file_map:
                return candidate_stem

        return None

    def extract_dependencies(self, rel_path: str):
        full_path = self.root_dir / rel_path
        try:
            with open(full_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
        except Exception:
            return

        ext = Path(rel_path).suffix.lower()
        if ext not in {".ts", ".tsx", ".js", ".jsx", ".mjs", ".cjs"}:
            return

        for pattern in JS_TS_IMPORT_PATTERNS:
            for match in pattern.finditer(content):
                target, is_external = self.resolve_import_path(rel_path, match.group(1))
                if is_external:
                    continue
                self.edges.append({"source": rel_path, "target": target})
                self.nodes.add(rel_path)
                self.nodes.add(target)
                if target not in self.adj_down[rel_path]:
                    self.adj_down[rel_path].append(target)
                if rel_path not in self.adj_up[target]:
                    self.adj_up[target].append(rel_path)

    def analyze(self):
        self.scan_files()
        for file in sorted(self.file_map):
            self.extract_dependencies(file)

    def find_matching_nodes(self, query: str) -> List[str]:
        clean_q = query.replace("\\", "/").strip().lower()
        matches = []
        for n in self.nodes:
            if clean_q == n.lower() or clean_q in n.lower():
                matches.append(n)
        matches.sort(key=lambda x: (len(x), x))
        return matches

    def trace_module_chain(self, query: str) -> Set[str]:
        clean_q = query.replace("\\", "/").strip().lower()
        core_files = {n for n in self.nodes if clean_q in n.lower()}

        if not core_files:
            matching = self.find_matching_nodes(query)
            core_files = set(matching[:5])

        result = set(core_files)

        for core in list(core_files):
            for down in self.adj_down.get(core, []):
                if not down.startswith("@") and (self.root_dir / down).exists():
                    result.add(down)
            for up in self.adj_up.get(core, []):
                if not up.startswith("@") and (self.root_dir / up).exists():
                    result.add(up)

        return result

    def classify_and_order_files(
        self, file_set: Set[str], query: str = ""
    ) -> Dict[str, Any]:
        layers = {
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

        clean_q = query.lower()

        for file in sorted(file_set):
            in_cnt = len(self.adj_up.get(file, []))
            out_cnt = len(self.adj_down.get(file, []))
            is_core = clean_q in file.lower() if clean_q else False

            file_meta = {
                "path": file,
                "basename": Path(file).name,
                "in_count": in_cnt,
                "out_count": out_cnt,
                "is_core": is_core,
            }

            if "db/schema" in file or (
                "schema" in file and ("apps/api/src/db" in file or "src/db" in file)
            ):
                layers["1_database_schemas"]["files"].append(file_meta)
            elif "repositories" in file or "repository" in file:
                layers["2_repositories"]["files"].append(file_meta)
            elif "services" in file or "service" in file:
                layers["3_services"]["files"].append(file_meta)
            elif "controllers" in file or "controller" in file:
                layers["4_controllers"]["files"].append(file_meta)
            elif "routers" in file or "router" in file or "routes" in file:
                layers["5_routers_api"]["files"].append(file_meta)
            elif ("apps/web" in file or "web" in file or "frontend" in file) and (
                "hooks" in file or "services" in file or "api" in file
            ):
                layers["6_frontend_hooks_api"]["files"].append(file_meta)
            elif (
                "apps/web" in file or "web" in file or "frontend" in file
            ) and "components" in file:
                layers["7_frontend_components"]["files"].append(file_meta)
            elif ("apps/web" in file or "web" in file or "frontend" in file) and (
                "pages" in file or "views" in file
            ):
                layers["8_frontend_pages"]["files"].append(file_meta)
            else:
                layers["9_entrypoints_config"]["files"].append(file_meta)

        return layers

    def generate_markdown(self, query: str, layers: Dict[str, Any]) -> str:
        total_files = sum(len(l["files"]) for l in layers.values())

        md = []
        md.append(
            f"# 🧭 ROTEIRO DE LEITURA PARA A IA — MÓDULO / CONTEXTO: `{query.upper()}`\n"
        )
        md.append(
            f"> **Instrução para a IA:** Para analisar, debugar ou implementar qualquer mudança neste módulo sem se perder no projeto, siga rigorosamente a leitura dos arquivos na ordem arquitetural abaixo (do banco de dados até a interface do usuário):\n"
        )
        md.append(
            f"**Total de arquivos essenciais:** {total_files} arquivos mapeados\n"
        )
        md.append("---\n")

        for key, layer_info in layers.items():
            if not layer_info["files"]:
                continue
            md.append(
                f"### {layer_info['icon']} {layer_info['title']} ({len(layer_info['files'])} arquivo{'s' if len(layer_info['files']) > 1 else ''})\n"
            )
            for f in layer_info["files"]:
                core_badge = " ⭐ **[ARQUIVO PRINCIPAL]**" if f["is_core"] else ""
                md.append(
                    f"- [`{f['path']}`](file:///{f['path']}){core_badge} — *(Consultado por {f['in_count']} | Consulta {f['out_count']})*"
                )
            md.append("")

        md.append("---\n")
        md.append("### 💡 Ordem de Execução & Dependência:")
        md.append(
            "1. **Schema (`db/schema/`):** Define a estrutura das tabelas e os tipos."
        )
        md.append("2. **Repositories (`repositories/`):** Executam consultas SQL.")
        md.append("3. **Services (`services/`):** Contêm a lógica de negócio.")
        md.append(
            "4. **Controllers & Routers (`controllers/`, `routers/`):** Endpoints HTTP e validações."
        )
        md.append(
            "5. **Frontend Hooks (`hooks/`):** Gerenciam estado e chamadas de API."
        )
        md.append(
            "6. **UI Components & Pages (`components/`, `pages/`):** Renderizam as interfaces."
        )

        return "\n".join(md)


def generate_context(target: str, output_json: bool = False):
    """Gera o contexto arquitetural do módulo no terminal."""
    root = find_repo_root()
    builder = AIContextBuilder(Path(root))
    builder.analyze()

    query = target or "agenda"
    file_chain = builder.trace_module_chain(query)
    layers = builder.classify_and_order_files(file_chain, query)

    if output_json:
        result_json = {
            "query": query,
            "total_files": sum(len(l["files"]) for l in layers.values()),
            "layers": layers,
        }
        print(json.dumps(result_json, indent=2, ensure_ascii=False))
    else:
        markdown_output = builder.generate_markdown(query, layers)
        print(markdown_output)


if __name__ == "__main__":
    t = sys.argv[1] if len(sys.argv) > 1 else "agenda"
    is_json = "--json" in sys.argv
    generate_context(t, output_json=is_json)
