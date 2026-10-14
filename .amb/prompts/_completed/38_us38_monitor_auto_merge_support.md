# US-38: Piloto Automático Completo com Auto-Merge no Sentinela (amb monitor --auto-merge)

## 📌 Contexto e Objetivo
O sentinela unificado ([`monitor.py`](file:///c:/Users/DiogoHungaro/Desktop/Script/amb_v2/amb_cli/agents/monitor.py)) possui a flag de piloto automático `--auto-approve` (`-y`), que responde dúvidas do Jules em tempo real usando o Gemini. Contudo, quando o Jules conclui a implementação e abre um Pull Request (`completed_needs_merge`), o sentinela apenas emite um aviso no terminal sugerindo que o desenvolvedor execute manualmente `amb jules merge -s <id>`.

Para desenvolvedores trabalhando no editor de código ou equipes com tarefas disparadas via agendamento web, essa etapa manual interrompe o fluxo de trabalho.

Esta US adiciona a flag `--auto-merge` ao comando `amb monitor`, capacitando o sentinela a executar automaticamente o Quality Gatekeeper local e realizar o merge seguro do PR via GitHub CLI (`gh pr merge`) assim que a sessão for concluída com sucesso.

---

## 📐 Requisitos Técnicos

### 1. Integração de Auto-Merge no Loop do Monitor
- **Arquivo (`amb_cli/agents/monitor.py`):**
  - Atualizar `run_monitor`:
    ```python
    def run_monitor(
        interval_seconds: int = 15,
        check_once: bool = False,
        auto_approve: bool = False,
        auto_merge: bool = False,
        verbose: bool = False
    ) -> None:
    ```
  - Quando `jules_alerts` contiver alertas do tipo `completed_needs_merge`:
    - Se `auto_merge=True`:
      - Extrair `sid = alt.get("session_id")` e `pr = alt.get("pr")`.
      - Emitir log: `🔀 [AUTO-PILOT] Executando validação de QA e auto-merge para a sessão {sid} (PR #{pr.get('number')})...`
      - Importar e invocar:
        ```python
        from integrations.jules.tools.merge_session import run_jules_merge
        run_jules_merge(session_id=sid, branch="main")
        ```
      - Tratar exceções de validação de QA ou conflitos de merge de forma segura com log de erro sem interromper o loop de monitoramento.
  - Atualizar a classe `UnifiedMonitor` para aceitar `auto_merge: bool = False`.
  - Manter o limite rígido de 300 linhas por arquivo (Regra 02).

### 2. Integração na Camada CLI
- **Arquivo (`amb_cli/cli_modules/cli_parsers.py`):**
  - No subparser `monitor`:
    ```python
    p.add_argument("--auto-merge", action="store_true", help="Executa testes locais de QA e realiza merge automático do Pull Request ao detectar conclusão de sessão.")
    ```
- **Arquivo (`amb_cli/cli_modules/cli_handlers.py`):**
  - No `cmd_monitor`: repassar `auto_merge=getattr(args, "auto_merge", False)`.

---

## 🧪 Critérios de Aceite
1. **Suíte de Testes Unitários:**
   - Criar `tests/test_monitor_auto_merge.py` cobrindo:
     - Detecção de alerta `completed_needs_merge` sem `--auto-merge` (apenas emite aviso, sem acionar merge).
     - Detecção de alerta com `auto_merge=True` invocando `run_jules_merge` com o ID da sessão.
     - Resiliência do monitor caso a validação de QA ou o comando `gh pr merge` falhe (continua o loop de vigilância sem crash).
     - Parsing da flag `--auto-merge` no parser de CLI de `amb monitor`.
2. **Qualidade de Código e Limites Arquiteturais:**
   - 100% dos testes unitários passando (`pytest -q`).
   - Teto rígido de 300 linhas por arquivo (Regra 02).
   - Tipagem estrita com `typing` (Regra 04).
