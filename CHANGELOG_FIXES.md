# 📜 AMB_V2 — Changelog de Melhorias, Entregas & Bugs Corrigidos

> **Data de Atualização:** 2026-09-16 | **Versão:** 2.3.0  
> **Fonte Única da Verdade:** Este documento registra detalhadamente todas as melhorias arquiteturais, refatorações SRP, funcionalidades desenvolvidas e bugs corrigidos no ecossistema `amb_v2`. Para o planejamento futuro e backlog MoSCoW, consulte o [SUGGESTIONS.md](./SUGGESTIONS.md).

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

### Proteção contra Command Injection em Comandos Git
**Arquivos:** `integrations/jules/tools/merge_session_pr.py`, `agents/autonomous_loop.py`
- **Motivação:** Invocação de comandos do `git` com `shell=True` permitia vulnerabilidade potencial caso nomes de branches ou mensagens de commit contivessem caracteres de controle do shell.
- **Implementação:** Substituído `shell=True` por `shell=False` em todos os comandos `git checkout`, `git pull`, `git commit` e `git add`, passando argumentos via vetor seguro (`argv`).

### Resolução Segura de Binários no Executor de QA
**Arquivos:** `pipeline/pipeline.py`, `integrations/jules/tools/merge_session_pr.py`
- **Motivação:** Execução de comandos de validação pós-merge e pós-pipeline via `shell=True`. A remoção ingênua causava quebra no Windows ao rodar scripts como `npm run typecheck` (`npm.cmd`).
- **Implementação:** Integrado `shlex.split` com resolução segura do executável via `shutil.which` antes da execução, mantendo compatibilidade nativa com Windows (`.cmd`) sem recorrer ao shell para binários resolvidos.

### Criação da Suíte de Testes Unitários Automatizados
**Arquivos:** `tests/test_auto_reply.py`, `tests/test_ai_context_builder.py`
- **Motivação:** Ausência de suíte de testes automatizados (`pytest` coletava 0 testes).
- **Implementação:**
  - Criados testes cobrindo `extract_activity_text` para todas as variações de payload do Jules (`agentMessaged`, `userMessaged`, strings diretas e fallbacks).
  - Criados testes para a máquina de detecção de turnos (`get_last_conversation_turn`).
  - Criados testes de mapeamento e isolamento de estado por `copy.deepcopy` em `AIContextBuilder`.
  - 100% dos testes validados e passando com `pytest`.

### Inversão de Modo Padrão no Executor de Personas (`amb agent`)
**Arquivos:** `agents/local_agent_runner.py`, `cli_modules/cli_parsers.py`, `cli_modules/cli_handlers.py`
- **Motivação:** O comportamento padrão anterior requeria `--dispatch-jules` explícito para enviar à nuvem.
- **Implementação:**
  - O Google Jules passa a ser o despachante padrão para `amb agent --role <persona>` e `amb agent --all`.
  - Adicionadas as flags `--agy` e `--local` para executar personas localmente via Antigravity CLI sem consumir cota do Jules.

### Criação de Suíte Completa de Skills Especializadas do Antigravity
**Diretório:** `.agents/skills/`
- **Motivação:** Capacitar qualquer agente de IA ou desenvolvedor a atuar com maestria tanto nas ferramentas individuais quanto nas integrações cruzadas e no bootstrap em projetos consumidores.
- **Implementação:**
  - `amb-jules-specialist`: Ciclo de vida completo do Google Jules (sessões, streaming, auto-reply, merge de PRs).
  - `amb-stitch-specialist`: Geração de UI, extração de código e design systems com Stitch.
  - `amb-antigravity-specialist`: Personas locais (`agy`), calibração de prompts e diários de aprendizado.
  - `amb-autonomous-pipeline`: O loop contínuo de 7 etapas (`amb agent --loop`).
  - `amb-design-to-code`: Esteira Stitch ➔ Jules/AGY para codificação de protótipos em componentes de produção.
  - `amb-context-architecture`: Mapeamento de repositórios em camadas (`LAYERS_CONFIG`) com `ai_context_builder.py`.
  - `amb-consumer-bootstrap`: Guia e procedimentos para plugar e operar o `amb_v2` em qualquer projeto externo (`amb setup`).

### Suporte a Arquivos de Prompt no Módulo Stitch
**Arquivo:** `cli_modules/cli_handlers.py`
- **Motivação:** Prompts longos passados via argumento na linha de comando sofriam risco de truncamento ou escape incorreto de aspas.
- **Implementação:** Adicionado helper `_resolve_prompt` que lê automaticamente o conteúdo caso o parâmetro seja o caminho de um arquivo existente.

---

## 🏛️ Frente 1 (Arquitetura & Engenharia) — Implementação Must Have (2026-09-16)

### F1-M1 — Módulo Central de Bootstrap de Ambiente
**Arquivos:** `config/bootstrap.py`, `amb_bootstrap.py`, `config/__init__.py`, e refatoração em mais de 10 arquivos (`cli.py`, `pipeline/pipeline.py`, `agents/autonomous_loop.py`, `agents/local_agent_runner.py`, `architecture/ai_context_builder.py`, `architecture/db_schema_reader.py`, `dashboard/auto_advisor.py`, `config/setup_project.py`, etc.).
- **Motivação:** Mais de 12 arquivos repetiam um bloco de 15 a 20 linhas de manipulação manual e redundante de `sys.path`.
- **Implementação:**
  - Criado `config/bootstrap.py` com resolução determinística da raiz (`get_amb_root()`), injeção idempotente de submódulos canônicos (`ensure_amb_env()`) e utilitário `add_to_sys_path()`.
  - Criado `amb_bootstrap.py` na raiz para inicialização imediata via `import amb_bootstrap`.
  - Eliminados mais de 180 linhas de código boilerplate em todo o monorepo.
  - Criada suíte de testes unitários `tests/test_bootstrap.py`.

### F1-M2 — BaseGoogleClient com Retry Exponencial, Jitter e Mascaramento de Secrets
**Arquivos:** `integrations/common/base_google_client.py`, `integrations/common/__init__.py`, `integrations/jules/jules_client.py`, `integrations/antigravity/antigravity_client.py`.
- **Motivação:** Lógica de requisição, retries, headers de autenticação, captura de erros e decodificação JSON duplicadas entre `JulesClient` e `AntigravityClient`.
- **Implementação:**
  - Criado `BaseGoogleClient` com suporte a retry automático com **backoff exponencial e jitter aleatório (0.8x a 1.2x)** para quotas de IA (429, 500, 502, 503, 504) e instabilidades transitórias de socket/rede.
  - Implementado mascaramento de credenciais e tokens sensíveis (`AIzaSy...`, query params `key=...`, headers `X-Goog-Api-Key` e `Bearer`) nos logs e stack traces.
  - Normalização semântica de respostas de erro do Google em `ApiExecutionError` com hints contextuais.
  - `JulesClient` refatorado para herdar diretamente de `BaseGoogleClient`.
  - `AntigravityClient` integrado a `BaseGoogleClient` para chamadas REST ao Gemini.
  - Criada suíte de testes unitários `tests/test_base_google_client.py`.

### F1-M3 — Decomposição SRP de `auto_reply.py`
**Arquivos:** `agents/auto_reply_core/turn_extractor.py`, `agents/auto_reply_core/cognitive_advisor.py`, `agents/auto_reply_core/feedback_dispatcher.py`, `agents/auto_reply_core/__init__.py`, `agents/auto_reply.py`.
- **Motivação:** O módulo `auto_reply.py` acumulava mais de 700 linhas misturando parsing de conversação, inferência no Gemini, sanitização de Markdown e despacho REST para o Jules.
- **Implementação:**
  - Criado pacote `agents/auto_reply_core/` decomposto segundo o Princípio da Responsabilidade Única (SRP):
    - `TurnHistoryExtractor`: Responsável exclusivamente pelo parsing de atividades do Jules, extração de texto em múltiplos formatos e detecção do último interlocutor e status do turno.
    - `CognitiveAdvisor`: Responsável pelo carregamento/filtragem de regras arquiteturais, formatação de prompts contextuais e geração de pareceres técnicos via Antigravity/Gemini com fallbacks resilientes.
    - `JulesFeedbackDispatcher`: Responsável pelo despacho de mensagens à REST API do Jules, aprovação de planos (`:approvePlan`) e orquestração de menus interativos e resolução em lote.
  - `agents/auto_reply.py` refatorado como fachada leve delegando para as 3 classes com 100% de compatibilidade retroativa.
  - Criada suíte de testes unitários `tests/test_auto_reply_srp.py`.

### F1-M4 — Serviço Central de Abstração Git/GitHub (`GitService`)
**Arquivos:** `integrations/git/git_service.py`, `integrations/git/__init__.py`, `integrations/jules/tools/merge_session_pr.py`, `integrations/jules/tools/cleanup_sessions.py`, `config/setup_modules/project_analyzer.py`, `agents/autonomous_loop.py`, `pipeline/pipeline.py`, `integrations/jules/jules_client.py`.
- **Motivação:** Comandos `git` e `gh` eram executados via subprocess dispersos em pelo menos 6 locais distintos sem interface única, tratamento centralizado ou validação de autenticação.
- **Implementação:**
  - Criado `GitService` com operações locais do Git (`get_current_branch`, `get_remote_url`, `detect_github_repo`, `get_log_oneline`, `get_status`, `is_clean`, `checkout`, `pull`, `apply_patch`, `add_all_and_commit`, `push`).
  - Implementadas operações da GitHub CLI (`gh`) com validação fail-fast de autenticação (`check_gh_auth`), listagem de PRs (`list_open_prs`, `get_latest_open_pr`), marcação de ready (`mark_pr_ready`), code review (`approve_pr`) e merge com squash (`merge_pr`).
  - Migrados todos os locais que executavam comandos Git/GitHub dispersos para utilizar `GitService`.
  - Criada suíte de testes unitários `tests/test_git_service.py` com mocks seguros.

### F1-M8 — Extinção da Pasta `dashboard/` e Migração SRP dos Sentinelas
**Arquivos:** `cli_modules/alert_notifier.py`, `integrations/jules/jules_watcher.py`, `agents/monitor.py`, `tests/test_bootstrap.py`, `config/bootstrap.py`, `cli_modules/cli_handlers.py`.
- **Motivação:** A pasta de topo `dashboard/` era semanticamente incorreta (não continha interface gráfica/web, apenas scripts de sentinela CLI) e fragmentava a arquitetura do projeto.
- **Implementação:**
  - Extinção total da pasta `dashboard/`.
  - Migração de alertas e banners ANSI para `cli_modules/alert_notifier.py`.
  - Migração do sentinela especializado para `integrations/jules/jules_watcher.py`, com desduplicação da extração de PR (`extract_pull_request`).
  - Migração do loop de vigilância e auto-reply contínuo para `agents/monitor.py` (classe `UnifiedMonitor`), alinhado aos demais agentes autônomos.
  - Eliminação da fachada redundante `dashboard/auto_advisor.py`.
  - Remoção de `dashboard` de `CANONICAL_SUBMODULES` em `config/bootstrap.py` e atualização das rotas na CLI (`cli_modules/cli_handlers.py`).
  - Adicionado teste unitário `test_migrated_sentinel_modules()` em `tests/test_bootstrap.py`.


### F1-M9 — Modernização do Setup de Ambiente (`amb setup`), Diagnóstico (`amb check`), Proteção Preventiva `.env` e Persona Única (`engineer.md`)
**Arquivos:** `config/setup_project.py`, `config/setup_modules/project_analyzer.py`, `config/setup_modules/amb_provisioner.py`, `config/config.py`, `cli_modules/cli_parsers.py`, `cli_modules/cli_handlers.py`, `agents/autonomous_loop.py`, `agents/local_agent_runner.py`, `tests/test_setup_and_analyzer.py`.
- **Motivação:** O processo de setup possuía resolução frágil de diretório (busca ascendente por `.git` até 6 níveis arriscando poluir pastas-mãe), não persistia comandos de QA em `amb_project.json`, não verificava se o `.env` estava no `.gitignore`, e mantinha 10 personas legadas hardcoded e dispersas.
- **Implementação:**
  - **Decomposição Modular (SRP):** Extraídos `ProjectAnalyzer` e `AmbProvisioner` para `config/setup_modules/`.
  - **Detecção Avançada & QA:** Suporte completo a Go (`go.mod`), Rust (`Cargo.toml`), gerenciadores modernos de Python (`uv`, `poetry`), npm/pnpm/yarn/bun e monorepos (`pnpm-workspace`, `turbo`, `lerna`). Inferência e persistência explícita de `typecheck`, `test`, `build` e `lint` no schema v2 de `.amb/amb_project.json`.
  - **Segurança Preventiva:** `ensure_gitignore_security()` insere automaticamente `.env`, `.env.local` e `.amb/telemetry.jsonl` no `.gitignore` sem corromper comentários existentes. Criação automática de `.env.example` sanitizado.
  - **Persona Única Genérica de Exemplo:** Eliminação das 10 personas legadas e consolidação em `engineer.md` e diário `engineer.md`, integrando contexto de QA específico da stack detectada.
  - **Diagnóstico Modernizado (`amb check`):** Verificação de status Git, autenticação GitHub CLI (`gh`), credenciais mascaradas, binários de QA via `shutil.which`, verificação de segurança no `.gitignore` e suporte total à flag `--json`.
  - **Novas Opções na CLI:** `amb setup --force`, `--path <dir>`, `--dry-run`, `amb check --json`.

### Expansão da Suíte de Testes Automatizados (40 testes passando)
- Suíte expandida de 34 para **40 testes automatizados** com tempo de execução de ~0.47s:
  - `tests/test_setup_and_analyzer.py` (6 testes novos: detecção Python, Node, Go, provisionamento, dry-run e diagnóstico JSON)
  - `tests/test_bootstrap.py` (5 testes)
  - `tests/test_base_google_client.py` (5 testes)
  - `tests/test_auto_reply_srp.py` (7 testes)
  - `tests/test_git_service.py` (7 testes)
  - `tests/test_auto_reply.py` (8 testes retrocompatíveis)
  - `tests/test_ai_context_builder.py` (2 testes)





