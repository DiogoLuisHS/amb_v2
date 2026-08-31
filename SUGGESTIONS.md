# 📊 AMB_V2 — Sugestões de Melhoria Pendentes (Método MoSCoW)

> Atualizado em: 2026-08-30 | Versão: 2.0.0
>
> Este documento lista apenas os itens **ainda não implementados**, organizados pelo método MoSCoW.
> Para bugs corrigidos e features já implementadas, consulte [CHANGELOG_FIXES.md](./CHANGELOG_FIXES.md).

---

## 🐛 Bugs Pendentes

### Bug #5 — `find_repo_root()` pode falhar em monorepos aninhados
**Arquivo:** `config/config.py`
**Causa:** A busca sobe até 6 níveis procurando marcadores de repositório (`.git`, `.env`, `package.json`). Em monorepos com subpacotes (cada um com seu `package.json`), a busca pode parar no subpacote em vez da raiz real.
**Impacto:** `GITHUB_REPOSITORY` lido incorretamente → sessão Jules criada no repositório errado.
**Proposta de fix:** Dar prioridade máxima à presença de `.git` (único marcador de raiz de repositório real) e usar `.env` apenas como fallback secundário.

---

## 🔴 MUST HAVE — Essenciais para estabilidade em produção

### M1 — Retry com Backoff Exponencial nas Chamadas à API Jules
**Arquivo:** `integrations/jules/jules_client.py`
**Problema:** Qualquer falha transitória de rede (429 rate limit, 503, timeouts) derruba o loop permanentemente na primeira tentativa. Não há mecanismo de recuperação.
**Proposta:**
```python
def _request_with_retry(self, method, path, params=None, data=None, max_retries=3):
    for attempt in range(max_retries):
        try:
            return self._request(method, path, params, data)
        except ApiExecutionError:
            if attempt == max_retries - 1:
                raise
            wait = (2 ** attempt) + random.uniform(0, 1)
            log("JULES", f"Tentativa {attempt+1}/{max_retries}. Aguardando {wait:.1f}s...", Colors.YELLOW)
            time.sleep(wait)
```
**Impacto esperado:** Elimina crashes desnecessários do loop por falhas transitórias de rede.

---

### M2 — Persistência de Estado do Loop (Retomada Automática após Crash)
**Arquivo:** `agents/autonomous_loop.py`
**Problema:** Se o terminal fechar durante um ciclo ativo, o loop recomeça do zero ao ser reiniciado. PRs podem ser duplicados e o trabalho do Jules em andamento fica órfão.
**Proposta:** Salvar estado em `.amb/loop_state.json` e retomar sessão ativa ao reiniciar:
```json
{
  "cycle": 2,
  "active_session_id": "538227422414712240",
  "persona": "relay",
  "started_at": "2026-08-30T18:53:37Z"
}
```
**Impacto esperado:** Resiliência total a crashes e reinícios do terminal.

---

### M4 — Timeout Global Configurável para Sessões Jules
**Arquivo:** `agents/autonomous_loop.py`
**Problema:** `monitor_and_assist_session` faz polling eternamente. Se Jules travar em estado desconhecido (nem COMPLETED nem FAILED), o loop fica bloqueado para sempre.
**Proposta:** Flag `--session-timeout <minutos>` (padrão: 60). Após o timeout, encerra o monitoramento, loga o incidente e avança para o próximo ciclo.
```bash
amb agent --all --loop --session-timeout 45
```

---

## 🟡 SHOULD HAVE — Importantes para maturidade do produto

### S1 — Notificações Desktop/Webhook (Slack, Discord, Email)
**Arquivo:** `dashboard/watchers/alert_notifier.py`
**Problema:** Alertas são apenas impressos no terminal. Se o usuário não está monitorando o terminal, não sabe que o Jules está bloqueado ou que um PR está esperando merge.
**Proposta:** Integrar via `.env`:
```bash
SLACK_WEBHOOK_URL=https://hooks.slack.com/...
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/...
```
Notificações no estilo: _"[Jules] Sessão 538... aguardando sua resposta: 'Como devo tratar os erros de tipo?'"_

---

### S2 — Diário de Operações do Loop (Log Persistente em `.amb/logs/`)
**Arquivo:** `agents/autonomous_loop.py`
**Problema:** Toda a história de execução vai para o terminal e se perde. Não há como auditar o que o Jules fez nos últimos N ciclos ou quanto tempo cada sessão levou.
**Proposta:** Salvar cada ciclo em `.amb/logs/loop-YYYY-MM-DD.jsonl`:
```json
{"cycle": 1, "persona": "relay", "session_id": "538...", "state": "COMPLETED", "pr": 164, "merged": true, "duration_min": 23, "timestamp": "2026-08-30T18:53:37Z"}
```

---

### S3 — `amb jules list` com filtros e exibição de PR
**Arquivo:** `cli.py`
**Problema:** `amb jules list` não mostra se a sessão tem PR criado, qual é o número, nem permite filtrar por status.
**Proposta:**
```bash
amb jules list --state COMPLETED    # Filtra por estado
amb jules list --with-pr            # Apenas sessões com PR criado
amb jules list --format table       # Output em tabela (sessão, PR#, estado, duração)
```

---

### S4 — Agendamento de Ciclos (Cron Expression para o Loop)
**Arquivo:** `agents/autonomous_loop.py`
**Problema:** O loop roda continuamente ou com delay fixo entre ciclos. Não há como programar "rodar apenas das 22h às 6h" para economizar quota da API Jules durante o dia.
**Proposta:**
```bash
amb agent --all --loop --schedule "0 22 * * *"        # Todo dia às 22h
amb agent --all --loop --schedule "*/30 * * * *" --max-cycles 10  # A cada 30min
```

---

### S5 — Dashboard Web com WebSocket em Tempo Real
**Arquivo:** `dashboard/dashboard_server.py`
**Problema:** Se o dashboard usa polling HTTP do frontend, há atraso de 5-15s para exibir mudanças de estado do loop. Para automação em tempo real, é muito lento.
**Proposta:** Substituir polling por push de eventos via WebSocket (`websockets` ou `aiohttp`) direto do loop autônomo para o navegador.

---

### S6 — `amb setup` com Geração Automática de Personas Padrão
**Arquivo:** `config/setup_project.py`
**Problema:** Após `amb setup`, o usuário precisa criar manualmente os arquivos de personas em `.amb/personas/`. Projetos novos ficam sem personas funcional até configuração manual.
**Proposta:** Ao final do setup, detectar a stack do projeto e gerar personas pré-configuradas:
- `relay.md` — Desenvolvimento e manutenção geral
- `sentry.md` — Auditoria de tipos, arquitetura e segurança
- `pixel.md` — UI/UX, Design System e consistência visual

---

## 🟢 COULD HAVE — Desejável para versão futura

### C1 — Multi-Repositório em Paralelo
**Problema:** Um único `amb agent --loop` só trabalha em um projeto por vez. Para usuários com múltiplos projetos ativos, é necessário abrir múltiplos terminais com contextos separados.
**Proposta:**
```bash
amb agent --all --loop --repos nexushub_v2,frontend_app,api_service
```
Cada projeto rodaria em uma `Thread` separada, com log unificado e dashboard consolidado.

---

### C2 — Cache SQLite do Histórico Jules
**Problema:** O histórico de cada sessão Jules é sempre buscado ao vivo da API. Em sessões longas (100+ activities), isso gera delays de 2-5s a cada polling e aumenta consumo de quota da API.
**Proposta:** Cache local em `.amb/cache/jules.db` com TTL configurável (padrão: 5min por sessão).

---

### C3 — Stitch Integrado no Loop (Design → Código → PR)
**Problema:** O loop autônomo cobre o ciclo Jules (backend/código), mas não integra o Stitch (design). Uma persona `pixel` completa deveria usar o Stitch para gerar telas e pedir ao Jules para implementá-las.
**Proposta:** Persona `pixel` no loop usa Stitch SDK para gerar HTML → envia para Jules com instrução de implementar → auto-merge.

---

### C4 — Validação de Segurança do Prompt antes do Despacho ao Jules
**Problema:** Qualquer string em um arquivo `.md` de persona é enviada diretamente ao Jules sem sanitização. Um arquivo malicioso poderia injetar instruções destrutivas.
**Proposta:** Antes de despachar, validar o prompt contra lista de padrões bloqueados (`rm -rf`, `DROP TABLE`, chaves de API, etc.) e bloquear com alerta ao usuário.

---

## 🔵 WON'T HAVE (nesta versão)

| Item | Justificativa |
|:-----|:-------------|
| **W1** — GUI/Web para edição de personas | CLI-first. Plugins de editor (VS Code Extension) são mais adequados para edição de Markdown. |
| **W2** — Integração com GitLab / Bitbucket | A integração usa `gh` (GitHub CLI) profundamente. Suporte a outros VCS exigiria abstração completa. |
| **W3** — Self-Hosted Jules (API On-Premise) | Jules é um serviço Google Cloud gerenciado. Deployments próprios estão fora do escopo do `amb_v2`. |

---

## 📅 Roadmap de Implementação

### Sprint 1 — Alta prioridade (1 semana)
- [ ] **M1** — Retry com backoff exponencial na API Jules
- [ ] **M4** — Timeout global de sessão Jules (`--session-timeout`)
- [ ] **S2** — Diário de operações em JSONL (`.amb/logs/`)
- [ ] **S3** — `amb jules list` com filtros e coluna de PR

### Sprint 2 — Estabilidade (2-4 semanas)
- [ ] **M2** — Persistência de estado do loop (retomada após crash)
- [ ] **Bug #5** — `find_repo_root` em monorepos aninhados
- [ ] **S1** — Notificações Slack/Discord

### Sprint 3 — Funcionalidades (1-2 meses)
- [ ] **S4** — Agendamento cron do loop
- [ ] **S6** — `amb setup` gera personas padrão por stack
- [ ] **C4** — Validação de segurança do prompt

### Versão Futura
- [ ] **S5** — WebSocket no Dashboard em tempo real
- [ ] **C1** — Multi-repositório em paralelo
- [ ] **C2** — Cache SQLite do histórico Jules
- [ ] **C3** — Stitch integrado no loop (Design → Código → PR)
