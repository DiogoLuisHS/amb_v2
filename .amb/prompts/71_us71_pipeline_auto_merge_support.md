# US-71: Auto-Merge e Fechamento de Ciclo em amb pipeline (--auto-merge)

## 📌 Contexto e Objetivo
Atualmente, quando o desenvolvedor executa o pipeline Design-to-Deploy ([`pipeline.py`](file:///c:/Users/DiogoHungaro/Desktop/Script/amb_v2/amb_cli/pipeline/pipeline.py)), o fluxo percorre as etapas:
1. Geração de tela no Stitch;
2. Síntese e envio ao Jules;
3. Monitoramento em tempo real da sessão;
4. Validação de QA local pelo `QualityGatekeeper`.
Porém, ao concluir a validação de QA com 100% de sucesso, o pipeline encerra **deixando o Pull Request aberto no GitHub sem fazer o merge**, exigindo que o desenvolvedor execute manualmente comandos extras para integrar a branch.

Esta US fecha o ciclo ponta a ponta:
```bash
amb pipeline specs/nova_tela.md --auto-merge
# ou em modo totalmente autônomo (com -y):
amb pipeline specs/nova_tela.md -y
```
Ao validar a integridade local pelo Gatekeeper de QA, o pipeline realiza o auto-merge seguro do PR no GitHub (com squash e exclusão de branch remota) e sincroniza a branch base localmente.

---

## 📐 Requisitos Técnicos

### 1. Atualização do PipelineOrchestrator
- **Arquivo (`amb_cli/pipeline/pipeline.py`):**
  - Adicionar o parâmetro `auto_merge: bool = False` ao método `PipelineOrchestrator.run`.
  - Se `auto_approve` estiver ativo (`-y`), ativar `auto_merge = True` por padrão (a menos que explicitamente desativado com `--no-auto-merge`).
  - No encerramento de `_monitor_jules_session`:
    - Após `QualityGatekeeper.run_qa(repo_root)` ter retornado sucesso:
      - Se `auto_merge`:
        - log("PIPELINE", "🔀 Integrando Pull Request automaticamente no Git...", Colors.HEADER)
        - Importar e executar `run_merge_session_pr(session_id=session_id, target_branch=starting_branch)`.
  - Manter o limite rígido de 300 linhas por arquivo (Regra 02).

### 2. Atualização do Parser CLI
- **Arquivo (`amb_cli/cli_modules/cli_parsers.py`):**
  - No subparser `pipeline`:
    - Adicionar a flag `--auto-merge`:
      ```python
      p.add_argument("--auto-merge", action="store_true", help="Realiza o merge automático do Pull Request no Git após aprovação nos testes locais de QA.")
      p.add_argument("--no-auto-merge", action="store_true", help="Desabilita o merge automático do Pull Request ao concluir.")
      ```

---

## 🧪 Critérios de Aceite
1. **Suíte de Testes Unitários:**
   - Criar `tests/test_pipeline_auto_merge.py` cobrindo:
     - Execução de `amb pipeline --auto-merge` acionando a rotina de merge após sucesso no QA.
     - Execução com `-y` / `--auto-approve` ativando o auto-merge por padrão.
     - Preservação do comportamento sem merge quando `--no-auto-merge` for fornecido.
     - Bloqueio do merge caso a validação do `QualityGatekeeper` falhe.
2. **Qualidade de Código:**
   - 100% dos testes passando (`pytest -q`).
   - Teto rígido de 300 linhas por arquivo (Regra 02).
   - Tipagem estrita com `typing` (Regra 04).
