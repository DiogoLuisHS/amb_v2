# 🎯 Tarefa Jules: Auditoria e Alinhamento de `amb_cli/architecture/db_schema_reader.py`

## 📌 Arquivo Alvo
- **Caminho:** `amb_cli/architecture/db_schema_reader.py`
- **Estado Atual:** 150 linhas (Em conformidade com teto de linhas, mas necessita de auditoria de regras).
- **Responsabilidade Única (SRP - Regra 01):** Inspecionar e catalogar tabelas, colunas e constraints de schemas de banco de dados (Drizzle ORM) de forma estritamente read-only.

---

## 📐 Regras Arquiteturais Obrigatórias (`.agents/rules/`)
1. **Regra 01 (SRP):** Manter a classe `DbSchemaReader` focada exclusivamente no parsing e descoberta de schemas. A função `show_schema` deve atuar apenas como formatadora para o terminal.
2. **Regra 02 (Atomização para IA):** O arquivo deve permanecer estritamente abaixo de 300 linhas.
3. **Regra 03 (DRY & Imports Canônicos):** Utilizar sempre imports canônicos (`from config.bootstrap import ensure_amb_env`, `from config import Colors, find_repo_root, log_error`). Corrigir qualquer chamada externa com import plano (como em `amb_cli/cli_modules/cli_handlers.py` linha 542: mudar para `from architecture.db_schema_reader import show_schema`).
4. **Regra 04 (Tipagem Estrita):** 100% dos métodos públicos e funções auxiliares devem possuir type hints completos (`List[Path]`, `List[Dict[str, Any]]`, `Optional[str]`).
5. **Regra 05 (Documentação Concisa):** Proibido banners gigantes decorativos ASCII (`# =============...`). Substituir por cabeçalhos e prints declarativos e limpos.
6. **Regra 06 (Segurança Git & Testes):** Criar a suíte de testes unitários [`tests/test_db_schema_reader.py`](file:///c:/Users/DiogoHungaro/Desktop/Script/amb_v2/tests/test_db_schema_reader.py) cobrindo os métodos `find_schema_dirs`, `list_schema_files`, `parse_drizzle_schema` e `show_schema`. Todos os testes devem rodar com 100% de sucesso.

---

## 🛠️ Itens Específicos a Verificar / Refatorar
1. **Tipagem e Robustez do Regex:**
   - Garantir que `parse_drizzle_schema` trate arquivos vazios, malformados ou inexistentes de forma defensiva sem levantar exceções não tratadas.
2. **Correção de Caller Legado:**
   - Em `amb_cli/cli_modules/cli_handlers.py` (função `cmd_db_schema`), atualizar o import local para usar o caminho absoluto canônico:
     `from architecture.db_schema_reader import show_schema`
3. **Criação de Testes Unitários:**
   - Adicionar arquivo de testes `tests/test_db_schema_reader.py` usando `tmp_path` do pytest para criar arquivos de schema Drizzle mock e testar o parsing.

---

## 🧪 Validação Obrigatória
Antes de abrir o Pull Request:
```bash
python -m py_compile amb_cli/architecture/db_schema_reader.py
python -m pytest tests/test_db_schema_reader.py
python -m pytest
```
Todos os testes unitários devem passar (100% green).

---

## 🚀 Ação Final Obrigatória: Abertura do Pull Request
Ao concluir todas as alterações e validar os testes com sucesso (100% green):
1. Você DEVE submeter/abrir o Pull Request no GitHub imediatamente.
2. Não encerre a sessão apenas no estado "Ready for submission"; confirme a criação do PR diretamente no GitHub com título e descrição claros das alterações.
