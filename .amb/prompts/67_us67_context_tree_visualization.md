# US-67: Resumo Compacto em Árvore de Camadas em amb context (--tree)

## 📌 Contexto e Objetivo
Para módulos complexos ou domínios de monorepos com 20 a 50 arquivos mapeados, a saída integral detalhada do `amb context <modulo>` pode gerar centenas de linhas de listagem no terminal.
Quando o desenvolvedor deseja apenas ter uma visão panorâmica rápida e visual da distribuição arquitetural (para saber se o módulo está balanceado entre DB, Serviços e Telas), essa listagem é excessiva.

Esta US introduz a visualização compacta em árvore de camadas:
```bash
amb context kanban --tree
```
Que renderiza um diagrama ANSI resumido do fluxo e contagem de arquivos por camada:
```
🧭 FLUXO ARQUITETURAL EM CAMADAS: KANBAN
├── 🏛️  Database & Schemas:   3 arquivos
├── 🗄️  Repositories:         2 arquivos
├── ⚙️  Services / Business:   4 arquivos
├── 🌐  Controllers & APIs:    3 arquivos
└── 🖥️  UI & Components:       6 arquivos
Total: 18 arquivos mapeados (DB ➔ Services ➔ UI)
```

---

## 📐 Requisitos Técnicos

### 1. Atualização do Parser CLI
- **Arquivo (`amb_cli/cli_modules/cli_parsers.py`):**
  - No subparser `context`:
    - Adicionar a flag `--tree`:
      ```python
      p.add_argument("--tree", action="store_true", help="Exibe um resumo compacto em árvore do fluxo arquitetural por camadas.")
      ```

### 2. Atualização do Construtor de Contexto
- **Arquivo (`amb_cli/architecture/ai_context_builder.py`):**
  - Implementar método `generate_tree_view(self, query: str, layers: Dict[str, Any]) -> str`:
    - Monta árvore formatada em caracteres ANSI/Unicode (`├──`, `└──`).
    - Exibe cada camada com seu ícone, título e total de arquivos.
    - Exibe o total geral consolidado.
  - Em `generate_context`:
    - Se `tree_view`:
      - Imprimir `builder.generate_tree_view(query, layers)` e retornar.
  - Manter o limite rígido de 300 linhas por arquivo (Regra 02).

---

## 🧪 Critérios de Aceite
1. **Suíte de Testes Unitários:**
   - Criar `tests/test_context_tree_view.py` cobrindo:
     - Execução de `amb context <modulo> --tree` emitindo a árvore compacta.
     - Contagem precisa de arquivos por camada.
     - Preservação do relatório markdown completo detalhado quando `--tree` não for especificado.
2. **Qualidade de Código:**
   - 100% dos testes passando (`pytest -q`).
   - Teto rígido de 300 linhas por arquivo (Regra 02).
   - Tipagem estrita com `typing` (Regra 04).
