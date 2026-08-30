# 🚀 Pipeline Autônomo Design-to-Code — AMB_V2

Pipeline unificado e modular para desenvolvimento autônomo de interfaces e funcionalidades de software, integrando **Google Stitch SDK**, **Antigravity Cognition Engine**, **Google Jules Cloud** e **Gatekeepers de QA com Validação Rigorosa**.

---

## 🏛️ Arquitetura do Fluxo

```mermaid
graph TD
    A["📄 Prompt da Tarefa (.amb/prompts/ ou template_tarefa.md)"] --> B["🎨 Google Stitch SDK (Geração/Refinamento Visual)"]
    B --> C["🚪 Gatekeeper 1: Decisão de Design (Aprovar / Refinar / Variantes)"]
    C -->|Aprovar| D["🧠 Antigravity Synthesizer (Injeção de DOM, Tokens e Regras do Projeto)"]
    C -->|Refinar| B
    D --> E["⚡ Google Jules Cloud (Desenvolvimento & Codificação Remota)"]
    E --> F["📡 Monitoramento de Atividades & Auto-Reply de Dúvidas"]
    F --> G["🛡️ Gatekeeper 2: QA Local (Typecheck + Build)"]
    G --> H["🧪 Validação de Tipos e Linter"]
    H --> I["🏗️ Build de Produção"]
    I --> J["✅ Código Validado & Pronto para Commit/PR"]
```

---

## 📖 Como Executar

### 🔹 1. Execução Padrão de uma Tarefa (Fluxo Completo)
```bash
# Via CLI unificada amb
amb pipeline amb_v2/pipeline/prompts/template_tarefa.md

# Ou apontando para qualquer especificação em .amb/prompts/
amb pipeline .amb/prompts/minha_tela.md
```

### 🔹 2. Utilizar Tela Já Existente no Stitch (`--screen-id`)
```bash
amb pipeline template_tarefa.md --screen-id <SCREEN_ID>
```

### 🔹 3. Retomar Monitoramento de Sessão Ativa do Jules (`--resume-session`)
```bash
amb pipeline template_tarefa.md --resume-session <SESSION_ID>
```

### 🔹 4. Pular a Etapa do Stitch (`--skip-stitch`)
```bash
amb pipeline template_tarefa.md --skip-stitch
```
