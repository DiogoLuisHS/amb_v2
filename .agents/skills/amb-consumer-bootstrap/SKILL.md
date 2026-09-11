---
name: amb-consumer-bootstrap
description: >-
  Bootstrap, configure, and operate AMB_V2 inside external consumer repositories. Use when running amb setup, creating .amb/ project configurations, declaring stack QA commands, or executing AMB tools from any project folder.
---

# 🔌 AMB Consumer Bootstrap

Especialista em plugar, configurar e operar a plataforma `amb_v2` em **qualquer repositório consumidor externo**.

## 📌 Visão Geral & Arquitetura

O `amb_v2` é agnóstico a projetos:
- É instalado globalmente no ambiente Python (`pip install -e .`).
- O executável `amb` pode ser chamado em **qualquer diretório**.
- A função [`find_repo_root()`](file:///c:/Users/DiogoHungaro/Desktop/Script/amb_v2/config/__init__.py) descobre automaticamente a raiz do projeto onde o terminal está aberto (buscando por `.git`, `package.json` ou `pyproject.toml`).
- O repositório consumidor armazena suas configurações específicas em uma pasta local chamada `.amb/`.

---

## 🚀 Passo a Passo: Configurando um Novo Projeto

### 1. Instalação Global do AMB_V2 (Modo Editável)
No diretório do `amb_v2`, instale o pacote globalmente uma única vez:
```bash
pip install -e .
```
Isso disponibiliza o comando `amb` no terminal de qualquer pasta do seu computador.

### 2. Inicializar o AMB no Projeto Consumidor
Abra o terminal no repositório que deseja gerenciar e execute:
```bash
amb setup
```
*Ou modo não interativo:*
```bash
amb setup --auto
```

Isso criará a seguinte estrutura no projeto consumidor:
```text
meu-projeto/
├── .amb/
│   ├── amb_project.json      # Configuração de stack, QA e metadados
│   ├── personas/             # Personas especializadas deste projeto
│   └── diarios/              # Histórico cognitivo e lições aprendidas
└── .env                      # Chaves de API (JULES_API_KEY, etc.)
```

### 3. Configurar `.amb/amb_project.json`
Exemplo de configuração com comandos de validação de QA do projeto:
```json
{
  "name": "meu-projeto",
  "stack": "node",
  "qa": {
    "typecheck": "npm run typecheck",
    "lint": "npm run lint",
    "test": "npm test",
    "build": "npm run build"
  }
}
```
*Para projetos Python:*
```json
{
  "name": "meu-backend",
  "stack": "python",
  "qa": {
    "test": "pytest",
    "typecheck": "python -m py_compile app.py"
  }
}
```

### 4. Validar o Ambiente
Verifique se todas as chaves e ferramentas necessárias estão ativas no projeto consumidor:
```bash
amb check
```

---

## 🛠️ Comandos Comuns no Projeto Consumidor

Uma vez inicializado, você pode executar todos os fluxos normais do AMB direto do novo projeto:

```bash
# Iniciar o sentinela para monitorar sessões:
amb monitor

# Listar personas ativas do projeto:
amb agent --list

# Despachar uma persona para desenvolver no Jules:
amb agent --role bolt

# Executar persona localmente via agy CLI:
amb agent --role bolt --agy

# Iniciar o loop autônomo completo com auto-merge:
amb agent --all --loop
```

---

## ⚠️ Checklist de Boas Práticas no Repositório Consumidor

1. **Gitignore:**
   - Adicione `.amb/diarios/` e `.env` ao `.gitignore` do projeto consumidor para evitar versionamento de credenciais e logs temporários.
   - Versionar `.amb/amb_project.json` e `.amb/personas/` é recomendado para que toda a equipe use as mesmas personas.
2. **Compatibilidade de QA no Windows:**
   - Evite scripts que dependam de bash puro caso a equipe utilize Windows. O pipeline do AMB resolve executáveis `.cmd` automaticamente se declarados no `qa`.
