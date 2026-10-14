# US-32: Auto-Numeração e Enfileiramento Direto de Prompts (amb prompt --queue)

## 📌 Contexto e Objetivo
O ecossistema AMB_V2 organiza prompts de desenvolvimento autônomo em arquivos sequenciais na pasta `.amb/prompts/` (ex: `16_us16_...md`, `30_us30_...md`).
Atualmente, quando o desenvolvedor sintetiza um prompt arquitetural via `amb prompt`, ele precisa salvar manualmente ou especificar o caminho completo com `-o`, tendo que inspecionar a pasta e adivinhar o próximo número livre da sequência.

Esta US implementa a funcionalidade de enfileiramento automático (`--queue` / `-q`), que calcula automaticamente o próximo número sequencial disponível (considerando tanto `.amb/prompts/` quanto `.amb/prompts/_completed/`), gera um nome de arquivo padronizado baseado no escopo e salva o prompt pronto para consumo imediato pelo `amb agent`.

---

## 📐 Requisitos Técnicos

### 1. Utilitário de Descoberta de Próximo Prompt Sequencial
- **Arquivo (`amb_cli/workspace/project_context.py` ou módulo de contexto):**
  - Adicionar a função:
    ```python
    def get_next_prompt_filepath(prompts_dir: Path, slug_title: str) -> Path:
        """
        Calcula o próximo número sequencial de US analisando .amb/prompts e _completed.
        Retorna o Path correspondente: ex: .amb/prompts/31_us31_<slug>.md
        """
    ```
  - Varrer `.amb/prompts/` e `.amb/prompts/_completed/` procurando padrões de regex `^(\d+)_[uU][sS](\d+)_`.
  - Encontrar o maior número encontrado (fallback: 1 se nenhum existir) e calcular `next_idx = max_num + 1`.
  - Sanitizar o título para caracteres alfanuméricos e hífens.
  - Retornar o `Path` final: `.amb/prompts/{next_idx:02d}_us{next_idx}_{clean_slug}.md`.

### 2. Suporte no Gerador de Síntese
- **Arquivo (`amb_cli/integrations/antigravity/tools/synthesize_prompt.py`):**
  - Atualizar `run_synthesize_prompt` para aceitar `queue: bool = False`:
    - Se `queue` for True e `output_file` não tiver sido definido manualmente:
      - Extrair título/slug do prompt gerado.
      - Resolver o caminho de destino via `get_next_prompt_filepath`.
      - Salvar o arquivo no disco e emitir log claro com o próximo comando sugerido (`amb agent -p .amb/prompts/`).

### 3. Integração na CLI
- **Arquivo (`amb_cli/cli_modules/cli_parsers.py`):**
  - No subparser `prompt`:
    - Adicionar argumento:
      ```python
      p.add_argument("--queue", "-q", action="store_true", help="Salva o prompt automaticamente como a próxima User Story sequencial na fila (.amb/prompts/).")
      ```
  - Repassar `queue=getattr(args, "queue", False)` na invocação do handler.

---

## 🧪 Critérios de Aceite
1. **Suíte de Testes Unitários:**
   - Criar `tests/test_prompt_queue_saving.py` cobrindo:
     - Cálculo determinístico do próximo número de US quando há arquivos existentes.
     - Cálculo correto quando pastas de completed contêm numeração mais alta.
     - Geração do nome de arquivo sanitizado (`XX_usXX_<slug>.md`).
     - Salvamento automático quando a flag `--queue` é informada.
2. **Qualidade de Código e Limites Arquiteturais:**
   - 100% dos testes unitários passando (`pytest -q`).
   - Teto rígido de 300 linhas por arquivo (Regra 02).
   - Tipagem estrita com `typing` (Regra 04).
