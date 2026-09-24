---
name: amb-antigravity-specialist
description: >-
  Manage local personas, prompt engineering, RulesManager and cognitive execution via Antigravity SDK and agy CLI in AMB_V2. Use when creating or tuning personas in .amb/personas/, inspecting architectural rules with amb agy rules, synthesizing prompts, running agents locally with --agy/--local, or inspecting learning diaries.
---

# 🛸 AMB Antigravity Specialist

Especialista na gestão de personas, engenharia de prompts, gerenciamento de regras arquiteturais (`RulesManager`) e inferência cognitiva via **Antigravity SDK (`agy` CLI)** e API do Gemini no `amb_v2`.

## 📌 Visão Geral & Arquitetura

O ecossistema `amb_v2` integra o Google Antigravity para permitir que personas e ferramentas cognitivas operem tanto **localmente na sua máquina** quanto **na nuvem do Jules**:
- **Cliente Cognitivo Unificado:** [`amb_cli/integrations/antigravity/antigravity_client.py`](file:///c:/Users/DiogoHungaro/Desktop/Script/amb_v2/amb_cli/integrations/antigravity/antigravity_client.py)
- **Gerenciador de Regras Centralizado:** [`amb_cli/workspace/rules_manager.py`](file:///c:/Users/DiogoHungaro/Desktop/Script/amb_v2/amb_cli/workspace/rules_manager.py)
- **Executor Dinâmico de Personas:** [`amb_cli/agents/local_agent_runner.py`](file:///c:/Users/DiogoHungaro/Desktop/Script/amb_v2/amb_cli/agents/local_agent_runner.py)
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

## 🛠️ CLI Unificada do Antigravity (`amb agy`)

O AMB_V2 disponibiliza o comando mestre `amb antigravity` (alias `amb agy`) com subcomandos modulares:

```bash
# Diagnóstico de runtime (SDK, CLI agy, GEMINI_API_KEY, modelo ativo e regras):
amb agy status [--json]

# Listar e auditar regras arquiteturais ativas no repositório:
amb agy rules [--json] [--content]

# Sintetizar ideia informal em prompt executivo formal estruturado:
amb agy prompt -i "Implementar endpoint de pagamentos idempotente" -r backend [-o prompt.md]

# Auditar conformidade arquitetural e boas práticas de um arquivo:
amb agy validate path/to/file.py [--json]

# Executar inferência direta arbitrária com o modelo cognitivo:
amb agy run "Explique a diferença entre SRP e OCP" --model gemini-3.8-flash

# Ativar ou desativar confirmação interativa antes de chamadas ao Gemini:
amb config --gemini-confirm <on|off>
```

---

## 📐 Gerenciamento Central de Regras (`RulesManager`)

O [`RulesManager`](file:///c:/Users/DiogoHungaro/Desktop/Script/amb_v2/amb_cli/workspace/rules_manager.py) descobre automaticamente as regras arquiteturais do projeto seguindo a precedência:
1. Diretório explicitamente configurado via CLI ou parâmetro.
2. `.antigravity/rules/`
3. `.gemini/rules/`
4. `.agents/rules/` ou `rules/`
5. Arquivos raiz (`AGENTS.md`, `GEMINI.md`).

**Garantias:**
- **Zero Premissas a Priori:** Suporte poliglota transparente (Python, TypeScript, Go, Rust, etc.).
- **Markdown Íntegro:** Fechamento automático de fences (```` ``` ````) quando regras são truncadas.
- **Cache em Memória:** Performance otimizada com invalidação instantânea (`RulesManager.invalidate_cache()`).

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
- Regra 1: Manter compatibilidade com Python 3.10+ / stack do projeto
- Regra 2: Não alterar contratos de API existentes sem aviso
- Regra 3: Rodar os testes após implementar
```

---

## 🧠 Diários de Aprendizado (`.amb/diarios/`)

Quando uma persona é executada:
1. O `local_agent_runner.py` verifica se existe um diário em `.amb/diarios/<nome_da_persona>.md`.
2. Se existir, o histórico de aprendizados anteriores daquele repositório é **automaticamente concatenado** ao prompt enviado ao agente.
3. Isso evita que o agente cometa os mesmos erros em ciclos subsequentes.
