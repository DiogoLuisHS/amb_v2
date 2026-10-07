# 🎯 US-08: Suíte de Testes Unitários Dedicada para `knowledge_grounding`

## 👤 User Story
> **Como** engenheiro de qualidade do AMB_V2,  
> **Quero** um novo arquivo de testes `tests/test_knowledge_grounding.py` cobrindo o comportamento do grounder e sua integração com o builder,  
> **Para que** a integridade da funcionalidade de grounding seja comprovada com 100% de sucesso automatizado.

---

## 📌 Critérios de Aceitação BDD

* **Cenário 1: Teste de renderização para múltiplas tecnologias conhecidas**
  * **Dado** as tecnologias `["fastapi", "react", "typescript"]`;
  * **Quando** `DeveloperKnowledgeGrounder().render_markdown(...)` for invocado;
  * **Então** o texto retornado deve conter o cabeçalho `Canonical Developer Knowledge Guidelines` e mencionar links oficiais para as 3 tecnologias.

* **Cenário 2: Teste de robustez para tecnologias desconhecidas**
  * **Dado** uma tecnologia não mapeada como `["desconhecida_lib_xyz"]`;
  * **Quando** o método for executado;
  * **Então** deve retornar uma string vazia `""` sem disparar exceção.

* **Cenário 3: Teste de flag `include_grounding` no builder**
  * **Dado** uma chamada mockada para `AIContextBuilder`;
  * **Quando** `build_context(..., include_grounding=True)` for chamado;
  * **Então** o resultado deve conter a seção de grounding;
  * **E** quando chamado com `include_grounding=False`, a seção NÃO deve estar presente.

---

## 🛠️ Arquivos Alvo & Alterações Necessárias

### Criar Novo Arquivo: `tests/test_knowledge_grounding.py`
```python
# -*- coding: utf-8 -*-
"""Testes unitários dedicados para o módulo de grounding de documentação oficial."""

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch
import pytest

_root = Path(__file__).resolve().parent.parent
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))
from core.bootstrap import ensure_amb_env
ensure_amb_env()

from architecture.context_core.knowledge_grounding import DeveloperKnowledgeGrounder, CANONICAL_GUIDELINES
from architecture.ai_context_builder import AIContextBuilder


def test_grounding_render_known_technologies():
    grounder = DeveloperKnowledgeGrounder()
    output = grounder.render_markdown(["fastapi", "drizzle"])
    assert "## 📚 Canonical Developer Knowledge Guidelines" in output
    assert "Fastapi" in output
    assert "Drizzle" in output
    assert "https://fastapi.tiangolo.com/" in output


def test_grounding_render_unknown_technologies():
    grounder = DeveloperKnowledgeGrounder()
    output = grounder.render_markdown(["unknown_tool_xyz"])
    assert output == ""


def test_grounding_case_insensitivity():
    grounder = DeveloperKnowledgeGrounder()
    output = grounder.render_markdown(["TYPESCRIPT", "React"])
    assert "Typescript" in output
    assert "React" in output


def test_grounding_empty_list():
    grounder = DeveloperKnowledgeGrounder()
    assert grounder.render_markdown([]) == ""


def test_ai_context_builder_grounding_flag_behavior():
    builder = AIContextBuilder(_root)
    # Testa chamada com include_grounding=True
    if hasattr(builder, "build_context"):
        res_with = builder.build_context(include_grounding=True)
        res_without = builder.build_context(include_grounding=False)
        assert isinstance(res_with, str)
        assert isinstance(res_without, str)
```
Teto do arquivo: <= 120 linhas.

---

## 🔍 Comandos de Verificação Local
```bash
# 1. Executar os novos testes unitários dedicados
pytest tests/test_knowledge_grounding.py -v

# 2. Executar toda a suíte de testes de arquitetura
pytest tests/test_knowledge_grounding.py tests/test_ai_context_builder.py -v

# 3. Executar toda a suíte pytest
pytest -q

# 4. Validar limites de linhas
python -m amb_cli.cli validate tests/test_knowledge_grounding.py
```

---

## 📋 Definition of Done (DoD)
- [ ] Arquivo `tests/test_knowledge_grounding.py` criado com 5+ testes.
- [ ] 100% de sucesso em `pytest tests/test_knowledge_grounding.py`.
- [ ] Nenhum arquivo modificado ultrapassa 290 linhas.
- [ ] Suíte global `pytest` continua 100% passando.
