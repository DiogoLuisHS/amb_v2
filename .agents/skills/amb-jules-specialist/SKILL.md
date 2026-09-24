---
name: amb-jules-specialist
description: >-
  Operate, automate, and troubleshoot Google Jules cloud coding agent sessions in the AMB_V2 ecosystem. Use when creating sessions, streaming live outputs, approving plans, answering agent doubts, and safely merging PRs.
---

# ☁️ AMB Jules Specialist

Especialista no ciclo de vida e operações do **Google Jules** dentro do ecossistema `amb_v2`.

## 📌 Visão Geral & Arquitetura

O Google Jules é um agente de desenvolvimento em nuvem que executa em uma máquina virtual (Cloud VM) dedicada com clone do repositório, branch própria e capacidade de abrir Pull Requests no GitHub.

No `amb_v2`, a integração está localizada em:
- **Cliente Core:** [`amb_cli/integrations/jules/jules_client.py`](file:///c:/Users/DiogoHungaro/Desktop/Script/amb_v2/amb_cli/integrations/jules/jules_client.py) (Wrapper oficial da API REST v1alpha)
- **Ferramentas Modulares:** [`amb_cli/integrations/jules/tools/`](file:///c:/Users/DiogoHungaro/Desktop/Script/amb_v2/amb_cli/integrations/jules/tools/) (`status`, `sources`, `list_sessions`, `get_session`, `create_session`, `approve_plan`, `send_message`, `monitor_activities`, `merge_session_pr`, `cleanup_sessions`)
- **Sentinela / Watcher:** [`amb_cli/integrations/jules/jules_watcher.py`](file:///c:/Users/DiogoHungaro/Desktop/Script/amb_v2/amb_cli/integrations/jules/jules_watcher.py)

---

## 🚀 Comandos Essenciais da CLI (`amb jules`)

### 1. Diagnóstico e Status da Integração
Verifica conectividade, credenciais da API Key, repositórios vinculados e sessões ativas do repositório:
```bash
amb jules status [--json]
```

### 2. Listar Fontes/Repositórios Conectados
Exibe os repositórios GitHub vinculados à conta Jules:
```bash
amb jules sources [--json]
```

### 3. Listar Sessões Recentes
Lista sessões do repositório ativo com suporte a filtros e paginação:
```bash
# Sessões do repositório ativo:
amb jules list --limit 10

# Filtrar por estado específico:
amb jules list --state AWAITING_USER_FEEDBACK

# Listar de todos os repositórios da conta:
amb jules list --all --json
```

### 4. Criar uma Nova Sessão
Despacha uma tarefa para uma nova VM na nuvem:
```bash
amb jules create --prompt "Implementar validação de input no formulário de login" --title "Auth Input Validation" --branch main
```
*Suporta IDs puros, rotas `sessions/<id>` ou URLs completas do navegador (`https://jules.google.com/session/<id>`).*

### 5. Acompanhar em Tempo Real (Live Streaming)
Mostra o fluxo de pensamento, comandos bash e logs em tempo real:
```bash
amb jules get <SESSION_ID_OU_URL> --watch
```
*Para obter saída em JSON puro:*
```bash
amb jules get <SESSION_ID_OU_URL> --json
```

### 6. Aprovar o Plano do Agente
Quando a sessão atinge o estado `AWAITING_PLAN_APPROVAL`:
```bash
amb jules approve <SESSION_ID_OU_URL> [--force]
```

### 7. Responder Dúvidas do Agente
Quando a sessão atinge `AWAITING_USER_FEEDBACK`:
```bash
# Resposta manual direta:
amb jules reply <SESSION_ID> -m "Utilize o schema existente em auth/schemas.py"

# Resposta automática assistida por Gemini (Auto-Advisor):
amb jules reply <SESSION_ID> --auto-approve
```

### 8. Fazer Merge Seguro do PR
Detecta o PR aberto pelo Jules (que o Jules sempre cria como Draft), converte automaticamente em Ready for Review (`gh pr ready`), aprova no GitHub, valida o QA localmente e faz merge:
```bash
amb jules merge <SESSION_ID_OU_URL> [--branch main]

# Ou detectar automaticamente o PR mais recente:
amb jules merge --auto-latest
```

### 9. Limpar Sessões Antigas (Preservação de Cota)
Remove sessões `COMPLETED` ou `FAILED` para manter o workspace limpo:
```bash
amb jules clean --failed -f
amb jules clean --merged -f
```

---

## ⚙️ Regras de Implementação & Gotchas

1. **Normalização Universal de IDs:**
   - O `JulesClient.normalize_session_id(session_id)` extrai automaticamente o ID limpo de números puros, caminhos `sessions/<id>` e URLs `https://jules.google.com/session/<id>`. Todos os métodos e comandos aceitam qualquer um desses formatos de forma intercambiável.

2. **Estrutura de Resposta de Atividades:**
   - A API do Jules pode retornar `activities` tanto como uma lista direta `[ { ... } ]` quanto envelopada em dict `{ "activities": [...] }`.
   - **Padrão Obrigatório:**
     ```python
     acts = act_res if isinstance(act_res, list) else act_res.get("activities", [])
     ```

3. **Ordenação Cronológica de Atividades:**
   - A API retorna atividades em ordem decrescente (mais recentes primeiro).
   - Para síntese de contexto ou logs, inverta a lista com `reversed(acts)` para obter ordem cronológica correta.

4. **Subprocessos sem `shell=True`:**
   - Comandos Git em `merge_session_pr.py` usam `shell=False` passando listas de argumentos (`["git", "pull", "origin", branch]`) para evitar injeção de comandos via nomes de branch.

5. **Conversão de Draft PRs Automática:**
   - O Google Jules cria Pull Requests em modo Draft por padrão. O utilitário `merge_session_pr` dispara `gh pr ready` antes do merge, dispensando qualquer ação manual na interface web do GitHub.
