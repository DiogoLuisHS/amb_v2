---
name: amb-antigravity-specialist
description: >-
  Manage local personas, prompt engineering, and execution via Antigravity SDK and agy CLI in AMB_V2. Use when creating or tuning personas in .amb/personas/, running agents locally with --agy/--local, or inspecting learning diaries.
---

# 🛸 AMB Antigravity Specialist

Especialista na gestão de personas, engenharia de prompts e execução de agentes locais via **Antigravity SDK (`agy` CLI)** no `amb_v2`.

## 📌 Visão Geral & Arquitetura

O ecossistema `amb_v2` integra o Google Antigravity para permitir que personas especializadas executem manutenções tanto **localmente na sua máquina** quanto **na nuvem do Jules**.
- **Executor Dinâmico de Personas:** [`agents/local_agent_runner.py`](file:///c:/Users/DiogoHungaro/Desktop/Script/amb_v2/agents/local_agent_runner.py)
- **Diretório de Personas do Projeto Ativo:** `.amb/personas/` (ou `.jules/personas/`)
- **Diários Cognitivos de Aprendizado:** `.amb/diarios/<persona>.md`

---

## 🧭 Despacho Nuvem (Padrão) vs Execução Local (`--agy`)

Por padrão no `amb_v2`, qualquer persona é despachada para o **Google Jules** na nuvem:
- `amb agent --role <persona>` ➔ **Despacha para o Jules (Cloud)** ☁️
- `amb agent --all` ➔ **Despacha todas para o Jules (Cloud)** ☁️

Para forçar a execução **local** no terminal usando o motor do Antigravity (`agy` CLI):
- `amb agent --role <persona> --agy` (ou `--local`) ➔ **Executa Localmente** 💻
- `amb agent --all --agy` ➔ **Executa todas localmente** 💻

*Nota:* A execução local com `--agy` **não consome cota do Google Jules**.

---

## 📝 Como Criar uma Nova Persona

Toda persona é um arquivo Markdown (`.md`) colocado em `.amb/personas/` (ou na pasta definida por `--personas-dir`).

### Estrutura Padrão de uma Persona:
```markdown
# 🛡️ Nome da Persona: Especialidade

Breve resumo da missão da persona em uma ou duas frases.

## 🎯 Missão Principal
Descrever o objetivo claro que o agente deve atingir no repositório.

## 📂 Arquivos Alvos
1. `caminho/para/arquivo1.py`
2. `caminho/para/arquivo2.ts`

## 📋 Regras de Implementação
- Regra 1: Manter compatibilidade com Python 3.10+
- Regra 2: Não alterar contratos de API existentes sem aviso
- Regra 3: Rodar os testes após implementar
```

---

## 🧠 Diários de Aprendizado (`.amb/diarios/`)

Quando uma persona é executada:
1. O `local_agent_runner.py` verifica se existe um diário em `.amb/diarios/<nome_da_persona>.md`.
2. Se existir, o histórico de aprendizados anteriores daquele repositório é **automaticamente concatenado** ao prompt enviado ao agente.
3. Isso evita que o agente cometa os mesmos erros em ciclos subsequentes.

---

## 🚀 Comandos Úteis

```bash
# Listar todas as personas encontradas no projeto ativo:
amb agent --list

# Executar persona localmente com instrução adicional:
amb agent --role deadwood --task "Remover imports não utilizados em controllers/" --agy

# Executar todas as personas de um diretório customizado:
amb agent --personas-dir correcoes/ --all --agy
```
