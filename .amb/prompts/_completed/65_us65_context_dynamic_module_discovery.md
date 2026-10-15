# US-65: Descoberta Dinâmica de Módulos em amb context

## 📌 Contexto e Objetivo
Atualmente, no comando `amb context`, o argumento `module` possui como valor padrão chumbado/hardcoded a string `"agenda"`.
Se o desenvolvedor estiver trabalhando em qualquer repositório que não possua um módulo chamado "agenda" e executar `amb context` sem argumentos, o gerador de contexto busca por "agenda", falha ou gera um roteiro vazio.

Esta US adota uma abordagem moderna e adaptativa ao projeto ativo:
1. **Remoção do Valor Fixo:** Elimina o default hardcoded `"agenda"`.
2. **Auto-Descoberta de Módulos:** Se nenhum módulo for fornecido (`amb context` sem parâmetros):
   - O construtor varre a árvore do projeto (pastas sob `apps/`, `src/modules/`, `src/features/`, `src/domain/` ou schemas existentes) e identifica os domínios reais do repositório.
   - Se encontrar módulos, lista-os no terminal com seus totais de arquivos e sugere o comando direto:
     ```
     === 🧩 MÓDULOS ENCONTRADOS NO PROJETO ===
       • kanban      (18 arquivos) -> amb context kanban
       • users       (12 arquivos) -> amb context users
       • billing     (9 arquivos)  -> amb context billing
     ```
3. Se o projeto não estiver estruturado por módulos, gera o roteiro abrangente de todas as camadas do projeto.

---

## 📐 Requisitos Técnicos

### 1. Atualização do Parser CLI
- **Arquivo (`amb_cli/cli_modules/cli_parsers.py`):**
  - No subparser `context`:
    - Atualizar `module`:
      ```python
      p.add_argument("module", nargs="?", default=None, help="Nome do módulo ou pasta para rastrear (se omitido, auto-descobre os módulos do projeto).")
      ```

### 2. Descoberta de Módulos no AIContextBuilder
- **Arquivo (`amb_cli/architecture/ai_context_builder.py`):**
  - Adicionar o método `discover_modules(self) -> List[Dict[str, Any]]`:
    - Varre a estrutura do repositório identificando subdiretórios de domínio em pastas convencionais (`modules`, `features`, `routes`, `domains`, etc.).
    - Conta os arquivos de código pertencentes a cada módulo.
    - Retorna lista ordenada de módulos encontrados.
  - Em `generate_context(target: Optional[str] = None, ...)`:
    - Se `not target`:
      - Invocar `discover_modules()`.
      - Se módulos existirem: listar de forma amigável no terminal ou retornar em JSON.
      - Se nenhum módulo isolado for detectado: gerar o contexto global de todas as camadas do projeto (`query="PROJETO"`).
  - Manter o limite rígido de 300 linhas por arquivo (Regra 02).

---

## 🧪 Critérios de Aceite
1. **Suíte de Testes Unitários:**
   - Criar `tests/test_context_dynamic_discovery.py` cobrindo:
     - Chamada a `amb context` sem argumentos em repositório modular listando as opções disponíveis.
     - Chamada a `amb context` passando módulo específico mantendo a geração detalhada do roteiro.
     - Suporte a `--json` retornando a lista de módulos descobertos.
2. **Qualidade de Código:**
   - 100% dos testes passando (`pytest -q`).
   - Teto rígido de 300 linhas por arquivo (Regra 02).
   - Tipagem estrita com `typing` (Regra 04).
