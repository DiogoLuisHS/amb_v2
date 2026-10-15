# US-64: Suporte Agnóstico a Schemas Prisma (schema.prisma) em amb schema

## 📌 Contexto e Objetivo
Atualmente, o `DbSchemaReader` só analisa definições do Drizzle ORM em arquivos `.ts` e `.js`.
Em projetos que adotam o Prisma ORM (um dos ORMs mais populares do ecossistema TypeScript e Node.js com o arquivo `schema.prisma`), o comando `amb schema` falha ao tentar localizar os modelos, informando que nenhum diretório de schema foi encontrado.

Esta US amplia o leitor de schemas para suportar arquivos `schema.prisma`:
1. **Descoberta de Arquivo Prisma:** Localiza `schema.prisma` em `prisma/`, `src/prisma/` ou na raiz do projeto.
2. **Parser Agnóstico de Modelos:** Extrai modelos (`model User { ... }`), nomes de campos, tipos e atributos (`@id`, `@unique`, `@default`, etc.).
3. **Unificação:** Apresenta tabelas e colunas do Prisma no mesmo formato padronizado do catálogo de schemas do AMB_V2.

---

## 📐 Requisitos Técnicos

### 1. Atualização do DbSchemaReader
- **Arquivo (`amb_cli/architecture/db_schema_reader.py`):**
  - Atualizar `find_schema_dirs(root: str)`:
    - Incluir candidatos: `Path(root) / "prisma"`, `Path(root) / "src" / "prisma"`.
  - Atualizar `list_schema_files(root: str)`:
    - Incluir busca por `*.prisma` (ex: `schema.prisma`).
  - Implementar o método `parse_prisma_schema(filepath: Path) -> List[Dict[str, Any]]`:
    - Regex para detectar blocos `model <Nome> { ... }`.
    - Itera sobre linhas do bloco ignorando comentários `//` e linhas vazias.
    - Extrai `name`, `type` e `options` (ex: `@id @default(autoincrement())`).
    - Retorna lista de tabelas compatível com o formato unificado:
      ```python
      {
          "variable": model_name,
          "table_name": model_name.lower(),
          "file": filepath.name,
          "path": str(filepath),
          "columns": columns
      }
      ```
  - Em `show_schema`: se o arquivo terminar com `.prisma`, invocar `parse_prisma_schema`.
  - Manter o limite rígido de 300 linhas por arquivo (Regra 02).

---

## 🧪 Critérios de Aceite
1. **Suíte de Testes Unitários:**
   - Criar `tests/test_schema_prisma_support.py` cobrindo:
     - Detecção e leitura de arquivo `schema.prisma`.
     - Parsing correto de modelos Prisma com campos, tipos e decorators (`@id`, `@unique`).
     - Exibição adequada no terminal e na saída JSON quando `--json` for fornecido.
2. **Qualidade de Código:**
   - 100% dos testes passando (`pytest -q`).
   - Teto rígido de 300 linhas por arquivo (Regra 02).
   - Tipagem estrita com `typing` (Regra 04).
