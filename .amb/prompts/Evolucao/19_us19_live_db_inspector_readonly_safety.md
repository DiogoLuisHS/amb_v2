# 🎯 US-19: Invariante de Segurança Read-Only em `LiveDatabaseInspector`

## 👤 User Story
> **Como** administrador de banco de dados e mantenedor de integridade do AMB_V2,  
> **Quero** que o `LiveDatabaseInspector` valide rigorosamente a segurança de qualquer consulta ou comando,  
> **Para que** comandos de mutação (DML/DDL) sejam rejeitados preventivamente com `AmbError`, garantindo risco zero de perda ou corrupção de dados.

---

## 📌 Critérios de Aceitação BDD

* **Cenário 1: Rejeição incondicional de comandos DML (`INSERT`, `UPDATE`, `DELETE`)**
  * **Dado** uma instrução de consulta contendo `"INSERT INTO users VALUES (1, 'teste')"` ou `"DELETE FROM users"`;
  * **Quando** `inspector.validate_safety(query)` for executado;
  * **Então** deve lançar imediatamente `AmbError` com mensagem informando que a operação é estritamente Read-Only.

* **Cenário 2: Rejeição incondicional de comandos DDL (`DROP`, `ALTER`, `TRUNCATE`)**
  * **Dado** uma instrução contendo `"DROP TABLE users"` ou `"ALTER TABLE users ADD COLUMN pass TEXT"`;
  * **Quando** for validada;
  * **Então** deve lançar `AmbError` detalhando a palavra-chave proibida detectada.

* **Cenário 3: Aprovação de consultas legítimas de leitura**
  * **Dado** queries puramente informativas como `"SELECT * FROM sqlite_master"` ou `"PRAGMA table_info('users')"`;
  * **Quando** validadas;
  * **Então** o método deve retornar normalmente sem lançar exceções.

---

## 🛠️ Arquivos Alvo & Alterações Necessárias

### `amb_cli/architecture/context_core/live_db_inspector.py`
Adicionar o conjunto de palavras-chave proibidas e o método `validate_safety`:
```python
FORBIDDEN_KEYWORDS = {"insert", "update", "delete", "drop", "alter", "truncate", "create"}

    def validate_safety(self, query: str) -> None:
        """Valida que uma consulta ou comando SQL é estritamente de leitura (Read-Only)."""
        if not query:
            return
        cleaned = " " + " ".join(query.strip().lower().split()) + " "
        for word in FORBIDDEN_KEYWORDS:
            if f" {word} " in cleaned:
                raise AmbError(
                    f"Operação proibida: a inspeção de banco é estritamente Read-Only. Palavra-chave detectada: '{word.upper()}'."
                )
```
Teto do arquivo: <= 140 linhas.

---

## 🔍 Comandos de Verificação Local
```bash
# Validar bloqueio de segurança via terminal
python -c "from amb_cli.architecture.context_core.live_db_inspector import LiveDatabaseInspector; insp = LiveDatabaseInspector(); insp.validate_safety('SELECT * FROM users'); print('Select OK')"
python -c "from amb_cli.architecture.context_core.live_db_inspector import LiveDatabaseInspector; insp = LiveDatabaseInspector(); insp.validate_safety('DROP TABLE users')" 2>&1 | findstr "Operação proibida"

# Garantir integridade da suíte pytest
pytest -q

# Validar conformidade de tamanho
python -m amb_cli.cli validate amb_cli/architecture/context_core/live_db_inspector.py
```

---

## 📋 Definition of Done (DoD)
- [ ] Método `validate_safety` implementado com bloqueio de `FORBIDDEN_KEYWORDS`.
- [ ] Lançamento consistente de `AmbError`.
- [ ] Consultas benignas de leitura aprovadas sem falhas.
- [ ] Arquivo mantido abaixo de 140 linhas.
- [ ] Suíte global `pytest` continua 100% verde.
