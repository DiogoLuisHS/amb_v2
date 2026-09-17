# 📚 Catálogo de Prompts Atômicos do Pacote `amb_cli/agents/`

Este diretório contém os prompts modulares específicos para orientar o **Google Jules** no alinhamento, refatoração e auditoria contínua de cada um dos módulos do pacote `amb_cli/agents/`.

Cada prompt é 100% focado em um único arquivo, garantindo economia de tokens, precisão cirúrgica de contexto e ausência de alucinações cognitivas.

---

## 📑 Prompts por Arquivo

| # | Arquivo Prompt | Módulo Alvo | Linhas Alvo | Responsabilidade Principal |
|---|---|---|:---:|---|
| **01** | [`01_agent_auto_reply.md`](./01_agent_auto_reply.md) | `amb_cli/agents/auto_reply.py` | ~140 | Fachada pública e despachante CLI do Auto-Reply |
| **02** | [`02_agent_autonomous_loop.md`](./02_agent_autonomous_loop.md) | `amb_cli/agents/autonomous_loop.py` | ~270 | Orquestrador de alto nível do loop autônomo de ciclos |
| **03** | [`03_agent_local_runner.md`](./03_agent_local_runner.md) | `amb_cli/agents/local_agent_runner.py` | ~270 | Descoberta e execução de personas (Local AGY ou Jules) |
| **04** | [`04_agent_monitor.md`](./04_agent_monitor.md) | `amb_cli/agents/monitor.py` | ~100 | Monitor e sentinela em tempo real com auto-piloto |
| **05** | [`05_agent_cognitive_advisor.md`](./05_agent_cognitive_advisor.md) | `amb_cli/agents/auto_reply_core/cognitive_advisor.py` | ~170 | Síntese de prompts cognitivos, regras e LLM |
| **06** | [`06_agent_feedback_dispatcher.md`](./06_agent_feedback_dispatcher.md) | `amb_cli/agents/auto_reply_core/feedback_dispatcher.py` | ~300 | Despacho de mensagens e aprovações REST para o Jules |
| **07** | [`07_agent_turn_extractor.md`](./07_agent_turn_extractor.md) | `amb_cli/agents/auto_reply_core/turn_extractor.py` | ~190 | Parsing polimórfico e determinação de turnos |
| **08** | [`08_agent_cycle_dispatcher.md`](./08_agent_cycle_dispatcher.md) | `amb_cli/agents/loop_core/cycle_dispatcher.py` | ~115 | Context builder, despacho no Jules e auto-merge Git |
| **09** | [`09_agent_session_assistant.md`](./09_agent_session_assistant.md) | `amb_cli/agents/loop_core/session_assistant.py` | ~120 | Monitoramento da sessão e desbloqueio autônomo |

---

## 🚀 Como Executar com o Google Jules

### 1. Criar Sessão no Jules com um Prompt Específico
```bash
# Exemplo para o turn_extractor:
amb jules create -p .amb/prompts/07_agent_turn_extractor.md -t "Refactor turn_extractor.py"
```

### 2. Executar em Loop Autônomo com o Prompt
```bash
# Executar o loop mirando um prompt específico:
amb agent -p .amb/prompts/02_agent_autonomous_loop.md --loop --max-cycles 1
```

### 3. Acompanhar em Tempo Real com o Watcher
```bash
amb monitor --auto-approve
```
