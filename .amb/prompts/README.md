# 📚 Catálogo de Prompts Atômicos: AMB_V2 Core Evolution & Google AI

Este diretório contém os prompts sequenciais atômicos para orientar o **Google Jules** na implementação em lote via `amb agent -p .amb/prompts/`.

Cada arquivo `.md` representa **estritamente 1 User Story (US) Atômica = 1 Sessão de VM no Jules = 1 Pull Request Incremental**, garantindo:
- **Economia extrema de tokens e contexto limpo.**
- **Conformidade arquitetural estrita (SRP, atomização <= 300 linhas, tipagem estrita).**
- **Testes unitários dedicados sem inflar arquivos existentes.**
- **Ciclo contínuo de Auto-Merge seguro via QA local.**

---

## 📑 Matriz Sequencial de Prompts Atômicos do Core (8 USs)

| # | Arquivo Prompt | Módulo Alvo | User Story / Responsabilidade |
|---|---|---|---|
| **01** | [`01_us01_session_state_and_monitor.md`](./01_us01_session_state_and_monitor.md) | `session_state.py`, `session_monitor.py`, `jules_watcher.py` | US-01: Unificação de polling e estados com enum `SessionState` e classe `SessionMonitor`. |
| **02** | [`02_us02_loop_state_machine.md`](./02_us02_loop_state_machine.md) | `loop_state_machine.py`, `loop_handler.py`, `cli_parsers.py` | US-02: Máquina de estados persistente em `.amb/loop_state.json` com `amb loop status/pause/resume`. |
| **03** | [`03_us03_precommit_validate_staged_and_hooks.md`](./03_us03_precommit_validate_staged_and_hooks.md) | `rules_manager.py`, `validate_handler.py`, `hooks_handler.py` | US-03: Validador pré-commit com `amb validate --staged` e instalador de hook `amb hooks install`. |
| **04** | [`04_us04_config_manager_singleton.md`](./04_us04_config_manager_singleton.md) | `config_manager.py`, `env.py`, `config_handler.py` | US-04: Gerenciador singleton com cache em memória e comando `amb config reload`. |
| **05** | [`05_us05_local_telemetry_and_stats.md`](./05_us05_local_telemetry_and_stats.md) | `local_telemetry.py`, `stats_handler.py` | US-05: Telemetria append-only em `.amb/telemetry.jsonl` e comando analítico `amb stats`. |
| **06** | [`06_us06_persona_engine.md`](./06_us06_persona_engine.md) | `persona_engine.py`, `persona_handler.py` | US-06: Engine unificada de personas com interpolação e validação via `amb persona validate`. |
| **07** | [`07_us07_console_presenter_and_qa_sandbox.md`](./07_us07_console_presenter_and_qa_sandbox.md) | `console_presenter.py`, `qa_sandbox.py`, `quality_gatekeeper.py` | US-07: Camada central de apresentação (`--json`, `--quiet`) e sandbox de logs de QA com extrator sanitizado. |
| **08** | [`08_us08_docs_and_skills_sync.md`](./08_us08_docs_and_skills_sync.md) | `README.md`, `_docs/`, `.agents/skills/` | US-08: Sincronização e atualização de todas as documentações e das 8 skills especializadas. |

> **Nota:** Os 22 prompts adicionais de expansão do ecossistema Google AI (`google-genai`, Model Armor, Stitch MCP, Live DB) estão catalogados na pasta [`Evolucao/`](./Evolucao/).

---

## 🚀 Como Executar com o AMB Agent em Lote

### 1. Execução Sequencial em Lote
Para executar as 8 USs do Core em sequência na branch ativa com o Google Jules:
```bash
amb agent -p .amb/prompts/
```

### 2. O que o AMB faz automaticamente em cada prompt (US):
1. **Cloud VM Dedicada:** Cria uma VM isolada no Google Jules exclusivamente para a US do prompt.
2. **Contexto Cirúrgico:** Injeta automaticamente o mapa de arquivos via `ai_context_builder` para a US.
3. **Auto-Advisor Gemini:** Monitora logs e comandos bash do Jules e responde dúvidas técnicas instantaneamente.
4. **Validação & Auto-Merge:** Ao abrir o PR, executa `gh pr ready`, roda a suíte local de testes (`pytest`), aprova e faz auto-merge no GitHub.
5. **Git Pull & Avanço:** Faz `git pull` local e passa de forma limpa para a próxima US até concluir o lote com 100% de sucesso!
