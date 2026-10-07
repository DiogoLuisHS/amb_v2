# 🎯 US-05: Módulo de Diretrizes Canônicas `DeveloperKnowledgeGrounder`

## 👤 User Story
> **Como** arquiteto de software do AMB_V2,  
> **Quero** criar o módulo `amb_cli/architecture/context_core/knowledge_grounding.py` com catálogo de diretrizes de engenharia e resiliência offline,  
> **Para que** o sistema possua uma fundação canônica de boas práticas oficiais para tecnologias modernas (TypeScript, FastAPI, Drizzle, React, Python).

---

## 📌 Critérios de Aceitação BDD

* **Cenário 1: Formatação de diretrizes para tecnologias reconhecidas**
  * **Dado** uma lista de tecnologias detectadas contendo `["fastapi", "drizzle"]`;
  * **Quando** `DeveloperKnowledgeGrounder().render_markdown(technologies)` for executado;
  * **Então** deve retornar um bloco Markdown com cabeçalho `## 📚 Canonical Developer Knowledge Guidelines` contendo as regras e links de documentação oficiais para FastAPI e Drizzle.

* **Cenário 2: Retorno vazio para listas vazias ou tecnologias desconhecidas**
  * **Dado** uma lista vazia ou contendo apenas bibliotecas fora do catálogo;
  * **Quando** `render_markdown(...)` for acionado;
  * **Então** deve retornar uma string vazia `""` sem poluir a saída nem lançar exceção.

* **Cenário 3: Tolerância a variações de maiúsculas/minúsculas**
  * **Dado** a lista contendo `["TypeScript", "REACT", "Python"]`;
  * **Quando** o grounder realizar o matching;
  * **Então** deve normalizar as chaves para minúsculo e incluir as diretrizes correspondentes.

---

## 🛠️ Arquivos Alvo & Alterações Necessárias

### Criar Novo Arquivo: `amb_cli/architecture/context_core/knowledge_grounding.py`
```python
# -*- coding: utf-8 -*-
"""Módulo de grounding semântico com diretrizes canônicas para agentes de IA."""

from typing import List, Dict, Optional

CANONICAL_GUIDELINES: Dict[str, Dict[str, str]] = {
    "typescript": {
        "standard": "Strict typing, zero 'any', discriminated unions, no-implicit-any.",
        "docs": "https://www.typescriptlang.org/docs/"
    },
    "fastapi": {
        "standard": "Pydantic v2 schemas, async def for I/O routes, Depends for DI.",
        "docs": "https://fastapi.tiangolo.com/"
    },
    "drizzle": {
        "standard": "Type-safe SQL schemas, explicit foreign keys, no implicit raw queries.",
        "docs": "https://orm.drizzle.team/docs/overview"
    },
    "react": {
        "standard": "Functional components, custom hooks for state/side-effects, Tailwind/pure CSS.",
        "docs": "https://react.dev/"
    },
    "python": {
        "standard": "PEP 8, type hints, SRP modules <= 300 lines, explicit exceptions.",
        "docs": "https://peps.python.org/pep-0008/"
    }
}


class DeveloperKnowledgeGrounder:
    """Provedor de diretrizes canônicas de engenharia para blueprints de IA."""

    def __init__(self, custom_catalog: Optional[Dict[str, Dict[str, str]]] = None):
        self.catalog = custom_catalog or CANONICAL_GUIDELINES

    def render_markdown(self, technologies: List[str]) -> str:
        """Gera seção Markdown concisa com diretrizes oficiais."""
        if not technologies:
            return ""

        matches = []
        for tech in sorted(set(t.lower() for t in technologies)):
            if tech in self.catalog:
                info = self.catalog[tech]
                matches.append(f"- **{tech.capitalize()}**: {info['standard']} ([Docs]({info['docs']}))")

        if not matches:
            return ""

        header = "\n## 📚 Canonical Developer Knowledge Guidelines\n"
        return header + "\n".join(matches) + "\n"
```
Teto do arquivo: <= 120 linhas.

---

## 🔍 Comandos de Verificação Local
```bash
# Validar importação e comportamento do módulo
python -c "from amb_cli.architecture.context_core.knowledge_grounding import DeveloperKnowledgeGrounder; g = DeveloperKnowledgeGrounder(); print(g.render_markdown(['fastapi', 'typescript']))"

# Garantir integridade da suíte pytest
pytest -q

# Validar conformidade de tamanho
python -m amb_cli.cli validate amb_cli/architecture/context_core/knowledge_grounding.py
```

---

## 📋 Definition of Done (DoD)
- [ ] Arquivo `amb_cli/architecture/context_core/knowledge_grounding.py` criado.
- [ ] Classe `DeveloperKnowledgeGrounder` implementada com catálogo `CANONICAL_GUIDELINES`.
- [ ] Método `render_markdown` com normalização de maiúsculas/minúsculas e retorno limpo.
- [ ] Arquivo com menos de 100 linhas.
- [ ] Suíte existente `pytest` 100% verde.
