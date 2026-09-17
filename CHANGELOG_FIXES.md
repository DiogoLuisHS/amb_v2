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

### Bug #14 — Tipo de Dispositivo hardcoded como `"DESKTOP"` no Stitch SDK e Pipeline
**Arquivos:** `integrations/stitch/stitch_client.py`, `pipeline/pipeline.py`, `cli_modules/cli_parsers.py`, `cli_modules/cli_handlers.py`, `config/config.py`
**Causa:** O cliente e as ferramentas do Stitch forçavam `"DESKTOP"` como padrão para todas as gerações de tela, impedindo que projetos mobile ou agnósticos tivessem seus layouts gerados apropriadamente.
**Fix aplicado:**
1. Remoção total do padrão `"DESKTOP"` hardcoded.
2. Implementação de resolução genérica via `get_device_type(default=None)`: flag `--device` > `STITCH_DEVICE_TYPE` / `DEVICE_TYPE` no `.env` > `stitch.device` / `device_type` em `amb_project.json` > `None` (parâmetro omitido, deixando o Stitch decidir).
3. Suporte aos tipos de dispositivo oficiais do Stitch SDK: `"MOBILE"`, `"DESKTOP"`, `"TABLET"`, `"AGNOSTIC"`.

### Bug #15 — Funções e Modelos Fictícios no Runner e Cliente do Stitch
**Arquivos:** `integrations/stitch/stitch_client.mjs`, `integrations/stitch/stitch_client.py`, `integrations/stitch/tools/*.py`
**Causa:** O cliente invocava ferramentas inexistentes no MCP do Stitch (`upload_design_md`, `create_design_system_from_design_md`) e referia um modelo inexistente `GEMINI_3_8_FLASH` em vez de consultar a especificação oficial do `@google/stitch-sdk`.
**Fix aplicado:**
1. Remoção completa de ferramentas fictícias no runner Node.js e Python.
2. Alinhamento estrito com os 12 tools oficiais do MCP Server do Stitch (`create_project`, `get_project`, `list_projects`, `list_screens`, `get_screen`, `generate_screen_from_text`, `edit_screens`, `generate_variants`, `create_design_system`, `update_design_system`, `list_design_systems`, `apply_design_system`) e a virtual tool `download_assets`.
3. Sincronização de `design.md` via canal nativo do SDK: `theme.designMd` em `create_design_system` e `update_design_system`.
4. Correção do modelo de geração: remoção do modelo falso, deixando opcional (Stitch default) ou suportando `GEMINI_3_FLASH` / `GEMINI_3_1_PRO`.

### Bug #16 — `amb check` reportava falso-negativo de autenticação do GitHub CLI (`gh`) e truncamento de leading space no git status
**Arquivos:** `config/config.py`, `integrations/git/git_service.py`
**Causa:**
1. Em `config/config.py:378`, a chamada `git.check_gh_auth(cwd=root)` sofria `TypeError: check_gh_auth() got an unexpected keyword argument 'cwd'`, sendo silenciada por um `except: pass` e marcando `"authenticated": false` mesmo com o `gh` perfeitamente autenticado no sistema.
2. Em `integrations/git/git_service.py`, `get_status` utilizava `res.stdout.strip()`, eliminando o leading space do primeiro caractere da primeira linha no formato porcelain (ex: ` M README.md` virava `M README.md`, gerando falso arquivo staged `M EADME.md`).
**Fix aplicado:**
1. Parâmetro `cwd: Optional[str] = None` e `fail_silently: bool = False` adicionados explicitamente à assinatura de `check_gh_auth` em `GitService`.
2. Em `config/config.py`, chamada atualizada para `git.check_gh_auth(cwd=root, fail_silently=True)`. O comando `amb check --json` agora reporta `"authenticated": true` com total precisão.
3. Em `GitService.get_status`, substituído `.strip()` por `.rstrip()` e sanitizado `.is_clean` para preservar os identificadores de coluna na saída porcelain do Git.

### Bug #17 — Vazamento de sessões sem `sourceContext`, sobrescrita indevida de branch explícita e falha com URLs web no Google Jules
**Arquivos:** `integrations/jules/jules_client.py`, `integrations/jules/tools/*.py`, `cli_modules/cli_handlers.py`
**Causa:**
1. Em `list_sessions`: quando um `repo_filter` era especificado, sessões que não possuíam `sourceContext.source` eram incluídas indevidamente pelo bloco `else: filtered.append(s)`, vazando sessões de outros projetos.
2. Em `create_session`: a verificação `if not base_branch or base_branch in ["develop", "main"]` sobrescrevia a branch explicitamente definida pelo usuário se a branch local atual do Git fosse diferente, impedindo criar sessões mirando branches específicas.
3. Em `get_session`, `send_message`, `approve_plan`, `delete_session` e ferramentas de linha de comando: a passagem de URLs completas do navegador (`https://jules.google.com/session/<id>`) causava erros HTTP 404/400 ou requisições malformadas por falta de normalização de rotas REST.
### Bug #18 — Inversão cronológica no `TurnHistoryExtractor` causava falsa aprovação de plano em vez de resposta no chat
**Arquivos:** `amb_cli/agents/auto_reply_core/turn_extractor.py`, `amb_cli/agents/loop_core/session_assistant.py`, `amb_cli/agents/autonomous_loop.py`
**Causa:**
1. A API do Google Jules retorna a lista de atividades em ordem cronológica (da mais antiga para a mais recente). O `TurnHistoryExtractor.get_last_conversation_turn` iterava a lista a partir do índice 0 assumindo que vinha da mais recente para a mais antiga.
2. Como resultado, um evento antigo `planGenerated` (do início da sessão) era avaliado primeiro e definia `has_unapproved_plan = True`.
3. Quando o agente Jules fazia uma pergunta no chat (`agentMessaged`) em etapas subsequentes, o monitor interpretava erroneamente que havia um plano a ser aprovado e chamava `approvePlan` em vez de responder à pergunta no chat via `sendMessage`.
**Fix aplicado:**
1. `TurnHistoryExtractor.get_last_conversation_turn` agora ordena estritamente as atividades por `createTime` decrescente antes de analisar os turnos.
2. Mensagens recentes do agente (`agentMessaged`) são priorizadas sobre planos históricos antigos, garantindo que `last_speaker = 'AGENT'` quando há dúvida no chat.
3. No `session_assistant.py` e `autonomous_loop.py`, a aprovação de plano exige estritamente `has_unapproved_plan and last_speaker == 'PLAN'`. Se `last_speaker == 'AGENT'`, o fluxo despacha obrigatoriamente para o Auto-Reply cognitivo (`advise_and_reply`).
4. Reconhecimento de todos os estados de espera do Jules: `AWAITING_USER_FEEDBACK`, `AWAITING_USER_ACTION`, `AWAITING_INPUT`, `AWAITING_PLAN_APPROVAL`.

### Refatoração Arquitetural — Atomização do Pacote `amb_cli/agents` e Alinhamento com `.agents/rules/`
**Arquivos:** `amb_cli/agents/autonomous_loop.py`, `amb_cli/agents/loop_core/*`, `amb_cli/agents/auto_reply_core/*`, `amb_cli/agents/monitor.py`, `amb_cli/agents/local_agent_runner.py`
**Implementação:**
1. **Decomposição do `autonomous_loop.py` (Regras 01 e 02):**
   - Reduzido de 490 linhas para 276 linhas através da extração de responsabilidades para `amb_cli/agents/loop_core/`:
     - `session_assistant.py` (121 linhas): monitoramento contínuo da sessão, aprovação de planos e auto-resposta cognitiva.
     - `cycle_dispatcher.py` (115 linhas): síntese de contexto via `ai_context_builder`, despacho de sessões no Jules e auto-merge no Git.
2. **Refatoração DRY e Eliminação de Dead Imports (Regras 03 e 04):**
   - `turn_extractor.py`: criada a função auxiliar privada `_extract_text_from_node`, reduzindo duplicações de código no parsing de atividades e removendo imports não utilizados.
   - `cognitive_advisor.py`: migração completa de manipulação de caminhos para `pathlib.Path`, resolução centralizada das regras ativas em `.agents/rules/` e logging estruturado com `log_error`.
   - `feedback_dispatcher.py`: suporte completo a `AWAITING_USER_ACTION` e correspondência de estados insensível a maiúsculas/minúsculas.
3. **Validação de Integridade:**
   - 100% dos testes unitários verdes (92/92 aprovados em `tests/`).
   - Todos os arquivos do pacote `amb_cli/agents/` atendem aos limites estritos de SRP e contagem de linhas (<=300 linhas).

---

## 🚀 Features Implementadas

### F2-M3 — Alinhamento Estrito & Modernização da Integração Google Stitch SDK
**Arquivos:** `integrations/stitch/stitch_client.py`, `integrations/stitch/stitch_client.mjs`, `integrations/stitch/tools/*`, `cli_modules/*`, `.agents/skills/amb-stitch-specialist/SKILL.md`
**Implementação:**
- Suporte nativo completo aos 12 tools oficiais do Stitch MCP Server e aos métodos de domínio do SDK (`upload`, `downloadAssets`).
- Novos comandos CLI:
  - `amb stitch list`: Lista telas do projeto com dimensões e títulos.
  - `amb stitch download -o <dir>`: Baixa telas e assets autônomos para uso local.
  - `amb stitch project`: Exibe metadados e configurações do projeto ativo.
  - `amb stitch sync -f <file>`: Sincroniza tokens em Markdown com o tema oficial do Stitch.
- Facade `integrations/stitch/tools/download_assets.py` para download automatizado de telas e assets.
- Resolução dinâmica de dispositivos suportando `MOBILE`, `DESKTOP`, `TABLET` e `AGNOSTIC`.
- Suite de testes unitários abrangente em `tests/test_stitch_integration.py` (15 testes cobrindo todo o ciclo).

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

### F1-M5 — Extração e Centralização do `QualityGatekeeper` (SRP & DRY)
**Arquivos:** `pipeline/quality_gatekeeper.py`, `pipeline/__init__.py`, `pipeline/pipeline.py`, `integrations/jules/tools/merge_session_pr.py`, `config/config.py`, `tests/test_quality_gatekeeper.py`.
- **Motivação:** A rotina de validação e execução de comandos de QA (`test`, `typecheck`, `build`, `lint`) estava duplicada linha por linha entre `pipeline/pipeline.py` e `integrations/jules/tools/merge_session_pr.py`, violando o Princípio de Responsabilidade Única (SRP) e o princípio DRY.
- **Implementação:**
  - Criado o módulo `pipeline/quality_gatekeeper.py` com a classe `QualityGatekeeper`.
  - Métodos coesos e desacoplados:
    - `detect_qa_commands(repo_root)`: Recupera comandos do `.amb/amb_project.json` (com suporte prioritário a `repo_root` em `load_project_json(repo_root)`) com fallback determinístico ao `ProjectAnalyzer`.
    - `execute_command(cmd_str, label, cwd)`: Executa passos individuais de validação via subprocess com tratamento de saída, formatação visual e captura de falhas em Windows, Linux e macOS.
    - `run_qa(repo_root)`: Executa toda a suíte de validação do projeto ativo e reporta status consolidado.
  - Eliminação de todo o código duplicado de QA em `pipeline/pipeline.py` e `merge_session_pr.py` (tanto no pós-merge quanto no pós-patch), delegando exclusivamente ao `QualityGatekeeper`.
  - Suíte de testes unitários dedicada criada em `tests/test_quality_gatekeeper.py` (4 testes passando).

### F1-M7 — Refatoração e Modernização da Integração Google Jules & Desacoplamento CLI
**Arquivos:** `integrations/jules/jules_client.py`, `integrations/jules/jules_watcher.py`, `integrations/jules/tools/merge_session_pr.py`, `integrations/jules/tools/cleanup_sessions.py`, `cli_modules/cli_handlers.py`, `integrations/jules/tools/*.py`, `.agents/skills/amb-jules-specialist/SKILL.md`, `tests/test_jules_integration.py`.
- **Motivação:**
  - A extração de Pull Requests da sessão Jules era divergente entre o `jules_watcher.py`, `merge_session_pr.py` e `cleanup_sessions.py` (alguns checavam `outputs`, outros regex em `activities`).
  - O subcomando `amb jules get` não permitia acompanhamento contínuo em streaming.
  - O handler CLI `cli_modules/cli_handlers.py` manipulava a variável global `sys.argv = [...]` para despachar `amb jules merge` e `amb jules cleanup`.
  - Os 7 scripts utilitários em `integrations/jules/tools/` continham blocos manuais de 10 linhas de manipulação de `sys.path`.
- **Implementação:**
  - **Canonicidade na Detecção de PRs (`JulesClient.extract_pull_request`):** Método centralizado na classe `JulesClient` com suporte a `outputs` (lista de outputs estruturados com `pullRequest`, `url` e `title` ou dict) com fallback robusto por regex em `activities`.
  - **Streaming em Tempo Real (`stream_session_activities`):** Implementado no `JulesWatcher` e exposto na CLI via `amb jules get <session_id> --watch` (`-w`), exibindo atualizações progressivas de passos e ações do Jules até a finalização da sessão.
  - **Desacoplamento Completo da CLI:** Expostas funções canônicas `run_merge_session_pr(...)` e `run_cleanup_sessions(...)`. Eliminada 100% da mutação de `sys.argv` em `cli_modules/cli_handlers.py`.
  - **Modernização de Ferramentas de Fachada:** Migrados todos os 7 scripts em `integrations/jules/tools/` (`create_session.py`, `get_session.py`, `list_sessions.py`, `list_sources.py`, `approve_plan.py`, `send_message.py`, `monitor_activities.py`) para utilizar `ensure_amb_env()`.
  - **Atualização do Skill Specialist:** `.agents/skills/amb-jules-specialist/SKILL.md` atualizado para apontar para `integrations/jules/jules_watcher.py`.
  - Suíte de testes unitários criada em `tests/test_jules_integration.py` (6 testes passando).

---

### F1-M10 — Modernização Completa da Integração Google Stitch SDK (@google/stitch-sdk)
**Arquivos:** `integrations/stitch/stitch_client.py`, `integrations/stitch/stitch_client.mjs`, `integrations/stitch/tools/*.py`, `integrations/stitch/tools/list_screens.py`, `config/config.py`, `config/__init__.py`, `pipeline/pipeline.py`, `cli_modules/cli_parsers.py`, `cli_modules/cli_handlers.py`, `.agents/skills/amb-stitch-specialist/SKILL.md`, `README.md`, `tests/test_stitch_integration.py`.
- **Motivação:**
  - O runner do Stitch não validava a presença do executável Node.js ou do pacote `@google/stitch-sdk`, resultando em falhas crípticas de subprocess.
  - O tipo de dispositivo (`device_type`) estava fixado como hardcoded `"DESKTOP"` em múltiplos locais, desrespeitando projetos mobile/tablet ou configurações do usuário.
  - Não existia método nem comando para listar telas (`list_screens`), embora o runner Node.js suportasse a chamada.
  - Faltava suporte a salvar o HTML/DOM gerado pelo Stitch diretamente em disco (`--output`).
  - Os scripts em `integrations/stitch/tools/` continham o mesmo bloco legado de manipulação manual de `sys.path`.
  - Não existiam testes unitários automatizados para o Stitch em `tests/`.
- **Implementação:**
  - **Resolução Dinâmica e Genérica do Dispositivo Alvo (`get_device_type`):**
    - Adicionado `get_device_type()` em `config/config.py` para resolver a preferência do projeto:
      1. Argumento explícito da CLI (`--device` / `--device-type`).
      2. Variáveis `STITCH_DEVICE_TYPE` ou `DEVICE_TYPE` no `.env`.
      3. Campo `stitch.device` ou `device_type` no `.amb/amb_project.json`.
      4. `None` caso não especificado (deixando o Stitch SDK aplicar seu comportamento padrão sem forçar `"DESKTOP"`).
    - Eliminado qualquer valor default `"DESKTOP"` hardcoded em `StitchClient.generate_screen()`, `sync_design_system()`, `pipeline.py`, `cli_parsers.py` e `cli_handlers.py`.
  - **Diagnóstico Preventivo de Runtime:** `StitchClient` verifica preventivamente `shutil.which("node")` e captura erros `MODULE_NOT_FOUND` do runner com hints claros para instalação do Node.js e `npm install`.
  - **Novos Métodos Canônicos:**
    - `list_screens(project_id)`: Consulta e normaliza lista de telas com IDs, títulos, dimensões e descrições.
    - `get_project(project_id)`: Consulta metadados do workspace e do design system vinculado.
    - `save_screen_html(screen_data, output_path)`: Persiste o DOM HTML da tela em arquivo local.
    - `call_tool(tool_name, payload)`: Despacha ferramentas dinâmicas arbitrárias do SDK via JSON-RPC.
  - **Suporte a `--output` e `--json`:** `generate_screen`, `edit_screen` e `get_screen` aceitam `output_file` para salvar o HTML automaticamente.
  - **Runner Node.js Aprimorado:** `stitch_client.mjs` lê `STITCH_PROJECT_ID` automaticamente do arquivo `.env` e suporta `list_projects`.
  - **Fachadas Modernizadas & Nova Ferramenta:** Substituído o boilerplate legado de `sys.path` por `ensure_amb_env()` em todas as 5 ferramentas existentes e criada a nova ferramenta `list_screens.py`.
  - **CLI Enriquecida:** Novos subcomandos `amb stitch list`, `amb stitch call`, flags `--output` / `-o` e `--json` em todos os comandos do Stitch.
  - **Atualização de Documentação e Skills:** Atualizados `amb-stitch-specialist/SKILL.md` e a tabela de comandos do `README.md`.
  - Suíte de testes unitários dedicada criada em `tests/test_stitch_integration.py` (12 testes passando).

---

---

### F1-M6 — Unificação de Regras do Repositório (RulesManager) & Modernização da Integração Google Antigravity SDK
**Arquivos:** `config/rules_manager.py`, `config/__init__.py`, `integrations/antigravity/antigravity_client.py`, `integrations/antigravity/tools/synthesize_prompt.py`, `integrations/antigravity/tools/validate_architecture.py`, `agents/auto_reply_core/cognitive_advisor.py`, `pipeline/pipeline.py`, `cli_modules/cli_parsers.py`, `cli_modules/cli_handlers.py`, `.agents/skills/amb-antigravity-specialist/SKILL.md`, `README.md`, `tests/test_antigravity_integration.py`.
- **Motivação:**
  - Existiam premissas tecnológicas gravadas *a priori* (`"TypeScript estrito"`, `"0 any"`, `"contratos Zod"`) espalhadas em `antigravity_client.py`, `pipeline.py` e `cognitive_advisor.py`, violando o princípio poliglota agnóstico do AMB_V2.
  - A lógica de descoberta de diretórios de regras (`.antigravity/rules/` vs `.gemini/rules/`), corte de caracteres, fechamento de fences markdown e caching estava duplicada e desarticulada em 4 arquivos distintos.
  - O arquivo `antigravity_client.py` continha um bloco duplicado de código `if __name__ == "__main__":` no final.
  - Não existiam subcomandos unificados sob `amb antigravity` / `amb agy`.
  - As ferramentas em `integrations/antigravity/tools/` usavam o loop arcaico de `sys.path`.
- **Implementação:**
  - **Criação do `RulesManager` (`config/rules_manager.py`):**
    - Descoberta hierárquica e prioritária de regras: diretório explícito ➔ `.antigravity/rules/` ➔ `.gemini/rules/` ➔ `.agents/rules/` ➔ `rules/` ➔ arquivos de regras na raiz (`AGENTS.md`, `GEMINI.md`).
    - Fechamento seguro de code fences markdown abertas (```` ``` ````) quando trechos são truncados por orçamento de tokens.
    - Sanitização de frontmatter YAML e comentários HTML.
    - Cache em memória por diretório e tamanho, com método de invalidação `RulesManager.invalidate_cache()`.
    - Filtragem contextual por especialidade de agente (`filter_rules_for_agent`).
  - **Erradicação de Premissas Tecnológicas *A Priori*:**
    - Substituição de suposições fixas de TypeScript/Zod por regras derivadas exclusivamente do projeto ativo via `RulesManager`.
    - Validação poliglota (`validate_code`), detectando a linguagem a partir da extensão do arquivo (`.py`, `.go`, `.ts`, `.rs`, `.java`, etc.).
  - **Modernização de `AntigravityClient`:**
    - Resolução hierárquica dinâmica de modelo cognitivo (`model` explícito > `ANTIGRAVITY_MODEL`/`GEMINI_MODEL` no `.env` > `amb_project.json` > padrão `"gemini-3.8-flash"`).
    - Método de diagnóstico unificado `get_status()` retornando estado do runtime, API Key, `agy` CLI e regras ativas.
    - Parâmetros dinâmicos de geração (`temperature`, `max_output_tokens`).
  - **Desacoplamento e Injeção de Regras:**
    - `CognitiveAdvisor` e `PipelineOrchestrator` agora delegam a extração de regras diretamente ao `RulesManager`.
  - **Fachadas Modernizadas:**
    - `synthesize_prompt.py` e `validate_architecture.py` migrados para `ensure_amb_env()`, expondo as funções de serviço `run_synthesize_prompt` e `run_validate_architecture`.
  - **Nova CLI Unificada `amb antigravity` (alias `amb agy`):**
    - Subcomandos: `status` (ou `check`), `rules`, `prompt` (ou `synthesize`), `validate` (ou `audit`), `run` (ou `eval`).
  - **Atualização de Documentação e Skills:**
    - Atualizados `.agents/skills/amb-antigravity-specialist/SKILL.md` e `README.md`.
  - Suíte de testes unitários criada em `tests/test_antigravity_integration.py` (12 testes passando).

---

### F1-M7 — Modernização e Integração Consolidada de Git & GitHub CLI (`gh`)
**Arquivos:** `integrations/git/git_service.py`, `integrations/git/tools/git_status.py`, `integrations/git/tools/pr_manager.py`, `integrations/git/tools/sync_branch.py`, `cli_modules/cli_parsers.py`, `cli_modules/cli_handlers.py`, `config/bootstrap.py`, `config/config.py`, `README.md`, `tests/test_git_service.py`.
- **Motivação:**
  - O `GitService` continha apenas operações básicas e dispersas; não possuía métodos estruturados para `ahead/behind`, diff granular, `stash`, `fetch` ou ciclo de vida completo de Pull Requests (`get`, `create`, `close`).
  - A ferramenta `amb check` sofria com falso-negativo de autenticação do `gh`.
  - Não existiam subcomandos unificados sob `amb git` nem fachadas modulares em `integrations/git/tools/`.
- **Implementação:**
  - **Expansão do `GitService` (`integrations/git/git_service.py`):**
    - `get_detailed_status(cwd)`: diagnóstico consolidado com `branch`, `upstream`, contagem `ahead`/`behind`, status da working tree (`staged`, `unstaged`, `untracked`) e repositório GitHub detectado.
    - `get_upstream_branch(cwd)` e `get_ahead_behind(cwd)` via `git rev-parse` e `git rev-list`.
    - `get_diff(file_path, base_branch, cached, cwd)` para inspeções pontuais ou de branch completa.
    - `fetch(remote, prune, cwd)`, `stash(action, message, cwd)`, `create_branch(branch_name, from_branch, checkout, cwd)`.
    - Ciclo de vida de PRs: `get_pr(pr_number, repo_name)`, `create_pr(title, body, base, head, draft, repo_name)`, `close_pr(pr_number, comment, delete_branch, repo_name)`.
    - Sanitização de chamadas `check_gh_auth(cwd=..., fail_silently=True)` e preservação de leading spaces no formato porcelain.
  - **Criação de Ferramentas Facade Modulares (`integrations/git/tools/`):**
    - `git_status.py`: `run_git_status(as_json=False, cwd=None)` com visual rico no terminal e exportação JSON.
    - `pr_manager.py`: `run_pr_manager(action, ...)` para gerenciar PRs (`list`, `get`, `create`, `ready`, `approve`, `merge`, `close`).
    - `sync_branch.py`: `run_sync_branch(remote="origin", branch=None, auto_stash=True)` com preservação automática via stash.
    - Registro de `integrations/git/tools` no `CANONICAL_SUBMODULES` de `config/bootstrap.py`.
  - **CLI `amb git` Unificada (`cli_modules/cli_parsers.py` & `cli_modules/cli_handlers.py`):**
    - Subcomandos:
      - `amb git status` (flags `--json`): visão completa de branches, upstream, commits ahead/behind e status da working tree.
      - `amb git sync` (flags `-r/--remote`, `-b/--branch`, `--no-stash`): sincronização segura com stash automático.
      - `amb git diff` (flags `-f/--file`, `-b/--base`, `--cached`): exibição de diffs staged ou uncommited.
      - `amb git pr` (sub-ações `list`, `get`, `create`, `ready`, `approve`, `merge`, `close`).
  - **Documentação Atualizada:**
    - Seção "Git & GitHub CLI (`amb git`)" adicionada à tabela de referência do `README.md`.
  - Suíte de testes unitários expandida em `tests/test_git_service.py` (de 7 para 12 testes passando).

---

### F1-M8 — Modernização e Robustecimento da Integração Google Jules REST API
**Arquivos:** `integrations/jules/jules_client.py`, `integrations/jules/tools/*.py`, `cli_modules/cli_parsers.py`, `cli_modules/cli_handlers.py`, `.agents/skills/amb-jules-specialist/SKILL.md`, `integrations/jules/README.md`, `README.md`, `tests/test_jules_integration.py`.
- **Motivação:**
  - O `JulesClient` não possuía normalização de URLs/IDs, quebrando quando o usuário colava a URL do navegador.
  - O método `list_sessions` sofria de vazamento de sessões sem `sourceContext`.
  - O método `create_session` sobrescrevia a branch explicitamente definida pelo usuário caso coincidisse com valores padrão.
  - Várias ferramentas de fachada (`list_sources`, `list_sessions`, `send_message`) continham lógica exclusiva em seus blocos `main()`, impossibilitando uso programático ou teste direto.
  - Faltavam comandos de diagnóstico (`status`) e de listagem de fontes (`sources`) sob `amb jules`.
- **Implementação:**
  - **Robustecimento do `JulesClient` (`integrations/jules/jules_client.py`):**
    - `normalize_session_id(session_id)`: normalização universal aceitando ID numérico, rota `sessions/<id>` ou URL completa do console do Jules (`https://jules.google.com/session/...`).
    - `get_source(source_name)`: consulta de fontes e repositórios conectados.
    - `get_status(repo_filter)`: diagnóstico consolidado com conectividade, chave, fontes e contagem de sessões ativas por estado.
    - `list_sessions`: suporte a `state_filter` e correção do filtro estrito de repositório.
    - `create_session`: respeito estrito a branches manuais sem sobrescrita.
  - **Padronização das Ferramentas de Fachada (`integrations/jules/tools/`):**
    - `list_sources.py`: expõe `run_list_sources(...)` com suporte a `--json`.
    - `list_sessions.py`: expõe `run_list_sessions(...)` com filtros por `--all`, `--repo`, `--state` e `--json`.
    - `get_session.py`: expõe `run_get_session(...)` com suporte integrado a `--watch` e `--json`.
    - `create_session.py`: expõe `run_create_session(...)` com suporte a `--branch` / `-b` e `--json`.
    - `approve_plan.py`: expõe `run_approve_plan(...)` com guardrail integrado de validação de plano e flag `--force`.
    - `send_message.py`: expõe `run_send_message(...)` com guardrail contra mensagens consecutivas e flag `--force`.
    - `monitor_activities.py`: delegando ao streaming avançado `stream_session_activities`.
  - **CLI `amb jules` Enriquecida (`cli_modules/`):**
    - Novos subcomandos de primeira classe: `amb jules status` e `amb jules sources`.
    - Suporte a filtros (`--all`, `--repo`, `--state`), flags de controle (`--force`, `--branch`) e `--json` em todos os subcomandos.
    - Suporte a argumento posicional transparente para ID ou URL de sessão em `get`, `approve`, `reply` e `merge`.
  - **Documentação e Skills:**
    - Atualizados `.agents/skills/amb-jules-specialist/SKILL.md`, `integrations/jules/README.md` e `README.md`.
  - Suíte de testes unitários expandida em `tests/test_jules_integration.py` (de 6 para 15 testes passando).

### Refatoração Arquitetural Modular: Separação de Código Fonte no Pacote `amb_cli/` (v2.3.0)
**Arquivos:** `amb_cli/`, `docs/`, `cli.py`, `amb_bootstrap.py`, `pyproject.toml`, `setup.py`, `tests/conftest.py`.
- **Motivação:**
  - Separar com precisão o código-fonte executável da aplicação em relação a arquivos de documentação, testes unitários, metadados e arquivos de configuração de repositório.
  - Eliminar poluição da raiz do projeto, mantendo um padrão de empacotamento canônico Python (PEP 517/621).
  - Preservar 100% do histórico Git de todos os módulos (`git mv`).
  - Assegurar retrocompatibilidade total com shims raiz (`python cli.py` e `import amb_bootstrap`) e compatibilidade nativa com módulo (`python -m amb_cli`).
- **Implementação:**
  - **Mapeamento e Migração para `amb_cli/`:**
    - Movidos 65 arquivos via `git mv`: `agents`, `architecture`, `cli_modules`, `config`, `gui`, `integrations`, `pipeline`, `cli.py`, `amb_bootstrap.py`.
    - Criado `amb_cli/__init__.py` com `__version__ = "2.3.0"` e auto-bootstrap.
    - Criado `amb_cli/__main__.py` viabilizando `python -m amb_cli`.
  - **Bootstrap Resiliente e Multi-Camada (`amb_cli/config/bootstrap.py`):**
    - `get_amb_root()` localiza deterministamente a raiz do repositório (`amb_v2`).
    - `get_amb_package_dir()` localiza o diretório do pacote (`amb_cli`).
    - `ensure_amb_env()` e injeção em tempo de importação configuram automaticamente `amb_root`, `pkg_dir` e todos os submódulos canônicos no `sys.path`.
  - **Shims de Retrocompatibilidade Raiz:**
    - Raiz `cli.py` delega transparentemente para `amb_cli.cli:main`.
    - Raiz `amb_bootstrap.py` delega para o bootstrap canônico dentro de `amb_cli`.
  - **Configuração de Pacote e Testes:**
    - `pyproject.toml` e `setup.py` atualizados para o pacote `amb-cli` v2.3.0 apontando para `amb = "amb_cli.cli:main"`.
    - Criado `docs/README.md` com documentação da nova topologia.
    - Criado `tests/conftest.py` e configurado `pytest` com `pythonpath = [".", "amb_cli"]`.
### Governança Cognitiva & Padrões de Desenvolvimento no `.agents/rules/`
**Arquivos:** `.agents/rules/01_single_responsibility.md`, `.agents/rules/02_atomization_and_ai_context.md`, `.agents/rules/03_dry_and_zero_redundancy.md`, `.agents/rules/04_code_quality_and_typing.md`, `.agents/rules/05_concise_documentation.md`, `.agents/rules/06_git_safety_and_compatibility.md`, `.agents/rules/amb_standards.md`.
- **Motivação:**
  - Estabelecer diretrizes claras, auditáveis e estruturadas para humanos e agentes de IA autônomos (Google Antigravity, Jules e Gemini Advisor).
  - Prevenir inchaço de arquivos ("god files"), garantir granularidade compatível com janelas de contexto de LLMs e eliminar redundâncias de lógica.
  - Padronizar tipagem estrita, hierarquia de exceções `AmbError`, simplificação de comentários e segurança em operações Git.
- **Implementação:**
  - **01 (SRP):** Separação estrita de camadas (`cli_parsers`, `cli_handlers`, `tools/`, `*client.py`) e declaração obrigatória de responsabilidade única.
  - **02 (Atomização & IA):** Limite de 100 a 250 linhas (teto de 300) para máxima atenção e raciocínio de modelos de linguagem sem alucinação.
  - **03 (DRY & Zero Redundância):** Proibição de lógica duplicada; herança unificada em `BaseGoogleClient` e resolução única de paths em `bootstrap.py`/`config.py`.
  - **04 (Qualidade, Tipagem & Erros):** Type hints em 100% das funções públicas, hierarquia `AmbError`, Fail-Fast (`require_env`) e suporte nativo a `--json`.
  - **05 (Documentação Concisa):** Docstrings declarativas de 1 a 3 linhas ("o quê" e "por quê"), eliminação de comentários óbvios e de ruídos/banners decorativos.
  - **06 (Segurança Git & Retrocompatibilidade):** Uso estrito de `git mv`, shims na raiz, guardrails (`--force`, `--dry-run`) e suíte de testes sempre verde.
  - **Manifesto Mestre (`amb_standards.md`):** Atualizado como índice consolidado de governança do ecossistema.
- **Validação:**
  - `amb agy rules`: 7 arquivos descobertos e sumarizados dinamicamente pelo `RulesManager`.
  - `amb validate amb_cli/cli.py`: Auditoria em tempo real pelo Antigravity confirmando a aplicação das novas regras.
  - Suíte de 92 testes automatizados 100% verde (`pytest`).

---

### Expansão da Suíte de Testes Automatizados (92 testes passando — 100% Green)
- Suíte expandida de 83 para **92 testes automatizados** com tempo de execução de ~2.1s:
  - `tests/test_jules_integration.py` (15 testes: outputs list, outputs dict, activities fallback, empty fallback, watcher delegate, normalize session ID, explicit branch create, auto branch create, strict list filtering, get status and sources, approve plan guardrails and force, send message guardrails and force, facade tools, CLI handlers, cleanup sessions dry run)
  - `tests/test_git_service.py` (12 testes)
  - `tests/test_antigravity_integration.py` (12 testes)
  - `tests/test_stitch_integration.py` (16 testes)
  - `tests/test_quality_gatekeeper.py` (4 testes)
  - `tests/test_setup_and_analyzer.py` (6 testes)
  - `tests/test_bootstrap.py` (5 testes)
  - `tests/test_base_google_client.py` (5 testes)
  - `tests/test_auto_reply_srp.py` (7 testes)
  - `tests/test_auto_reply.py` (8 testes retrocompatíveis)
  - `tests/test_ai_context_builder.py` (2 testes)









