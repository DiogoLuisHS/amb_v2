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
- **Cliente Core:** [`integrations/jules/jules_client.py`](file:///c:/Users/DiogoHungaro/Desktop/Script/amb_v2/integrations/jules/jules_client.py) (Wrapper oficial da API REST)
- **Ferramentas CLI:** [`integrations/jules/tools/`](file:///c:/Users/DiogoHungaro/Desktop/Script/amb_v2/integrations/jules/tools/) (`create_session`, `get_session`, `approve_plan`, `reply_session`, `merge_session_pr`, `cleanup_sessions`)
- **Sentinela / Watcher:** [`dashboard/watchers/jules_watcher.py`](file:///c:/Users/DiogoHungaro/Desktop/Script/amb_v2/dashboard/watchers/jules_watcher.py)

---

## 🚀 Comandos Essenciais da CLI (`amb jules`)

### 1. Criar uma Nova Sessão
Despacha uma tarefa para uma nova VM na nuvem:
```bash
amb jules create --prompt "Implementar validação de input no formulário de login" --title "Auth Input Validation"
```
Retorna o ID da sessão e a URL: `https://jules.google.com/session/<SESSION_ID>`.

### 2. Acompanhar em Tempo Real (Live Streaming)
Mostra o fluxo de pensamento, comandos bash e logs em tempo real:
```bash
amb jules get <SESSION_ID> --watch
```
*Para obter saída em JSON puro:*
```bash
amb jules get <SESSION_ID> --json
```

### 3. Listar Sessões Recentes
```bash
amb jules list --limit 10
```

### 4. Aprovar o Plano do Agente
Quando a sessão atinge o estado `AWAITING_PLAN_APPROVAL`:
```bash
amb jules approve -s <SESSION_ID>
```

### 5. Responder Dúvidas do Agente
Quando a sessão atinge `AWAITING_USER_FEEDBACK`:
```bash
# Resposta manual direta:
amb jules reply -s <SESSION_ID> -m "Utilize o schema existente em auth/schemas.py"

# Resposta automática assistida por Gemini (Auto-Advisor):
amb jules reply -s <SESSION_ID> --auto-approve
```

### 6. Fazer Merge Seguro do PR
Detecta o PR aberto pelo Jules, aprova no GitHub, valida o QA localmente e faz merge:
```bash
amb jules merge -s <SESSION_ID>

# Ou detectar automaticamente o PR mais recente:
amb jules merge --auto-latest
```

### 7. Limpar Sessões Antigas (Preservação de Cota)
Remove sessões `COMPLETED` ou `FAILED` para manter o workspace limpo:
```bash
amb jules clean --failed -f
```

---

## ⚙️ Regras de Implementação & Gotchas

1. **Estrutura de Resposta de Atividades:**
   - A API do Jules pode retornar `activities` tanto como uma lista direta `[ { ... } ]` quanto envelopada em dict `{ "activities": [...] }`.
   - **Padrão Obrigatório:**
     ```python
     acts = act_res if isinstance(act_res, list) else act_res.get("activities", [])
     ```

2. **Ordenação Cronológica de Atividades:**
   - A API retorna atividades em ordem decrescente (mais recentes primeiro).
   - Para síntese de contexto ou logs, inverta a lista com `reversed(acts)` para obter ordem cronológica correta.

3. **Subprocessos sem `shell=True`:**
   - Comandos Git em `merge_session_pr.py` devem usar `shell=False` passando listas de argumentos (`["git", "pull", "origin", branch]`) para evitar injeção de comandos via nomes de branch.
