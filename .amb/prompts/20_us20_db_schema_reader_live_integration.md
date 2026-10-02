# 🎯 US-20: Integrar Método `inspect_live` em `DbSchemaReader`

## 👤 User Story
> **Como** desenvolvedor executando inspeção de arquitetura de dados no AMB,  
> **Quero** que a classe `DbSchemaReader` possua o método `inspect_live(target_table, explicit_path_or_uri)`,  
> **Para que** a leitura em tempo de execução descubra automaticamente bancos locais e unifique a experiência com a leitura estática de schemas.

---

## 📌 Critérios de Aceitação BDD

* **Cenário 1: Descoberta automática de arquivos de banco SQLite**
  * **Dado** um projeto que possui `dev.db` ou `local.sqlite` na raiz ou em `data/`;
  * **Quando** `reader.inspect_live()` for executado sem parâmetros;
  * **Então** deve localizar o arquivo, invocar `LiveDatabaseInspector().inspect_sqlite(...)` e formatar o resumo visual das tabelas.

* **Cenário 2: Suporte a caminho explícito**
  * **Dado** um caminho específico fornecido pelo usuário;
  * **Quando** `inspect_live(explicit_path_or_uri="banco_teste.db")` for chamado;
  * **Então** deve inspecionar exatamente o arquivo informado.

* **Cenário 3: Respeito ao limite de 300 linhas por arquivo**
  * **Dado** que `amb_cli/architecture/db_schema_reader.py` possui 154 linhas;
  * **Quando** a nova funcionalidade for integrada;
  * **Então** o arquivo deve permanecer estritamente abaixo de 200 linhas.

---

## 🛠️ Arquivos Alvo & Alterações Necessárias

### `amb_cli/architecture/db_schema_reader.py`
Adicionar o método `inspect_live` na classe `DbSchemaReader`:
```python
    def inspect_live(self, target_table: Optional[str] = None, explicit_path: Optional[str] = None) -> Dict[str, Any]:
        """Inspeciona o banco de dados local em tempo de execução via LiveDatabaseInspector."""
        from architecture.context_core.live_db_inspector import LiveDatabaseInspector
        inspector = LiveDatabaseInspector()

        db_file: Optional[Path] = None
        if explicit_path:
            db_file = Path(explicit_path)
            if not db_file.is_absolute():
                db_file = self.repo_root / db_file
        else:
            # Descoberta automática de SQLite na raiz ou pastas comuns
            candidates = list(self.repo_root.glob("*.db")) + list(self.repo_root.glob("*.sqlite*"))
            if candidates:
                db_file = candidates[0]

        if not db_file or not db_file.exists():
            return {"error": "Nenhum banco de dados SQLite local encontrado no projeto."}

        return inspector.inspect_sqlite(db_path=db_file, target_table=target_table)
```
Teto do arquivo: <= 190 linhas.

---

## 🔍 Comandos de Verificação Local
```bash
# Validar chamada inspect_live
python -c "from amb_cli.architecture.db_schema_reader import DbSchemaReader; r = DbSchemaReader(); print('Método existe:', hasattr(r, 'inspect_live'))"

# Executar testes existentes de db_schema_reader
pytest tests/test_db_schema_reader.py -v

# Validar conformidade de tamanho
python -m amb_cli.cli validate amb_cli/architecture/db_schema_reader.py
```

---

## 📋 Definition of Done (DoD)
- [ ] Método `inspect_live` adicionado à classe `DbSchemaReader`.
- [ ] Descoberta automática de arquivos `.db` e `.sqlite*` no repositório.
- [ ] Delegação limpa para `LiveDatabaseInspector`.
- [ ] Arquivo `db_schema_reader.py` mantido abaixo de 200 linhas.
- [ ] Suíte existente `pytest` 100% verde.
