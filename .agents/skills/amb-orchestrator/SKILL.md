---
name: amb-orchestrator
description: >-
  Master cognitive orchestrator and unified command hub for developing, testing, deploying, and automating tasks in any project using AMB_V2 CLI. Orchestrates Antigravity agents, autonomous loops, Google Jules cloud VMs, Stitch UI generation, design-to-code pipeline, repository layering, and local QA quality gates.
---

# 🛸 AMB Orchestrator — Master Cognitive Hub & CLI Engine

O **AMB Orchestrator** é o ponto de entrada unificado para orquestrar engenharia de software autônoma, geração de telas por IA, agentes locais e na nuvem, e validação contínua em **qualquer repositório consumidor**.

---

## 🧭 1. Roteamento de Capacidades & Subskills Especializadas

Cada domínio operacional do ecossistema possui um guia especializado dedicado na pasta [`subskills/`](./subskills/):

| Subskill | Arquivo de Referência | Domínio & Quando Utilizar |
| :--- | :--- | :--- |
| **Master Ecosystem** | [`subskills/master-ecosystem.md`](./subskills/master-ecosystem.md) | **Cheatsheet Definitivo:** Catálogo completo de comandos (`amb`), flags globais, troubleshooting e fluxos de alta produtividade. |
| **Autonomous Pipeline** | [`subskills/autonomous-pipeline.md`](./subskills/autonomous-pipeline.md) | **Ciclos Contínuos e Lotes:** Executar loops (`amb agent --loop`), processar pastas de prompts (`amb agent -p`), gerenciar estados (`amb loop status/pause/resume`) e sandbox de QA. |
| **Jules Cloud Specialist** | [`subskills/jules-specialist.md`](./subskills/jules-specialist.md) | **Cloud Coding (VMs):** Criar tarefas no Google Jules (`amb jules create`), streaming de logs ao vivo (`-w`), auto-reply com Gemini e auto-merge de PRs (`amb jules merge`). |
| **Stitch Specialist** | [`subskills/stitch-specialist.md`](./subskills/stitch-specialist.md) | **Design Generativo & UI:** Criar e refinar telas com Google Stitch (`amb stitch generate/refine`), variantes, download de assets e sincronização com `design.md`. |
| **Design-to-Code** | [`subskills/design-to-code.md`](./subskills/design-to-code.md) | **Ponte Visual ➔ Código:** Pipeline SRP ponta a ponta (`amb pipeline -s <stitch.md> -j <jules.md>`), convertendo mockups em componentes React/Tailwind com PR. |
| **Context Architecture** | [`subskills/context-architecture.md`](./subskills/context-architecture.md) | **Mapeamento de Monorepo:** Gerar mapa de 6 camadas para IAs (`amb context [modulo]`) e inspecionar schemas de banco de dados (`amb schema [filtro]`). |
| **Antigravity Specialist** | [`subskills/antigravity-specialist.md`](./subskills/antigravity-specialist.md) | **Cognição Local & Regras:** Personas em `.amb/personas/`, validação (`amb persona validate`), síntese de prompts (`amb prompt -s`) e governança (`amb validate --staged`, `amb hooks install`). |
| **Consumer Bootstrap** | [`subskills/consumer-bootstrap.md`](./subskills/consumer-bootstrap.md) | **Setup & Governança Externa:** Plugar o AMB em qualquer projeto (`amb setup`), configurar `.env` (`amb gui`), definir comandos de QA em `amb_project.json` e telemetria (`amb stats`). |

---

## ⚡ 2. Matriz de Comandos da CLI Global (`amb`)

### ⚙️ Configuração, Diagnóstico & Governança
```bash
amb check [--json]           # Diagnóstico de saúde: APIs Google, Git, GitHub CLI e QA
amb setup [--auto] [-f]      # Detectar stack do projeto e provisionar pasta .amb/
amb prompt [-s "<ideia>"]    # Imprimir prompt mestre ou sintetizar ideia com Gemini
amb config reload            # Limpar cache do ConfigManager e recarregar .env e configs
amb stats [--json]           # Telemetria local: taxa de QA, tempo médio de ciclo e PRs
amb validate --staged        # Auditar conformidade arquitetural apenas nos arquivos no stage
amb hooks install            # Instalar hook pre-commit automático (.git/hooks/pre-commit)
amb gui                      # Abrir interface gráfica nativa (Runner + editor de .env)
```

### 🤖 Loop Autônomo & Personas (`amb agent`, `amb loop`)
```bash
amb agent -p <pasta>         # Execução sequencial em lote de prompts numerados
amb agent -p <pasta> --loop  # Rotação infinita contínua sobre a pasta de prompts
amb agent --role <persona>   # Despachar persona para o Google Jules na nuvem
amb agent --role <p> --agy   # Executar persona localmente via Antigravity SDK
amb agent --all --loop       # Loop contínuo iterando sobre todas as personas
amb persona validate         # Auditar estrutura obrigatória das personas locais
amb loop status              # Inspecionar estado persistido em .amb/loop_state.json
amb loop pause               # Pausar graciosamente o ciclo autônomo
amb loop resume              # Retomar o ciclo do ponto exato onde foi pausado
```

### ☁️ Google Jules Cloud (`amb jules`)
```bash
amb jules list [--limit N]   # Listar sessões recentes com filtros de estado
amb jules get <id> --watch   # Live streaming de comandos bash e atividades da VM
amb jules create -p "<p>"    # Criar nova sessão na nuvem em branch dedicada
amb jules reply <id> [-y]    # Responder dúvidas (manual ou auto-reply com Gemini)
amb jules merge <id>         # Publicar Draft PR, validar QA local e fazer auto-merge
amb jules clean [--failed]   # Limpar sessões finalizadas para economizar cotas
```

### 🎨 Google Stitch SDK & Pipeline Design-to-Deploy
```bash
amb stitch generate -p "..." # Gerar tela visual interativa (Mobile, Desktop, Agnostic)
amb stitch refine -s <id>    # Refinar componentes ou cores de uma tela existente
amb stitch variants -s <id>  # Gerar de 1 a 5 variantes visuais exploratórias
amb pipeline -s <d> -j <e>   # Pipeline Design-to-Deploy com prompts separados (SRP)
amb pipeline -j <e> --no-qa  # Tarefa pura de engenharia sem interface gráfica
```

### 🧠 Arquitetura, Schemas & Git
```bash
amb context [modulo]         # Mapear 6 camadas (DB ➔ Services ➔ API ➔ UI) para IA
amb schema [filtro]          # Inspecionar tabelas e colunas de banco de dados
amb git status [--json]      # Status completo de branches, upstream e GitHub CLI
amb git sync [-b <branch>]   # Sincronização segura com auto-stash transparente
```

---

## 🎯 3. Princípios Operacionais do Orquestrador

1. **Auto-Containment & Zero Redundancy (DRY):** Todo módulo do core é atômico (<= 250 linhas) e opera sob o Single Responsibility Principle (SRP).
2. **Resiliência por Design:** Falhas de rede, interrupções de terminal ou reinicializações são absorvidas transparentemente pela `LoopStateMachine` via `.amb/loop_state.json`.
3. **Qualidade Inegociável:** Nenhum código gerado por IA é integrado à branch principal sem passar com 100% de sucesso nos testes locais (`QualityGatekeeper`).
4. **Privacidade e Performance Local:** Configurações e telemetrias operam 100% em arquivos locais (`.amb/telemetry.jsonl`, `ConfigManager`), sem envio desnecessário de dados para a nuvem.
