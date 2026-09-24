---
name: amb-jules-specialist
description: >-
  Operate, automate, and troubleshoot Google Jules cloud coding agent sessions for any consumer repository. Use when creating cloud tasks, streaming live activities and bash commands, approving plans, answering doubts via Gemini Advisor, and safely merging PRs.
---

# ☁️ AMB Jules Specialist

Guia para operar o **Google Jules** na nuvem a partir de qualquer repositório consumidor usando o comando `amb jules`.

---

## 📌 1. O que é o Google Jules no AMB?

O Google Jules é um agente de desenvolvimento em nuvem que executa em uma máquina virtual (Cloud VM) isolada. Ele clona o repositório vinculado no `.env` (`GITHUB_REPOSITORY`), cria uma branch própria (`jules/session-...`), implementa as mudanças de código e abre um Pull Request no GitHub.

No AMB, a integração é 100% automatizada:
- Suporta **Streaming ao Vivo** de pensamentos, comandos bash e logs.
- Suporta **Auto-Advisor com Gemini** para responder dúvidas do agente sem travar a sessão.
- Trata **Draft PRs** automaticamente via `gh pr ready`.
- Executa **QA Local** na sua máquina antes de aprovar o merge no Git.

---

## 🚀 2. Comandos Operacionais da CLI (`amb jules`)

### 1. Criar uma Nova Tarefa na Nuvem
Despacha uma tarefa para uma nova Cloud VM:
```bash
amb jules create -p "Implementar validação Zod no schema de usuários" -t "User Schema Validation" --branch main
```

> **Normalização Universal de IDs:** Todos os comandos abaixo aceitam o ID numérico puro (`175...`), caminho REST (`sessions/175...`) ou a URL completa do navegador (`https://jules.google.com/session/175...`).

### 2. Acompanhar em Tempo Real (Live Streaming)
Acompanhe os logs, comandos bash executados e pensamentos do agente em tempo real no seu terminal:
```bash
amb jules get <ID_OU_URL> --watch
```
*Para obter apenas os dados brutos em JSON:*
```bash
amb jules get <ID_OU_URL> --json
```

### 3. Listar Sessões do Repositório
```bash
# Listar as 10 sessões mais recentes do seu projeto:
amb jules list --limit 10

# Filtrar sessões aguardando resposta:
amb jules list --state AWAITING_USER_FEEDBACK

# Listar sessões de todos os repositórios conectados à sua conta:
amb jules list --all
```

### 4. Responder Dúvidas do Agente (`reply`)
Quando a sessão entra no estado `AWAITING_USER_FEEDBACK`:

```bash
# Opção A: Resposta manual direta via CLI:
amb jules reply <ID> -m "Utilize a biblioteca Lucide React já instalada para os ícones."

# Opção B: Resposta automática inteligente com Gemini (Auto-Advisor):
amb jules reply <ID> -y

# Opção C: Abrir menu cognitivo interativo para revisar todas as dúvidas:
amb jules reply
```

### 5. Aprovar o Plano de Execução (`approve`)
Quando o agente formula o plano de ação e aguarda autorização (`AWAITING_PLAN_APPROVAL`):
```bash
amb jules approve <ID> [--force]
```

### 6. Fazer Merge Seguro do Pull Request (`merge`)
Detecta o PR aberto pelo Jules, converte de Draft para Ready (`gh pr ready`), executa a suíte de testes locais do projeto (`amb_project.json`), aprova no GitHub e faz squash merge:
```bash
# Mesclar PR de uma sessão específica:
amb jules merge <ID> [--branch main]

# Detectar e mesclar automaticamente o PR mais recente aberto:
amb jules merge --auto-latest
```

### 7. Limpar Sessões Encerradas para Economizar Cota (`clean`)
Remove sessões da nuvem que já foram integradas ou que falharam:
```bash
# Limpar sessões com PRs já mesclados no Git:
amb jules clean --merged -f

# Limpar sessões com erro fatal (FAILED):
amb jules clean --failed -f
```

---

## 🛠️ 3. O Sentinela Contínuo (`amb monitor` e `amb advisor`)

Para monitorar e responder sessões em lote em segundo plano no projeto:

```bash
# Sentinela contínuo em tempo real (vigia a cada 15 segundos):
amb monitor

# Sentinela no Piloto Automático (vigia e auto-responde com Gemini sem parar):
amb monitor -y

# Checagem instantânea de 1 rodada:
amb monitor -1

# Menu cognitivo para revisar dúvidas pendentes:
amb advisor
```

---

## ⚠️ 4. Gotchas Críticos do Jules

1. **Jules Sempre Abre PRs como Draft:**
   - O Jules cria os PRs no GitHub no modo Draft. O comando `amb jules merge` executa automaticamente `gh pr ready` antes do merge, eliminando a necessidade de abrir a página web do GitHub.
2. **Ambiente Isolado da Cloud VM:**
   - A VM do Jules não tem acesso ao seu `.env` local. Passe chaves ou configurações de ambiente necessárias explicitamente no prompt ou instrua o agente a ler de `.env.example`.
3. **Erros de Build na VM:**
   - Se o Jules falhar por falta de um binário ou versão de runtime, o Auto-Advisor (`amb jules reply -y`) sugere os comandos alternativos automaticamente para desbloquear a VM.
