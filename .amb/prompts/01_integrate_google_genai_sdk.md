# 🎯 Task: Integrar o Google Gen AI SDK Oficial (`google-genai`) no Backend Gemini

## 📌 Contexto & Responsabilidade Única (SRP)
Atualmente, o motor cognitivo do AMB em `amb_cli/integrations/antigravity/antigravity_core/gemini_backend.py` realiza requisições HTTP manuais via `requests.post` contra a API REST do Gemini.
O Google lançou o novo **Google Gen AI SDK unificado (`google-genai`)**, que oferece suporte nativo a:
1. Modelos de Raciocínio (Thinking models: `gemini-2.5-flash`, `gemini-2.5-pro`, `gemini-3.8-flash`).
2. Gerenciamento nativo de Context Caching (reduzindo custo de tokens em prompts repetidos do `autonomous_loop`).
3. Tipagem estrita e function calling compatível com Model Context Protocol (MCP).

Sua missão é migrar o `gemini_backend.py` para usar o cliente oficial `from google import genai`, mantendo fallback defensivo e respeitando a regra de atomização (máximo 300 linhas).

---

## 🛠️ Arquivos Alvo & Alterações Necessárias

### 1. Dependências do Projeto
- `pyproject.toml` e `setup.py`:
  - Adicione a dependência `google-genai>=1.0.0` na lista de `dependencies`.
  - Mantenha compatibilidade com Python 3.10+.

### 2. Refatorar `amb_cli/integrations/antigravity/antigravity_core/gemini_backend.py`
- Importe o cliente oficial:
  ```python
  try:
      from google import genai
      from google.genai import types
      HAS_GENAI_SDK = True
  except ImportError:
      HAS_GENAI_SDK = False
  ```
- Atualize a classe `GeminiBackend` (ou função de inferência):
  - Inicialize `client = genai.Client(api_key=api_key)`.
  - Invoque `client.models.generate_content(model=model, contents=prompt, config=...)`.
  - Suporte parâmetros de configuração: `temperature`, `system_instruction` e suporte a `thinking_budget` quando suportado pelo modelo.
  - Caso `HAS_GENAI_SDK` seja `False` (ou falhe por import), mantenha um fallback gracioso para a chamada REST existente via `requests`.
  - Mantenha o arquivo estritamente abaixo de **300 linhas**.

### 3. Testes Unitários
- `tests/test_antigravity_integration.py`:
  - Adicione testes com mock de `genai.Client` garantindo que chamadas com `google-genai` funcionem e retornem texto limpo.
  - Teste o fallback defensivo quando a biblioteca não estiver presente ou disparar exceção.
  - Garanta que a suíte `pytest` continue 100% verde.

---

## 📋 Critérios de Aceite (DoD)
1. `amb agy run "Olá mundo"` funciona com sucesso usando o novo SDK `google-genai`.
2. Modelos como `gemini-2.5-flash` respondem corretamente com parsing limpo de conteúdo.
3. Tratamento de exceções deriva de `AmbError` com mensagens acionáveis.
4. Todos os testes unitários (`pytest`) rodam com 100% de sucesso.
