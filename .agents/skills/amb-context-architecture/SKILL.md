---
name: amb-context-architecture
description: >-
  Map repository layers and generate structured architectural blueprints using ai_context_builder.py in AMB_V2. Use when analyzing project topology, generating AI context maps for Jules or AGY prompts, or customizing layer configurations.
---

# 🏗️ AMB Context Architecture

Especialista no mapeamento de camadas e sintetização de blueprints arquiteturais via [`architecture/ai_context_builder.py`](file:///c:/Users/DiogoHungaro/Desktop/Script/amb_v2/architecture/ai_context_builder.py) no `amb_v2`.

## 📌 Visão Geral & Benefício

Modelos de IA na nuvem (como o Google Jules) perdem de 20 a 30 minutos por sessão explorando arquivos do repositório para entender onde ficam o banco de dados, os serviços e as rotas.

O **`ai_context_builder`** resolve isso:
- Ele varre o projeto ativo em milissegundos.
- Classifica cada arquivo em sua camada arquitetural correta (`Database`, `Services`, `API`, `UI`, `Config`).
- Gera um roteiro Markdown compacto que é injetado diretamente no início do prompt do agente.

---

## 🏛️ As Camadas Arquiteturais (`LAYERS_CONFIG`)

O builder classifica arquivos com base nas seguintes categorias canônicas:

| Camada | Padrões de Pastas & Nomes | Finalidade |
| :--- | :--- | :--- |
| **Database** | `models/`, `db/`, `migrations/`, `entities/`, `schema` | Modelagem e persistência de dados. |
| **Domain / Services** | `services/`, `use_cases/`, `domain/`, `core/`, `logic/` | Regras de negócio e casos de uso. |
| **API / Transport** | `api/`, `routes/`, `controllers/`, `handlers/`, `endpoints/` | Interfaces HTTP, REST ou RPC. |
| **UI / Client** | `views/`, `components/`, `pages/`, `frontend/`, `templates/` | Telas e componentes visuais. |
| **Configuration** | `config/`, `.env`, `settings/`, `setup` | Ajustes de ambiente e dependências. |
| **Tests** | `tests/`, `spec/`, `__tests__/` | Suítes de validação automatizada. |

---

## 🚀 Como Executar o Builder

### 1. Via Linha de Comando (`amb context`)
```bash
# Mapeia a arquitetura completa do projeto ativo:
amb context

# Mapeia com foco em um módulo ou submódulo específico:
amb context auth
```

### 2. Uso Programático em Python
```python
from architecture.ai_context_builder import build_ai_context

# Gera o bloco Markdown de contexto arquitetural
context_md = build_ai_context(focus_module="financeiro", max_files_per_layer=15)
print(context_md)
```

---

## 🔧 Extensibilidade e Regras de SRP

1. **Separação de Responsabilidades (SRP):**
   - A função `_determine_file_layer(filepath)` contém a regra pura de classificação.
   - O mapeamento é testado de forma isolada em [`tests/test_ai_context_builder.py`](file:///c:/Users/DiogoHungaro/Desktop/Script/amb_v2/tests/test_ai_context_builder.py).
2. **Customização por Repositório:**
   - Em monorepos com estruturas específicas, padrões adicionais podem ser incluídos em `LAYERS_CONFIG` sem quebrar projetos existentes.
