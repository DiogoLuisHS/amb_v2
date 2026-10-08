# US-73: Modo Simulação e Pré-Visualização da Orquestração (--dry-run)

## 📌 Contexto e Objetivo
Tanto o desenvolvimento em lote de prompts (`amb agent -p <pasta>`) quanto o pipeline Design-to-Deploy (`amb pipeline <arquivo>`) são fluxos pesados que consomem cotas de IA (Stitch, Jules, Gemini), criam branches remotas e abrem Pull Requests reais no GitHub.
Atualmente, não existe um mecanismo de pré-visualização para inspecionar com segurança:
- A lista e ordem de prompts que serão executados;
- O escopo de cada tarefa e os títulos inferidos;
- As etapas que serão acionadas (se haverá geração de tela no Stitch ou envio direto ao Jules);
- A branch base alvo.

Esta US introduz a flag unificada de simulação:
```bash
amb agent -p .amb/prompts/ --dry-run
# ou no pipeline:
amb pipeline specs/nova_tela.md --dry-run
```
Ela valida a sintaxe dos arquivos, exibe o roteiro estruturado das etapas no terminal e calcula métricas estimadas sem realizar nenhuma chamada externa nem criar sessões.

---

## 📐 Requisitos Técnicos

### 1. Atualização do Autonomous Loop
- **Arquivo (`amb_cli/agents/autonomous_loop.py`):**
  - Adicionar parâmetro `dry_run: bool = False` em `run_autonomous_loop`.
  - Se `dry_run`:
    - Resolver a fila de itens (`syncer.resolve_items_queue`).
    - Exibir cabeçalho visual de simulação:
      ```
      === 🔍 SIMULAÇÃO DE ORQUESTRAÇÃO EM LOTE [DRY-RUN] ===
        • Total de Itens: {len(items)}
        • Branch Base: {branch}
        • Fila Ordenada de Execução:
          1. [Prompt] 01_auth.md -> "Auth Refactor" (Stitch: Sim | Jules: Sim)
          2. [Prompt] 02_api.md  -> "API Endpoints" (Stitch: Não | Jules: Sim)
      ```
    - Retornar imediatamente sem criar sessões nem invocar o Jules.
  - Manter o limite rígido de 300 linhas por arquivo (Regra 02).

### 2. Atualização do PipelineOrchestrator
- **Arquivo (`amb_cli/pipeline/pipeline.py`):**
  - Adicionar parâmetro `dry_run: bool = False` em `PipelineOrchestrator.run`.
  - Se `dry_run`:
    - Executar o parsing dos prompts e exibição dos metadados extraídos (Stitch, Jules, branch).
    - Exibir resumo e retornar sem disparar chamadas de API.
  - Manter o limite rígido de 300 linhas por arquivo (Regra 02).

### 3. Integração no Parser CLI
- **Arquivo (`amb_cli/cli_modules/cli_parsers.py`):**
  - Adicionar a flag `--dry-run` tanto no subparser `agent` quanto no subparser `pipeline`.

---

## 🧪 Critérios de Aceite
1. **Suíte de Testes Unitários:**
   - Criar `tests/test_orchestrator_dry_run.py` cobrindo:
     - Execução de `amb agent -p <pasta> --dry-run` exibindo a fila sem criar sessões no Jules.
     - Execução de `amb pipeline <arquivo> --dry-run` exibindo o plano das etapas sem invocar o Stitch ou Jules.
     - Garantia de que nenhuma requisição externa de rede é realizada quando `--dry-run` está ativo.
2. **Qualidade de Código:**
   - 100% dos testes passando (`pytest -q`).
   - Teto rígido de 300 linhas por arquivo (Regra 02).
   - Tipagem estrita com `typing` (Regra 04).
