# US-37: Modo Silencioso por Padrão no Sentinela (amb monitor) e Flag Explícita --verbose

## 📌 Contexto e Objetivo
Atualmente, o sentinela unificado em tempo real ([`monitor.py`](file:///c:/Users/DiogoHungaro/Desktop/Script/amb_v2/amb_cli/agents/monitor.py)) opera por padrão em modo altamente prolixo (verbose). A cada intervalo de polling (padrão: 15s), ele imprime duas linhas no terminal:
```
[14:20:15] 🔄 Rodada #12: Checando chats e status...
ℹ️ [AMB] Tudo operando normalmente. Nenhuma pendência humana ou erro detectado.
```
Durante períodos normais de execução de tarefas na nuvem, o terminal acumula centenas de linhas redundantes, poluindo o buffer e dificultando a visualização de alertas reais de erro, perguntas do agente ou solicitações de aprovação de plano.

Esta US inverte essa abordagem para priorizar a experiência do desenvolvedor (DX):
1. **Silencioso por Padrão (Quiet by Default):** O sentinela exibe apenas o cabeçalho inicial e permanece silencioso, imprimindo no terminal e notificando **estritamente quando eventos reais acontecerem** (dúvidas para responder, planos gerados, falhas ou PRs prontos).
2. **Flag Explícita `--verbose` (`-v`):** Caso o desenvolvedor queira acompanhar o batimento contínuo de cada ciclo de polling, ele passa `-v` ou `--verbose`.

---

## 📐 Requisitos Técnicos

### 1. Atualização do Motor de Monitoramento
- **Arquivo (`amb_cli/agents/monitor.py`):**
  - Atualizar `run_monitor`:
    ```python
    def run_monitor(
        interval_seconds: int = 15,
        check_once: bool = False,
        auto_approve: bool = False,
        verbose: bool = False
    ) -> None:
    ```
  - Se `not verbose`:
    - Suprimir a impressão de `🔄 Rodada #{cycle}: Checando chats e status...` a cada tick.
    - Suprimir a notificação de rotina `Tudo operando normalmente...` quando não há alertas.
    - Manter ativas todas as impressões de eventos reais:
      - Alertas detectados pelo `JulesWatcher` (`failed`, `awaiting_feedback`, `completed_needs_merge`).
      - Ações de auto-resposta no piloto automático.
      - Erros ou exceções de conexão.
  - Atualizar a classe `UnifiedMonitor` para aceitar e repassar `verbose: bool = False`.
  - Manter o limite rígido de 300 linhas por arquivo (Regra 02).

### 2. Integração na Camada CLI
- **Arquivo (`amb_cli/cli_modules/cli_parsers.py`):**
  - No subparser `monitor`:
    ```python
    p.add_argument("--verbose", "-v", action="store_true", help="Exibe logs detalhados de polling a cada ciclo de checagem (por padrão o monitor é silencioso).")
    ```
- **Arquivo (`amb_cli/cli_modules/cli_handlers.py`):**
  - No `cmd_monitor`:
    - Instanciar `UnifiedMonitor(interval=args.interval, auto_approve=args.auto_approve, verbose=getattr(args, "verbose", False))`.

---

## 🧪 Critérios de Aceite
1. **Suíte de Testes Unitários:**
   - Criar `tests/test_monitor_quiet_mode.py` cobrindo:
     - Execução padrão de `run_monitor(check_once=True, verbose=False)` não emitindo mensagens de rotina quando não há alertas.
     - Execução com `verbose=True` emitindo logs de ciclo (`Rodada #...`) e status normal.
     - Garantia de que alertas de eventos reais continuam sendo exibidos normalmente em ambos os modos.
     - Parsing correto da flag `-v` / `--verbose` no subparser `amb monitor`.
2. **Qualidade de Código e Limites Arquiteturais:**
   - 100% dos testes unitários passando (`pytest -q`).
   - Teto rígido de 300 linhas por arquivo (Regra 02).
   - Tipagem estrita com `typing` (Regra 04).
