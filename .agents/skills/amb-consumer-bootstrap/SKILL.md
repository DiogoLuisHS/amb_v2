---
name: amb-consumer-bootstrap
description: >-
  Bootstrap, configure, and operate AMB_V2 inside any external consumer repository. Use when running amb setup, creating .amb/ project configurations, declaring stack QA commands, configuring .env via amb gui, or executing AMB tools from any project folder.
---

# 🔌 AMB Consumer Bootstrap

Guia completo para plugar, configurar e operar a CLI global **`amb`** em **qualquer repositório consumidor externo** (Node.js, React, Next.js, Python, Go, Rust ou Monorepos).

---

## 📌 1. Como Funciona o Bootstrap

O AMB opera de forma agnóstica a linguagens e frameworks:
- **Instalação Global Única:** Você instala o AMB uma única vez no seu ambiente (`pip install -e /caminho/para/amb_v2`).
- **Comando Universal `amb`:** Fica disponível em qualquer terminal aberto no seu computador.
- **Isolamento de Configuração (`.amb/`):** Cada projeto consumidor guarda suas próprias personas, comandos de QA e diários de aprendizado em uma pasta local `.amb/`.
- **Credenciais Locais (`.env`):** O projeto consumidor lê as chaves de API necessárias diretamente do seu próprio arquivo `.env`.

---

## 🚀 2. Passo a Passo: Configurando um Novo Projeto

### Passo 1: Abrir o Terminal no Repositório Alvo
Navegue até a pasta do projeto que você quer gerenciar com o AMB:
```bash
cd /caminho/para/meu-projeto
```

### Passo 2: Executar o Assistente de Setup
Execute o comando de inicialização:
```bash
amb setup
```
*Ou execute em modo totalmente automático (não-interativo):*
```bash
amb setup --auto
```

O assistente executará as seguintes tarefas:
1. Detectará a stack técnica (Node.js, Python, Go, etc.) e o gerenciador de pacotes (`npm`, `pnpm`, `yarn`, `pip`, etc.).
2. Inferirá automaticamente os comandos de QA do seu projeto (`typecheck`, `test`, `build`, `lint`).
3. Criará a pasta `.amb/` contendo:
   - `.amb/amb_project.json`: Configurações centrais do projeto.
   - `.amb/personas/`: Pasta para personas de engenharia do projeto.
   - `.amb/prompts/`: Pasta para desenvolvimento em lote via prompts.
   - `.amb/diarios/`: Diários de aprendizado cognitivo dos agentes.

---

## ⚙️ 3. Configurando o `.amb/amb_project.json`

O arquivo `.amb/amb_project.json` é o coração da governança do seu projeto. É dele que os comandos `amb jules merge` e `amb agent --loop` leem os testes que devem passar antes de autorizar o merge no Git.

### Exemplo para Monorepo TypeScript / React / Node:
```json
{
  "$schema": "https://amb-v2.dev/schemas/amb_project.v2.json",
  "version": "2.0.0",
  "name": "meu-monorepo",
  "repository": "minha-org/meu-monorepo",
  "default_branch": "main",
  "stack": {
    "type": "node",
    "primary_language": "typescript",
    "package_manager": "npm",
    "is_monorepo": true,
    "rules_dir": ".agents/rules"
  },
  "qa": {
    "typecheck": "npm run typecheck",
    "lint": "npm run lint",
    "test": "npm test",
    "build": "npm run build"
  },
  "personas": {
    "active": ["engineer"]
  }
}
```

### Exemplo para Projeto Python:
```json
{
  "name": "meu-backend",
  "stack": {
    "type": "python",
    "primary_language": "python",
    "package_manager": "pip"
  },
  "qa": {
    "test": "pytest",
    "typecheck": "python -m py_compile main.py"
  }
}
```

---

## 🔑 4. Configurando Credenciais (`.env` e `amb gui`)

Para que as IAs operem no seu projeto consumidor, configure as seguintes variáveis no arquivo `.env` na raiz do seu projeto:

```env
# Chaves da Plataforma Google
JULES_API_KEY=AQ.A...
GEMINI_API_KEY=AQ.A...
STITCH_API_KEY=AQ.A...

# Repositório GitHub Vinculado
GITHUB_REPOSITORY=minha-org/meu-projeto

# Opcional: ID do projeto no Stitch para geração de UI
STITCH_PROJECT_ID=1742...
```

> **💡 Dica Pro — Assistente Gráfico Nativo:**  
> Você não precisa editar o `.env` manualmente! Basta rodar `amb gui` (ou `amb ui`) no terminal do projeto. A interface gráfica nativa abrirá com uma aba dedicada para preencher e validar suas chaves com segurança.

---

## 🩺 5. Validando a Saúde do Ambiente (`amb check`)

Após o setup e configuração das chaves, execute:
```bash
amb check
```

O comando emitirá um diagnóstico completo confirmando:
- ✅ Credenciais das APIs Google (Jules, Gemini, Stitch).
- ✅ Associação com o repositório GitHub.
- ✅ Autenticação da GitHub CLI (`gh`).
- ✅ Proteção do `.env` no `.gitignore`.
- ✅ Binários de QA configurados e funcionais.

---

## 🛡️ 6. Boas Práticas de Versionamento Git no Consumidor

Adicione ao `.gitignore` do seu repositório:
```gitignore
# Credenciais sensíveis
.env

# Logs e diários cognitivos temporários
.amb/diarios/
```

**Mantenha no Git:**
- `.amb/amb_project.json` (para que toda a equipe use os mesmos comandos de QA).
- `.amb/personas/` (para compartilhar personas e regras com outros desenvolvedores e agentes).
- `.amb/prompts/` (para histórico de especificações e features).
