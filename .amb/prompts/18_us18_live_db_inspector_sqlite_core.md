# 🎯 US-18: Introspecção Dinâmica de SQLite Nativo em `LiveDatabaseInspector`

## 👤 User Story
> **Como** desenvolvedor ou agente autônomo analisando um projeto com banco local,  
> **Quero** que o módulo `amb_cli/architecture/context_core/live_db_inspector.py` inspecione tabelas e colunas reais de bancos SQLite via módulo padrão `sqlite3`,  
> **Para que** eu possa verificar a estrutura física de dados persistida sem instalar drivers externos compilados.

---

## 📌 Critérios de Aceitação BDD

* **Cenário 1: Introspecção de tabelas e colunas em banco SQLite**
  * **Dado** um arquivo de banco de dados SQLite existente no disco;
  * **Quando** `LiveDatabaseInspector().inspect_sqlite(db_path)` for chamado;
  * **Então** deve conectar em modo estritamente read-only (`mode=ro`);
  * **E** deve consultar `sqlite_master` para listar as tabelas de usuário (ignorando tabelas internas `sqlite_%`);
  * **E** deve consultar `PRAGMA table_info(...)` retornando colunas com nome, tipo, `not_null` e `primary_key`.

* **Cenário 2: Tratamento de arquivo inexistente**
  * **Dado** um caminho para arquivo que não existe;
  * **Quando** o método for executado;
  * **Então** deve lançar `AmbError("Arquivo de banco de dados não encontrado: ...")`.

---

## 🛠️ Arquivos Alvo & Alterações Necessárias

### Criar Novo Arquivo: `amb_cli/architecture/context_core/live_db_inspector.py`
```python
# -*- coding: utf-8 -*-
"""Módulo de introspecção dinâmica em tempo de execução para bancos de dados locais."""

import sqlite3
from pathlib import Path
from typing import Dict, Any, List, Optional
from core import AmbError


class LiveDatabaseInspector:
    """Introspecção segura em tempo de execução para bancos relacionais locais."""

    def inspect_sqlite(self, db_path: Path, target_table: Optional[str] = None) -> Dict[str, Any]:
        """Inspeciona tabelas e colunas de bancos de dados SQLite locais."""
        if not db_path or not db_path.exists():
            raise AmbError(f"Arquivo de banco de dados não encontrado: {db_path}")

        tables_result: Dict[str, Any] = {}
        conn_uri = f"file:{db_path.resolve()}?mode=ro"
        conn = sqlite3.connect(conn_uri, uri=True)
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';")
            table_names = [row[0] for row in cursor.fetchall()]

            if target_table:
                table_names = [t for t in table_names if target_table.lower() in t.lower()]

            for t_name in table_names:
                cursor.execute(f"PRAGMA table_info('{t_name}');")
                columns = []
                for col in cursor.fetchall():
                    columns.append({
                        "name": col[1],
                        "type": col[2] or "TEXT",
                        "not_null": bool(col[3]),
                        "primary_key": bool(col[5])
                    })
                tables_result[t_name] = {"columns": columns}
        finally:
            conn.close()

        return tables_result
```
Teto do arquivo: <= 120 linhas.

---

## 🔍 Comandos de Verificação Local
```bash
# Validar importação e criação de banco sqlite em memória para teste rápido
python -c "import tempfile, sqlite3, pathlib; from amb_cli.architecture.context_core.live_db_inspector import LiveDatabaseInspector; tmp = pathlib.Path(tempfile.mktemp('.db')); conn = sqlite3.connect(str(tmp)); conn.execute('CREATE TABLE users (id INTEGER PRIMARY KEY, email TEXT)'); conn.close(); print('Tabelas:', LiveDatabaseInspector().inspect_sqlite(tmp)); tmp.unlink()"

# Garantir integridade da suíte pytest
pytest -q

# Validar conformidade de tamanho
python -m amb_cli.cli validate amb_cli/architecture/context_core/live_db_inspector.py
```

---

## 📋 Definition of Done (DoD)
- [ ] Arquivo `amb_cli/architecture/context_core/live_db_inspector.py` criado.
- [ ] Método `inspect_sqlite` conectando em `mode=ro`.
- [ ] Extração de tabelas via `sqlite_master` e colunas via `PRAGMA table_info`.
- [ ] Arquivo com menos de 100 linhas.
- [ ] Suíte global `pytest` continua 100% verde.
