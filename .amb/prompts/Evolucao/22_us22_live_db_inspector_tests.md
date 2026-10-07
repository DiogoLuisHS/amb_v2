# 🎯 US-22: Suíte de Testes Unitários Dedicada para `LiveDatabaseInspector`

## 👤 User Story
> **Como** engenheiro de testes do AMB_V2,  
> **Quero** um novo arquivo de testes `tests/test_live_db_inspector.py` cobrindo a introspecção e o bloqueio de segurança Read-Only,  
> **Para que** tenhamos certeza automatizada de que a leitura de banco é precisa e 100% segura contra comandos mutativos.

---

## 📌 Critérios de Aceitação BDD

* **Cenário 1: Teste de introspecção com banco SQLite temporário**
  * **Dado** um banco SQLite em arquivo temporário com tabela `users` contendo `id INTEGER PRIMARY KEY`, `name TEXT` e `email TEXT NOT NULL`;
  * **Quando** `inspect_sqlite` for invocado;
  * **Então** deve retornar a estrutura contendo os campos com tipos e flags corretas.

* **Cenário 2: Teste de bloqueio de segurança Read-Only**
  * **Dado** strings contendo instruções maliciosas (`INSERT INTO`, `DROP TABLE`, `UPDATE`, `DELETE`);
  * **Quando** `validate_safety` for chamado;
  * **Então** deve disparar `AmbError` bloqueando a execução imediatamente.

* **Cenário 3: Teste de filtro por tabela específica**
  * **Dado** um banco com tabelas `users` e `products`;
  * **Quando** `inspect_sqlite(..., target_table="users")` for chamado;
  * **Então** apenas `users` deve constar no dicionário retornado.

---

## 🛠️ Arquivos Alvo & Alterações Necessárias

### Criar Novo Arquivo: `tests/test_live_db_inspector.py`
```python
# -*- coding: utf-8 -*-
"""Testes unitários dedicados para o módulo LiveDatabaseInspector."""

import sys
import sqlite3
import tempfile
from pathlib import Path
import pytest

_root = Path(__file__).resolve().parent.parent
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))
from core.bootstrap import ensure_amb_env
ensure_amb_env()

from core import AmbError
from architecture.context_core.live_db_inspector import LiveDatabaseInspector


def test_inspect_sqlite_tables_and_columns():
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
        db_path = Path(tmp.name)

    try:
        conn = sqlite3.connect(str(db_path))
        conn.execute("CREATE TABLE accounts (id INTEGER PRIMARY KEY, email TEXT NOT NULL, balance REAL)")
        conn.execute("CREATE TABLE logs (id INTEGER PRIMARY KEY, msg TEXT)")
        conn.close()

        inspector = LiveDatabaseInspector()
        result = inspector.inspect_sqlite(db_path)

        assert "accounts" in result
        assert "logs" in result

        cols = {c["name"]: c for c in result["accounts"]["columns"]}
        assert cols["id"]["primary_key"] is True
        assert cols["email"]["not_null"] is True
        assert "TEXT" in cols["email"]["type"]
    finally:
        if db_path.exists():
            db_path.unlink()


def test_safety_blocks_dml_and_ddl():
    inspector = LiveDatabaseInspector()

    # Comandos proibidos devem falhar com AmbError
    with pytest.raises(AmbError):
        inspector.validate_safety("INSERT INTO users (id) VALUES (1)")

    with pytest.raises(AmbError):
        inspector.validate_safety("DROP TABLE users")

    with pytest.raises(AmbError):
        inspector.validate_safety("UPDATE accounts SET balance = 0")

    with pytest.raises(AmbError):
        inspector.validate_safety("DELETE FROM accounts")


def test_safety_allows_safe_queries():
    inspector = LiveDatabaseInspector()
    # Não deve lançar exceção
    inspector.validate_safety("SELECT * FROM sqlite_master")
    inspector.validate_safety("PRAGMA table_info('users')")


def test_filter_target_table():
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
        db_path = Path(tmp.name)

    try:
        conn = sqlite3.connect(str(db_path))
        conn.execute("CREATE TABLE orders (id INTEGER PRIMARY KEY)")
        conn.execute("CREATE TABLE customers (id INTEGER PRIMARY KEY)")
        conn.close()

        inspector = LiveDatabaseInspector()
        result = inspector.inspect_sqlite(db_path, target_table="orders")
        assert "orders" in result
        assert "customers" not in result
    finally:
        if db_path.exists():
            db_path.unlink()


def test_missing_db_raises_amb_error():
    inspector = LiveDatabaseInspector()
    with pytest.raises(AmbError):
        inspector.inspect_sqlite(Path("caminho_inexistente_12345.db"))
```
Teto do arquivo: <= 120 linhas.

---

## 🔍 Comandos de Verificação Local
```bash
# 1. Executar os novos testes dedicados do live db inspector
pytest tests/test_live_db_inspector.py -v

# 2. Executar toda a suíte de testes de schema
pytest tests/test_live_db_inspector.py tests/test_db_schema_reader.py -v

# 3. Executar toda a suíte pytest
pytest -q

# 4. Validar limites de linhas
python -m amb_cli.cli validate tests/test_live_db_inspector.py
```

---

## 📋 Definition of Done (DoD)
- [ ] Arquivo `tests/test_live_db_inspector.py` criado com 5+ testes unitários.
- [ ] 100% de aprovação em `pytest tests/test_live_db_inspector.py`.
- [ ] Invariante de segurança Read-Only comprovado com rejeição de DML/DDL.
- [ ] Suíte global `pytest` continua 100% passando.
