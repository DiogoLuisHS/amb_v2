# Google Jules Integration (AMB_V2)

Esta pasta contém o cliente REST e as ferramentas de integração com a API **Google Jules v1alpha**.

## Componentes

### `jules_client.py`
Cliente HTTP autenticado derivado de `BaseGoogleClient`, com resiliência, retry exponencial com jitter e normalização universal de URLs/IDs (`normalize_session_id`).
- Métodos principais: `create_session`, `get_session`, `list_sessions`, `list_sources`, `get_source`, `send_message`, `approve_plan`, `delete_session`, `list_activities`, `get_status`.

---

## Ferramentas Modulares (`tools/`)

| Ferramenta | Função de Serviço | Finalidade |
|---|---|---|
| `list_sources.py` | `run_list_sources(...)` | Lista fontes e repositórios GitHub conectados à conta Jules. |
| `list_sessions.py` | `run_list_sessions(...)` | Lista sessões com filtros estritos de repositório, estado e suporte a `--json`. |
| `get_session.py` | `run_get_session(...)` | Exibe metadados completos de uma sessão ou inicia streaming (`--watch`). |
| `create_session.py` | `run_create_session(...)` | Despacha nova sessão com suporte a `--branch`, `--source` e `--json`. |
| `approve_plan.py` | `run_approve_plan(...)` | Valida guardrail de plano pendente e aprova (suporta `--force`). |
| `send_message.py` | `run_send_message(...)` | Envia mensagem com guardrail contra mensagens consecutivas do usuário (suporta `--force`). |
| `monitor_activities.py`| `run_monitor_activities(...)` | Streaming em tempo real de logs, bash e planos da sessão. |
| `merge_session_pr.py` | `run_merge_session_pr(...)` | Detecta PR, marca como pronto (draft), aprova, faz squash merge e roda QA. |
| `cleanup_sessions.py` | `run_cleanup_sessions(...)` | Auditoria e exclusão segura de sessões na nuvem. |

---

## Guardrails de Segurança

1. **Aprovação de Plano (`approve_plan.py`):**
   Verifica se a sessão está em estado de espera de aprovação (`AWAITING_PLAN_APPROVAL`) ou se a atividade recente possui `planGenerated` do agente antes de disparar o endpoint. Bypass disponível com `--force`.

2. **Mensagens Duplicadas (`send_message.py`):**
   Verifica se a última atividade foi enviada pelo usuário, evitando duplicidades enquanto a VM do Jules processa. Bypass disponível com `--force`.

3. **Exclusão Segura (`cleanup_sessions.py`):**
   Apenas permite a exclusão de sessões em estados terminais (`COMPLETED`, `SUCCEEDED`, `FAILED`, `CANCELLED`). Sessões ativas são preservadas automaticamente.
