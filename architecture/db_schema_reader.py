#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🏛️ AMB_V2 - Leitor Agnóstico de Schemas de Banco de Dados (Read-Only)
Localização: amb_v2/architecture/db_schema_reader.py
Responsabilidade Única: Inspecionar e catalogar tabelas, colunas, tipos e constraints
de schemas (Drizzle ORM, Prisma, etc.) no projeto ativo sem permissão de escrita.
"""

import os
import sys
import re
from pathlib import Path
from typing import List, Dict, Any, Optional

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

from config import Colors, find_repo_root, log_error


class DbSchemaReader:
    """Inspeciona e analisa arquivos de schema no repositório ativo."""

    @staticmethod
    def find_schema_dirs(root: str) -> List[Path]:
        """Localiza diretórios prováveis de schemas no projeto."""
        candidates = [
            Path(root) / "apps" / "api" / "src" / "db" / "schema",
            Path(root) / "apps" / "api" / "db" / "schema",
            Path(root) / "src" / "db" / "schema",
            Path(root) / "src" / "database" / "schema",
            Path(root) / "db" / "schema",
            Path(root) / "server" / "src" / "db" / "schema",
            Path(root) / "backend" / "src" / "db" / "schema",
        ]
        valid_dirs = [p for p in candidates if p.exists() and p.is_dir()]
        return valid_dirs

    @classmethod
    def list_schema_files(cls, root: str) -> List[Path]:
        """Lista todos os arquivos de schema TypeScript/JavaScript encontrados."""
        dirs = cls.find_schema_dirs(root)
        files = []
        for d in dirs:
            files.extend([f for f in d.glob("*.ts") if f.name != "index.ts"])
            files.extend([f for f in d.glob("*.js") if f.name != "index.js"])
        return sorted(list(set(files)))

    @staticmethod
    def parse_drizzle_schema(filepath: Path) -> List[Dict[str, Any]]:
        """Extrai definições de tabelas e colunas de arquivos Drizzle ORM."""
        try:
            content = filepath.read_text(encoding="utf-8", errors="replace")
        except Exception:
            return []

        tables = []
        pattern = re.compile(
            r"export\s+const\s+(\w+)\s*=\s*(?:sqliteTable|pgTable|mysqlTable)\(\s*['\"]([^'\"]+)['\"]\s*,\s*\{([^}]+)\}",
            re.MULTILINE | re.DOTALL
        )

        for match in pattern.finditer(content):
            var_name = match.group(1)
            table_name = match.group(2)
            columns_block = match.group(3)

            columns = []
            for line in columns_block.splitlines():
                line = line.strip()
                if not line or line.startswith("//"):
                    continue
                col_match = re.match(r"^(\w+)\s*:\s*(\w+)\((.*)\)", line)
                if col_match:
                    col_name = col_match.group(1)
                    col_type = col_match.group(2)
                    col_opts = col_match.group(3)
                    columns.append({
                        "name": col_name,
                        "type": col_type,
                        "options": col_opts.strip().rstrip(",")
                    })

            tables.append({
                "variable": var_name,
                "table_name": table_name,
                "file": filepath.name,
                "path": str(filepath),
                "columns": columns
            })

        return tables


def show_schema(filter_term: Optional[str] = None):
    """Exibe no terminal o catálogo de tabelas e colunas formatado."""
    root = find_repo_root()
    schema_files = DbSchemaReader.list_schema_files(root)

    if not schema_files:
        print(f"\n{Colors.YELLOW}[!] Nenhum diretório de schema Drizzle/DB encontrado em: {root}{Colors.RESET}")
        return

    all_tables = []
    for f in schema_files:
        all_tables.extend(DbSchemaReader.parse_drizzle_schema(f))

    if filter_term:
        ft = filter_term.lower().strip()
        filtered = [
            t for t in all_tables
            if ft in t["table_name"].lower()
            or ft in t["variable"].lower()
            or ft in t["file"].lower()
        ]
    else:
        filtered = all_tables

    print("\n" + "=" * 75)
    print(f"🏛️  {Colors.BOLD}{Colors.CYAN}CATÁLOGO DE SCHEMAS DO BANCO DE DADOS (READ-ONLY){Colors.RESET}")
    print(f"📁 Repositório: {Colors.GREEN}{root}{Colors.RESET}")
    print(f"{Colors.DIM}[NOTA PARA IA: Estes schemas são IMUTÁVEIS. Ajuste apenas Controllers e Frontend!]{Colors.RESET}")
    print("=" * 75)

    if not filtered:
        print(f"\n{Colors.YELLOW}Nenhuma tabela encontrada com o termo: '{filter_term}'{Colors.RESET}")
        print("\n📋 Tabelas disponíveis no projeto:")
        for t in all_tables:
            print(f"  • {Colors.BOLD}{t['table_name']}{Colors.RESET} (em {t['file']})")
        print()
        return

    for t in filtered:
        print(f"\n📦 TABELA: `{Colors.BOLD}{Colors.GREEN}{t['table_name']}{Colors.RESET}` (Variável: `{t['variable']}` | Arquivo: `{t['file']}`)")
        print("-" * 75)
        print(f"{'COLUNA':<25} | {'TIPO ORM':<15} | {'DETALHES / CONSTRAINTS'}")
        print("-" * 75)
        for col in t["columns"]:
            print(f"{col['name']:<25} | {col['type']:<15} | {col['options']}")

    print("\n" + "=" * 75)
    print(f"📊 Total de tabelas listadas: {Colors.BOLD}{len(filtered)}{Colors.RESET}")
    print("=" * 75 + "\n")


if __name__ == "__main__":
    term = sys.argv[1] if len(sys.argv) > 1 else None
    show_schema(term)
