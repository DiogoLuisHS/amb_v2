# US-70: Sinergia Design-to-Deploy em Lote (amb agent -p com suporte a Pipeline)

## 📌 Contexto e Objetivo
Atualmente, existe um abismo entre os dois orquestradores:
- `amb agent -p <pasta>` processa dezenas de tarefas sequenciais em lote, mas despacha tudo diretamente para o Google Jules na nuvem, sem passar pela etapa de geração de interface visual no Google Stitch.
- `amb pipeline` executa o fluxo visual completo Design-to-Deploy (Stitch ➔ Síntese ➔ Jules ➔ QA), mas só aceita **um único arquivo por vez**, sem suporte a processamento sequencial de lotes.

Esta US integra a esteira visual ao processador de lotes:
```bash
amb agent -p .amb/prompts/ --pipeline
```
Ao processar a fila, se o prompt contiver divisões de tela (tags `## Stitch`, `UI:` ou a flag `--pipeline` estiver ativa), o orquestrador executa o pipeline visual completo para cada item da pasta sequencialmente:
1. Geração/refinamento da tela no Google Stitch SDK;
2. Síntese cognitiva da interface e tokens com Gemini;
3. Despacho da sessão com o prompt consolidado para o Google Jules;
4. Monitoramento com auto-reply e auto-merge no Git.

---

## 📐 Requisitos Técnicos

### 1. Atualização do Autonomous Loop
- **Arquivo (`amb_cli/agents/autonomous_loop.py`):**
  - Adicionar parâmetro `use_pipeline: bool = False` em `run_autonomous_loop`.
  - No loop de execução dos itens:
    - Se `use_pipeline` ou se o arquivo de prompt contiver divisões detectadas por `parse_single_prompt(content)`:
      - Invocar `PipelineOrchestrator.run(prompt_file=str(p_path), auto_approve=True, starting_branch=branch)`.
    - Caso contrário:
      - Prosseguir com o fluxo de engenharia pura direta no Jules via `dispatch_jules_session`.
  - Manter o limite rígido de 300 linhas por arquivo (Regra 02).

### 2. Integração no Parser CLI
- **Arquivo (`amb_cli/cli_modules/cli_parsers.py`):**
  - No subparser `agent`:
    - Adicionar a flag `--pipeline`:
      ```python
      p.add_argument("--pipeline", action="store_true", help="Aciona o pipeline visual Design-to-Deploy (Stitch -> Jules -> QA) para os prompts do lote.")
      ```

---

## 🧪 Critérios de Aceite
1. **Suíte de Testes Unitários:**
   - Criar `tests/test_batch_pipeline_design_to_deploy.py` cobrindo:
     - Execução do lote `amb agent -p <pasta> --pipeline` acionando o pipeline de design para os itens.
     - Auto-detecção de prompts contendo seções `## Stitch` roteando para o pipeline mesmo sem a flag.
     - Processamento sequencial de múltiplos prompts visuais em lote.
2. **Qualidade de Código:**
   - 100% dos testes passando (`pytest -q`).
   - Teto rígido de 300 linhas por arquivo (Regra 02).
   - Tipagem estrita com `typing` (Regra 04).
