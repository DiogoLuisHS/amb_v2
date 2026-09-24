# 📚 Catálogo de Prompts Atômicos: Expansão do Ecossistema Google AI

Este diretório contém os prompts modulares específicos para orientar o **Google Jules** na implementação em lote das novas integrações do ecossistema Google AI no **AMB_V2**.

Cada prompt é 100% focado em um único domínio, garantindo economia de tokens, precisão cirúrgica de contexto e respeito rigoroso às regras arquiteturais (SRP, atomização <= 300 linhas, DRY e tipagem estrita).

---

## 📑 Sequência de Prompts do Ciclo

| # | Arquivo Prompt | Módulo Alvo | Responsabilidade Principal |
|---|---|---|---|
| **01** | [`01_integrate_google_genai_sdk.md`](./01_integrate_google_genai_sdk.md) | `amb_cli/integrations/antigravity/` | Migra o backend Gemini para o SDK unificado `google-genai`, suportando Thinking models e Context Caching. |
| **02** | [`02_developer_knowledge_mcp_grounding.md`](./02_developer_knowledge_mcp_grounding.md) | `amb_cli/architecture/` | Grounding semântico com a documentação oficial do Google Developer Knowledge MCP em `amb context`. |
| **03** | [`03_vertex_model_armor_guardrail.md`](./03_vertex_model_armor_guardrail.md) | `amb_cli/agents/auto_reply_core/` | Guardrail de segurança com Vertex AI Model Armor para sanitizar prompt injection e mascarar PII/senhas em logs. |
| **04** | [`04_stitch_native_mcp_server.md`](./04_stitch_native_mcp_server.md) | `amb_cli/integrations/stitch/` | Expõe as ferramentas de design generativo do Stitch como um servidor MCP nativo (`amb stitch mcp`). |
| **05** | [`05_mcp_toolbox_database_introspection.md`](./05_mcp_toolbox_database_introspection.md) | `amb_cli/architecture/` | Introspecção dinâmica de banco de dados em tempo de execução via `amb schema --live` (estilo MCP Toolbox). |

---

## 🚀 Como Executar com o AMB Agent em Lote

### 1. Execução Sequencial em Lote
Para executar todos os prompts em sequência na branch ativa com o Google Jules:
```bash
amb agent -p .amb/prompts/
```

### 2. Direcionar para uma Feature Branch
```bash
amb agent -p .amb/prompts/ --branch feature/google-ai-ecosystem
```

### 3. O que o AMB fará automaticamente em cada prompt:
1. Cria a Cloud VM dedicada no Google Jules para a tarefa.
2. Anexa automaticamente o mapa de arquivos via `ai_context_builder` para acelerar a VM.
3. Monitora logs ao vivo e responde dúvidas do agente através do Auto-Advisor Gemini.
4. Ao abrir o PR (sempre em Draft pelo Jules), executa `gh pr ready`, roda os testes locais do projeto (`pytest`), aprova e faz auto-merge no GitHub.
5. Faz `git pull` local e passa de forma limpa para o próximo prompt até concluir os 5 desenvolvimentos!
