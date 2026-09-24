# 🎯 Task: Introspecção Dinâmica de Banco com MCP Toolbox (`amb schema --live`)

## 📌 Contexto & Responsabilidade Única (SRP)
O **Google MCP Toolbox for Databases** (`googleapis/mcp-toolbox`) é um gateway universal seguro para conectar LLMs a bancos relacionais (PostgreSQL, MySQL, SQLite, AlloyDB) com pooling e esquemas tipados.
Atualmente, o comando `amb schema` no AMB realiza leitura estática de arquivos de código (Drizzle, Prisma, migrations SQL). Em projetos em desenvolvimento, os desenvolvedores e agentes frequentemente precisam inspecionar o estado real do banco de dados (tabelas criadas, índices, constraints e tipos) para garantir que migrations foram aplicadas.

Sua missão é criar o módulo de introspecção dinâmico em `amb_cli/architecture/context_core/live_db_inspector.py` e integrá-lo ao `amb schema` via flag `--live`, mantendo a regra estrita de operação **Read-Only** (apenas inspeção de metadados, sem mutação de dados).

---

## 🛠️ Arquivos Alvo & Alterações Necessárias

### 1. Novo Módulo: `amb_cli/architecture/context_core/live_db_inspector.py`
- Crie a classe `LiveDatabaseInspector`:
  - `inspect_sqlite(db_path: Path) -> Dict[str, Any]`: Lê tabelas, colunas e foreign keys de bancos SQLite locais (`sqlite_master` / `PRAGMA table_info`).
  - `inspect_database(connection_uri: str) -> Dict[str, Any]`: Introspecção padrão para conexões locais (PostgreSQL, MySQL ou SQLite) obtendo catálogo estruturado de tabelas e colunas.
  - **Invariante de Segurança Crítico:** Proibição de comandos DML/DDL (`INSERT`, `UPDATE`, `DELETE`, `DROP`). Todas as consultas devem ser estritamente de leitura de catálogo (`information_schema` ou `PRAGMA`).
  - Mantenha o arquivo estritamente <= 250 linhas.

### 2. Integrar em `amb_cli/architecture/db_schema_reader.py`
- Atualize a função `read_db_schemas(...)` para aceitar o parâmetro opcional `live: bool = False`:
  - Se `live=True`, detecta arquivos `.db`, `.sqlite`, `.sqlite3` no projeto consumidor ou lê `DATABASE_URL` do `.env`.
  - Mescla as informações do schema em tempo de execução com as definições de código estáticas.

### 3. CLI Parsers
- `amb_cli/cli_modules/cli_parsers.py`:
  - Adicione a flag `--live` (alias `-l`) e `--url <URI>` no parser do comando `amb schema`.

### 4. Testes Unitários
- `tests/test_db_schema_reader.py`:
  - Crie um banco SQLite temporário em memória nos testes e valide que `LiveDatabaseInspector` extrai as tabelas e colunas corretamente.
  - Verifique que tentativas de injeção ou consultas que não sejam `SELECT` de metadados são rejeitadas.
  - Garanta que a suíte `pytest` permaneça 100% verde.

---

## 📋 Critérios de Aceite (DoD)
1. `amb schema --live` extrai e formata o schema real de bancos locais sem erros.
2. Segurança Read-Only garantida (zero risco de alteração ou perda de dados no banco do usuário).
3. Código modular e atomizado (nenhum arquivo acima de 300 linhas).
4. Suíte `pytest` 100% verde.
