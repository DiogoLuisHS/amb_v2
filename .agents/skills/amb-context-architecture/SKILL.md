---
name: amb-context-architecture
description: >-
  Map repository layers and database schemas using amb context and amb schema inside any consumer project. Use when analyzing project topology, generating structured AI context blueprints for Jules or Antigravity prompts, or inspecting Drizzle/DB schemas.
---

# 🏗️ AMB Context Architecture

Guia para mapear a **arquitetura em camadas** e inspecionar **schemas de banco de dados** em qualquer projeto consumidor através dos comandos `amb context` e `amb schema`.

---

## 📌 1. Por que o Mapeamento Arquitetural é Vital?

Modelos de IA na nuvem (como o Google Jules) perdem de **20 a 30 minutos por sessão** explorando arquivos do repositório para entender onde ficam os modelos de banco de dados, os serviços, os controladores e os componentes visuais.

O comando **`amb context`** resolve isso instantaneamente:
- Varre o repositório consumidor em milissegundos.
- Classifica os arquivos do projeto em 6 camadas canônicas: **Database ➔ Domain/Services ➔ API/Transport ➔ UI/Client ➔ Configuration ➔ Tests**.
- Gera um roteiro Markdown ordenado que pode ser colado no topo de prompts ou injetado automaticamente nas sessões do Jules.
- **Resultado:** A IA vai direto ao ponto, não alucina caminhos de imports e conclui as tarefas na metade do tempo.

---

## 🚀 2. Operação do `amb context`

### 1. Mapear a Arquitetura Completa do Projeto
No terminal do seu projeto:
```bash
amb context
```

### 2. Mapear com Foco em um Módulo Específico
Quando estiver desenvolvendo uma funcionalidade restrita a uma área do sistema:
```bash
# Foco no módulo de autenticação:
amb context auth

# Foco no módulo financeiro:
amb context financeiro

# Foco no módulo de agendamentos/agenda:
amb context agenda
```

### 3. Obter Saída Estruturada em JSON
Para ferramentas automatizadas ou scripts de orquestração:
```bash
amb context auth --json
```

---

## 🏛️ 3. As 6 Camadas Canônicas do AMB

O AMB classifica automaticamente os arquivos do seu repositório com base em padrões de nomes e estruturas de pastas:

| Camada | Padrões de Pastas & Nomes | Finalidade no Projeto |
| :--- | :--- | :--- |
| **Database** | `models/`, `db/`, `migrations/`, `entities/`, `schema` | Tabelas, tipos de banco e migrações. |
| **Domain / Services** | `services/`, `use_cases/`, `domain/`, `core/`, `logic/` | Regras de negócio, cálculos e casos de uso. |
| **API / Transport** | `api/`, `routes/`, `controllers/`, `handlers/`, `endpoints/` | Rotas HTTP, endpoints REST ou GraphQL. |
| **UI / Client** | `views/`, `components/`, `pages/`, `frontend/`, `templates/` | Telas visuais, componentes e formulários. |
| **Configuration** | `config/`, `.env`, `settings/`, `setup` | Variáveis de ambiente e configuração de libs. |
| **Tests** | `tests/`, `spec/`, `__tests__/` | Testes unitários, de integração e e2e. |

---

## 🗄️ 4. Inspeção de Schemas de Banco de Dados (`amb schema`)

O AMB inclui um leitor de schemas somente leitura (Read-Only) que funciona em repositórios com Drizzle ORM, Prisma, TypeORM, SQLAlchemy ou arquivos SQL:

```bash
# Inspecionar todos os schemas e tabelas do projeto:
amb schema

# Filtrar tabelas por palavra-chave (ex: pedidos, users, kanban):
amb schema kanban

# Exibir os schemas em formato JSON:
amb schema --json
```

O comando exibe o nome das tabelas, colunas, tipos de dados, chaves primárias e relacionamentos sem precisar de conexão com banco de dados externo.

---

## 💡 5. Como Usar o Contexto em Prompts de Desenvolvimento

Ao redigir um arquivo de especificação ou prompt para enviar ao Jules ou Antigravity:

1. Rode `amb context <modulo>` no terminal.
2. Copie o bloco Markdown gerado.
3. Cole na seção `## 🗺️ Mapa Arquitetural do Módulo` do seu prompt:

```markdown
# Tarefa: Implementar Relatório de Vendas

## 🗺️ Mapa Arquitetural do Módulo
- Database: `apps/api/src/db/schemas/vendas.ts`
- Service: `apps/api/src/services/vendasService.ts`
- Controller: `apps/api/src/routes/vendasRoutes.ts`
- UI: `apps/web/src/pages/RelatorioVendas.tsx`

## Requisitos
...
```

*Nota:* Se você utilizar o `amb agent --loop`, essa injeção é realizada **100% no piloto automático** pelo AMB!
