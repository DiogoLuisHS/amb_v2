#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Módulo de resolução de caminhos de importação JS/TS para o AI Context Builder.
Responsabilidade Única: Resolver caminhos relativos e aliases (@/) para arquivos reais no file_map.
"""

import os
from pathlib import Path
from typing import Set, Tuple, Optional, Any


class ImportResolver:
    """Resolve caminhos de import para caminhos canônicos no repositório."""

    @staticmethod
    def find_matching_file(file_map: Set[str], base_path: Any) -> Optional[str]:
        norm = os.path.normpath(str(base_path)).replace("\\", "/")
        if norm.startswith("./"):
            norm = norm[2:]

        if norm in file_map:
            return norm

        stem = norm
        for ext in [".js", ".jsx", ".mjs", ".cjs", ".ts", ".tsx", ".json", ".css"]:
            if norm.endswith(ext):
                stem = norm[: -len(ext)]
                break

        for ext in [".ts", ".tsx", ".js", ".jsx", ".mjs", ".cjs", ".css", ".json"]:
            candidate = f"{stem}{ext}"
            if candidate in file_map:
                return candidate

        for ext in [".ts", ".tsx", ".js", ".jsx", ".mjs", ".cjs"]:
            candidate = f"{norm}/index{ext}"
            if candidate in file_map:
                return candidate
            candidate_stem = f"{stem}/index{ext}"
            if candidate_stem in file_map:
                return candidate_stem

        return None

    @classmethod
    def resolve_import_path(
        cls, file_map: Set[str], current_file: str, import_str: str
    ) -> Tuple[str, bool]:
        import_str = import_str.strip()
        current_dir = Path(current_file).parent

        if import_str.startswith("./") or import_str.startswith("../"):
            target_candidate = current_dir / import_str
            resolved = cls.find_matching_file(file_map, target_candidate)
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
                resolved = cls.find_matching_file(file_map, candidate)
                if resolved:
                    return resolved, False
            return f"@{alias_path}", False

        return import_str, True
