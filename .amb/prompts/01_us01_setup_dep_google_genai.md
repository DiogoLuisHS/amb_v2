# 🎯 US-01: Adicionar Dependência `google-genai` e Importação Defensiva

## 👤 User Story
> **Como** engenheiro de software do AMB_V2,  
> **Quero** declarar a dependência oficial `google-genai` no projeto e configurar a importação defensiva em `gemini_backend.py`,  
> **Para que** o ecossistema suporte o novo SDK oficial do Google sem quebrar ambientes onde a biblioteca ainda não foi instalada.

---

## 📌 Critérios de Aceitação BDD

* **Cenário 1: Declaração de dependência no empacotamento**
  * **Dado** os arquivos `pyproject.toml` e `setup.py`;
  * **Quando** o Jules inspecionar as listas de dependências;
  * **Então** deve adicionar `"google-genai>=1.0.0"` em `dependencies` (`pyproject.toml`) e em `install_requires` (`setup.py`).

* **Cenário 2: Importação defensiva sem erro em runtime**
  * **Dado** o arquivo `amb_cli/integrations/antigravity/antigravity_core/gemini_backend.py`;
  * **Quando** for importado em um ambiente sem `google-genai`;
  * **Então** deve definir `HAS_GENAI_SDK = False` sem disparar `ModuleNotFoundError` ou `ImportError`.

* **Cenário 3: Detecção positiva quando o SDK está presente**
  * **Dado** que `google-genai` está instalado;
  * **Quando** o módulo for carregado;
  * **Então** `HAS_GENAI_SDK` deve ser `True`, expondo `genai` e `types`.

---

## 🛠️ Arquivos Alvo & Alterações Necessárias

### 1. `pyproject.toml`
Adicionar `"google-genai>=1.0.0"` na lista `dependencies`.

### 2. `setup.py`
Adicionar `"google-genai>=1.0.0"` na lista `install_requires`.

### 3. `amb_cli/integrations/antigravity/antigravity_core/gemini_backend.py`
Inserir no topo do arquivo:
```python
try:
    from google import genai
    from google.genai import types
    HAS_GENAI_SDK = True
except ImportError:
    genai = None  # type: ignore
    types = None  # type: ignore
    HAS_GENAI_SDK = False
```
Manter a classe `GeminiBackend` existente sem alterações funcionais nesta etapa.

---

## 🔍 Comandos de Verificação Local
```bash
# Validar sintaxe e importação do backend
python -c "from amb_cli.integrations.antigravity.antigravity_core.gemini_backend import HAS_GENAI_SDK; print('HAS_GENAI_SDK:', HAS_GENAI_SDK)"

# Validar que a suíte existente de testes permanece verde
pytest -q

# Validar conformidade de tamanho (<= 250 linhas)
python -m amb_cli.cli validate amb_cli/integrations/antigravity/antigravity_core/gemini_backend.py
```

---

## 📋 Definition of Done (DoD)
- [ ] `google-genai>=1.0.0` adicionado em `pyproject.toml` e `setup.py`.
- [ ] Bloco `try/except ImportError` com `HAS_GENAI_SDK` implementado em `gemini_backend.py`.
- [ ] Suíte existente `pytest` 100% verde (159 testes passando).
- [ ] Arquivo `gemini_backend.py` com menos de 100 linhas.
