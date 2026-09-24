---
name: amb-antigravity-specialist
description: >-
  Manage local personas, prompt engineering, rules inspection, and local cognitive agent execution via Antigravity SDK and agy CLI inside any consumer project. Use when creating or tuning personas in .amb/personas/, running agents locally with --agy/--local, auditing architectural rules with amb validate, or synthesizing prompts.
---

# 🛸 AMB Antigravity Specialist

Guia para criar e gerenciar **personas locais**, executar **agentes no seu terminal** sem gastar cota na nuvem (via Antigravity SDK / `agy` CLI) e auditar regras arquiteturais em qualquer projeto consumidor.

---

## 📌 1. Visão Geral: Nuvem (Jules) vs Local (`--agy`)

Por padrão, comandos de agente no AMB despacham tarefas para a nuvem do Google Jules:
- `amb agent --role engineer` ➔ **Nuvem (Jules Cloud VM)** ☁️

Quando você deseja que o agente trabalhe **diretamente nos arquivos locais da sua máquina**, com feedback instantâneo e **sem consumir cota do Google Jules**, utilize a flag `--agy` (ou `--local`):
- `amb agent --role engineer --agy` ➔ **Execução Local (Antigravity)** 💻
- `amb agent --all --agy` ➔ **Executa todas as personas localmente** 💻

*Requisito para execução local:* Chave `GEMINI_API_KEY` configurada no `.env` e a CLI `agy` instalada no PATH.

---

## 📝 2. Como Criar e Ajustar Personas no Projeto Consumidor

Todas as personas do seu projeto residem na pasta local `.amb/personas/` como arquivos Markdown (`.md`).

### Estrutura Padrão de uma Persona (`.amb/personas/frontend.md`):
```markdown
# 🎨 Frontend Engineer: Especialista em Interface e Design System

Persona responsável por componentes visuais, acessibilidade e integração com APIs.

## 🎯 Missão Principal
Construir e refatorar componentes de interface garantindo fidelidade ao Design System, responsividade e 100% de aprovação no typecheck do projeto.

## 📂 Arquivos de Foco
- `apps/web/src/components/`
- `apps/web/src/pages/`
- `apps/web/src/styles/`

## 📋 Regras de Implementação
1. Utilizar classes utilitárias do Tailwind já configuradas no repositório.
2. Não adicionar dependências externas sem aprovação prévia.
3. Garantir labels de acessibilidade (`aria-label`, contraste) em todos os botões e inputs.
4. Executar `npm run lint --prefix apps/web` antes de concluir.
```

### Comandos de Persona:
```bash
# Listar todas as personas do projeto:
amb agent --list

# Executar a persona localmente com uma instrução adicional:
amb agent --role frontend --agy -t "Refatorar modal de login para suportar OAuth"
```

---

## 📐 3. Governança e Auditoria de Regras Arquiteturais

O AMB permite definir regras de engenharia em `.agents/rules/` no seu repositório consumidor e auditar seus arquivos contra essas regras:

```bash
# Listar todas as regras ativas do seu projeto:
amb agy rules

# Exibir o conteúdo completo consolidado das regras:
amb agy rules --content

# Auditar conformidade arquitetural de um arquivo específico:
amb validate apps/web/src/components/Modal.tsx

# Diagnóstico de saúde do runtime Antigravity no projeto:
amb agy status
```

---

## 💡 4. Síntese de Prompts com Gemini (`amb prompt -s`)

Transforme ideias informais ou requisitos soltos em prompts arquiteturais estruturados, prontos para enviar a qualquer IA ou persona:

```bash
# Sintetizar prompt arquitetural a partir de uma ideia informal:
amb prompt -s "Criar sistema de notificações toast com auto-dismiss e som suave" --role frontend -o prompt.md

# Sintetizar prompt via comando agy dedicado:
amb agy prompt -i "Implementar endpoint de checkout idempotente com stripe" -r backend -o specs/checkout.md
```

O Gemini analisa a ideia, lê as regras arquiteturais ativas do seu repositório e gera um prompt profissional contendo escopo, arquivos alvos, invariantes de segurança e testes sugeridos.

---

## ⚡ 5. Inferência Cognitiva Direta (`amb agy run`)

Execute consultas técnicas ou tire dúvidas arquiteturais com o modelo Gemini diretamente no seu terminal:

```bash
amb agy run "Qual a melhor estratégia de cache para este monorepo?" -m gemini-2.5-flash
```

### Configurar Confirmação Interativa do Gemini:
```bash
# Desabilitar confirmação interativa para chamadas ao Gemini (100% autônomo):
amb config --gemini-confirm off

# Reativar pedido de confirmação antes de chamadas:
amb config --gemini-confirm on
```
