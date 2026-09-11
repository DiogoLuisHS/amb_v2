# ✅ AMB_V2 — Changelog de Bugs Corrigidos & Features Implementadas

> Atualizado em: 2026-09-11

Este documento registra todos os bugs corrigidos e features implementadas no ecossistema `amb_v2`.

---

## 🐛 Bugs Corrigidos

### Bug #1 — JulesWatcher quebra silenciosamente ao listar atividades
**Arquivo:** `dashboard/watchers/jules_watcher.py`
**Causa:** `act_res.get("activities", [])` assumia que a API retorna um dict, mas o Jules pode retornar lista direta. Resultava em `AttributeError` silenciado, e o watcher nunca detectava dúvidas pendentes.
**Fix:** `acts = act_res if isinstance(act_res, list) else act_res.get("activities", [])`
**Commit:** `a26f66e`

### Bug #2 — Loop responde mesma dúvida 2x em sequência rápida
**Arquivo:** `agents/autonomous_loop.py`
**Causa:** Flag `feedback_answered_for_turn` resetado com base no ID de qualquer activity (incluindo resposta do próprio usuário), não da mensagem do agente Jules.
**Fix:** Rastrear `last_answered_agent_msg_id` — apenas mensagens do agente Jules.
**Commit:** `8ea55ee`

### Bug #3 — Output de bash truncado em 150 chars impede diagnóstico correto
**Arquivo:** `agents/auto_reply.py`
**Causa:** `out[:150]...` cortava o output antes dos erros de typecheck/build aparecerem no prompt enviado ao Gemini.
**Fix:** 150 → 800 chars com indicador de truncamento: `...[+N chars omitidos]`
**Commit:** `a26f66e`

### Bug #4 — QA pós-merge hardcoded em `npm run typecheck` + `npm run build`
**Arquivo:** `integrations/jules/tools/merge_session_pr.py`
**Causa:** Comandos de QA fixos. Projetos Python, Go ou sem `package.json` falhavam no QA pós-merge mesmo com código correto.
**Fix:** Lê `qa{}` do `.amb/amb_project.json` com auto-detecção de stack:
- Node.js: detecta `package.json` → `npm run typecheck` + `npm run build`
- Python: detecta `pyproject.toml`/`requirements.txt` → `python -m py_compile`
- Go: detecta `go.mod` → `go build ./...`

Configuração manual via `.amb/amb_project.json`:
```json
{
  "qa": {
    "typecheck": "npm run typecheck",
    "build": "npm run build"
  }
}
```
**Commit:** `a26f66e`

### Bug #6 — `_filter_rules_for_jules` não detecta `###` como fim de seção
**Arquivo:** `agents/auto_reply.py`
**Causa:** O filtro só detectava `## ` (h2 exato) como delimitador. Seções com subseções `###` ou sem próximo h2 vazavam conteúdo de Git para o prompt do Jules.
**Fix:** `if skip and line.lstrip().startswith("#")` — detecta qualquer nível de header markdown.
**Commit:** `a26f66e`

### Bug #7 — Monitor ignora sessões COMPLETED sem PR mergeado
**Arquivo:** `dashboard/watchers/jules_watcher.py`
**Causa:** `JulesWatcher.check()` só emitia alertas para `AWAITING_USER_FEEDBACK` e `FAILED`. Sessões `COMPLETED` sem merge passavam despercebidas.
**Fix:** Novo alerta `completed_needs_merge` com sugestão automática de `amb jules merge -s <id>`.
**Commit:** `a26f66e`

### Bug #8 — Segunda dúvida do Jules não é respondida, travando o loop
**Arquivo:** `agents/autonomous_loop.py`
**Causa:** Após responder a 1ª dúvida, Jules fazia uma 2ª pergunta mas o loop não reconhecia o novo estado de AWAITING como uma nova dúvida a responder.
**Fix:** Detecção dupla:
1. Nova mensagem do agente com ID diferente do último respondido
2. Estado voltou para AWAITING após ter saído (Jules fez 2ª pergunta)
**Commit:** `8ea55ee`

### Bug #9 — PR criado pelo Jules fica como Draft e não é publicado para merge
**Arquivo:** `integrations/jules/tools/merge_session_pr.py`
**Causa:** Jules sempre cria PRs como Draft (botão "Publish PR" manual). O loop tentava fazer merge sem antes publicar.
**Fix aplicado:**
1. `gh pr ready <pr>` executado automaticamente antes do merge
2. `get_latest_open_pr` tenta primeiro com `--draft` para garantir que drafts sejam detectados
3. Aguarda 12s após `COMPLETED` para Jules popular o campo `outputs` com a URL do PR
**Commit:** `8ea55ee`

### Bug #10 — Resposta duplicada para chats que já haviam sido respondidos
**Arquivos:** `agents/auto_reply.py`, `agents/autonomous_loop.py`, `dashboard/watchers/jules_watcher.py`
**Causa:** Quando uma resposta era enviada, a API do Jules demorava alguns segundos para mudar o estado de `AWAITING_USER_FEEDBACK` para `IN_PROGRESS`. O `advisor` e o `watcher` listavam a sessão como pendente novamente e respondiam à pergunta anterior do agente, ignorando que a atividade mais recente na conversa já era um `userMessage` enviado pelo usuário.
**Fix aplicado:**
1. Implementada a função `get_last_conversation_turn(acts)` que analisa estritamente a última atividade de conversa.
2. Se a última atividade for `userMessage`, `is_awaiting_user_action` é definido como `False`.
3. `get_pending_sessions()` ignora sessões onde a última mensagem já foi do usuário.
4. `advise_and_reply()` impede reenvios no modo `auto_approve` e exibe aviso de proteção no modo interativo.
5. `monitor_and_assist_session()` e `jules_watcher.py` não disparam respostas nem alertas falsos se a bola estiver com o agente Jules.

### Bug #11 — QualityGatekeeper no Pipeline hardcoded para `npm`
**Arquivo:** `pipeline/pipeline.py`
**Causa:** `QualityGatekeeper.run_qa` executava `npm run typecheck` fixo mesmo em projetos Python ou Go, quebrando o término do pipeline no Gatekeeper 2.
**Fix:** Adicionada auto-detecção de stack (Node/Python/Go) e suporte a `.amb/amb_project.json`.

### Bug #12 — Branch `develop` inexistente causando `FAILED` no clone do Jules
**Arquivos:** `pipeline/pipeline.py`, `agents/autonomous_loop.py`, `integrations/jules/jules_client.py`, `cli.py`
**Causa:** Branch padrão estava hardcoded em `"develop"`. Repositórios com branch principal `main` falhavam no clone do Jules com `Remote branch develop not found in upstream origin`.
**Fix:** Auto-detecção dinâmica da branch ativa do repositório local (`git branch --show-current`) e exposição de `--branch` no `amb agent`.

### Bug #13 — Payload aninhado do Jules (`agentMessaged.agentMessage`) e sobrescrita por `progressUpdated`
**Arquivo:** `agents/auto_reply.py`
**Causa:** A API do Jules retorna mensagens aninhadas (`agentMessaged: { agentMessage: "..." }`) que não possuíam o campo `.get("text")`. O parser falhava em capturar a mensagem e acabava caindo no log do `progressUpdated` anterior.
**Fix:** Implementado `extract_activity_text()` polimórfico cobrindo todas as variações de payload do Jules e isolamento dos eventos de progresso para que nunca sobrescrevam mensagens ativas.


---


## 🚀 Features Implementadas

### C5 — `amb context` Integrado ao Prompt de Despacho do Jules
**Arquivo:** `agents/autonomous_loop.py`
**Problema:** O Jules precisava explorar o repositório do zero em cada sessão (20-30min iniciais de leitura de arquivos).
**Implementação:** Antes do despacho de cada sessão, `AIContextBuilder` gera automaticamente o roteiro arquitetural do módulo/persona ativo e o anexa ao prompt. O Jules já recebe o mapa completo de arquivos ordenado por camadas (DB → Repositórios → Services → Controllers → UI).
**Impacto:** Redução estimada de 20-30min no tempo de exploração inicial por sessão.
**Commit:** `a26f66e`

### Loop Autônomo com Suporte a `--all` e `--max-cycles`
**Arquivo:** `agents/autonomous_loop.py`, `cli.py`
**Implementação:** Loop itera por todas as personas encontradas em `.amb/personas/` a cada ciclo.
```bash
amb agent --all --loop --max-cycles 3
amb agent --role relay --loop --max-cycles 5
```

### Detecção de PR via `outputs` da Sessão Jules
**Arquivo:** `integrations/jules/tools/merge_session_pr.py`
**Implementação:** `detect_pr_from_session` inspeciona o campo `outputs` da sessão Jules (estruturado) antes de fazer log parsing, aumentando significativamente a confiabilidade.

### Publicação de Draft PRs Automática
**Arquivo:** `integrations/jules/tools/merge_session_pr.py`
**Implementação:** `gh pr ready <pr>` executado automaticamente no pipeline de merge antes do `gh pr review` e `gh pr merge`.

---

## 🧹 Refatorações & Code Health (2026-09-11)

### Limpeza de Imports e Facade do Auto Advisor (PR #11)
**Arquivo:** `dashboard/auto_advisor.py`
- **Motivação:** Remoção de imports mortos (`run_auto_advisor`, `auto_reply_all_pending`, `interactive_advisor_menu`) que eram redundantes na facade do script.
- **Implementação:** Mantido apenas `from auto_reply import main`, garantindo conformidade com linting e execução limpa.

### Refatoração de Classificação Arquitetural em AIContextBuilder (PR #13)
**Arquivo:** `architecture/ai_context_builder.py`
- **Motivação:** Monolito condicional em `classify_and_order_files` e risco de poluição de estado entre chamadas sucessivas.
- **Implementação:**
  - Extração da configuração de camadas para constante de classe `LAYERS_CONFIG`.
  - Uso de `copy.deepcopy` para inicialização isolada por execução.
  - Criação do helper privado `_determine_file_layer(self, file: str)` delegando a responsabilidade de roteamento de camadas.

### Decomposição Modular do Auto Advisor e Eliminação de Recursão (PR #14)
**Arquivo:** `agents/auto_reply.py`
- **Motivação:** `run_auto_advisor` acumulava controle de fluxo de aprovação em lote e menu interativo no terminal.
- **Implementação:**
  - Extraídos `_process_auto_approve_batch(pending)` e `_process_interactive_menu(pending)`.
  - Eliminação de recursão e chamadas duplicadas à API do Jules quando a opção "Todos" ('A') é selecionada, reutilizando a lista `pending` já obtida em memória.

### Refatoração SRP do Loop Autônomo (Inspirado no PR #12)
**Arquivo:** `agents/autonomous_loop.py`
- **Motivação:** `run_autonomous_loop` continha blocos extensos de lógica inline para injeção de contexto, despacho de sessão e merge de Git.
- **Implementação:**
  - Extraídas as funções auxiliares `_build_ai_context`, `_dispatch_jules_session` e `_handle_pr_merge`.
  - O PR #12 original foi fechado e descartado para evitar a aplicação indesejada de reformatação global do Ruff em 45 arquivos alheios ao escopo, integrando-se apenas a refatoração estritamente necessária de forma atômica e limpa.

