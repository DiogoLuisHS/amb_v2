#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Construtor de Contexto e Roteiro de Arquivos para IA.
Rastreia dependências e gera a ordem de leitura por camadas.
"""

import os
import sys
import json
import copy
from pathlib import Path
from collections import defaultdict
from typing import Set, Dict, List, Any, Optional, Tuple

from config.bootstrap import ensure_amb_env
ensure_amb_env()

from config import find_repo_root

from amb_cli.architecture.context_core.constants import (
    CODE_EXTENSIONS,
    IGNORE_DIRS,
    JS_TS_IMPORT_PATTERNS,
    LAYERS_CONFIG,
)
from amb_cli.architecture.context_core.utils import determine_file_layer


class AIContextBuilder:
    LAYERS_CONFIG: Dict[str, Any] = LAYERS_CONFIG

    def _determine_file_layer(self, file: str) -> str:
        return determine_file_layer(file)

    def __init__(self, root_dir: Path) -> None:
        self.root_dir: Path = root_dir.resolve()
        self.file_map: Set[str] = set()
        self.edges: List[Dict[str, str]] = []
        self.nodes: Set[str] = set()
        self.adj_down: Dict[str, List[str]] = defaultdict(list)
        self.adj_up: Dict[str, List[str]] = defaultdict(list)

    def scan_files(self) -> None:
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
    ) -> Tuple[str, bool]:
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

    def _find_matching_file(self, base_path: Any) -> Optional[str]:
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

    def extract_dependencies(self, rel_path: str) -> None:
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

    def analyze(self) -> None:
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

        exists_cache: Dict[str, bool] = {}

        def path_exists(p: str) -> bool:
            if p not in exists_cache:
                exists_cache[p] = (self.root_dir / p).exists()
            return exists_cache[p]

        for core in list(core_files):
            for down in self.adj_down.get(core, []):
                if not down.startswith("@") and path_exists(down):
                    result.add(down)
            for up in self.adj_up.get(core, []):
                if not up.startswith("@") and path_exists(up):
                    result.add(up)

        return result

    def classify_and_order_files(
        self, file_set: Set[str], query: str = ""
    ) -> Dict[str, Any]:
        layers = copy.deepcopy(self.LAYERS_CONFIG)

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

            layer_key = self._determine_file_layer(file)
            layers[layer_key]["files"].append(file_meta)

        return layers

    def generate_markdown(self, query: str, layers: Dict[str, Any]) -> str:
        total_files = sum(len(layer["files"]) for layer in layers.values())

        md = []
        md.append(
            f"# 🧭 ROTEIRO DE LEITURA PARA A IA — MÓDULO / CONTEXTO: `{query.upper()}`\n"
        )
        md.append(
            "> **Instrução para a IA:** Para analisar, debugar ou implementar qualquer mudança neste módulo sem se perder no projeto, siga rigorosamente a leitura dos arquivos na ordem arquitetural abaixo (do banco de dados até a interface do usuário):\n"
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


def generate_context(target: str, output_json: bool = False) -> None:
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
            "total_files": sum(len(layer["files"]) for layer in layers.values()),
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
