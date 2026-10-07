# 🎯 US-11: Integrar `ModelArmorGuardrail` em `BaseGoogleClient` e `CognitiveAdvisor`

## 👤 User Story
> **Como** arquiteto de software do AMB_V2,  
> **Quero** integrar o `ModelArmorGuardrail` na fundação HTTP `BaseGoogleClient` e no módulo `CognitiveAdvisor`,  
> **Para que** todas as mensagens de log de rede e todos os prompts de auto-resposta passem automaticamente pela esteira de sanitização sem acoplamento reverso.

---

## 📌 Critérios de Aceitação BDD

* **Cenário 1: Sanitização automática no cliente HTTP base**
  * **Dado** que `BaseGoogleClient.mask_sensitive_data(text)` foi chamado com uma URL contendo chaves ou senhas;
  * **Quando** o método for executado;
  * **Então** deve delegar para `ModelArmorGuardrail.sanitize_prompt(text)` e retornar a string ofuscada.

* **Cenário 2: Sanitização automática no conselheiro cognitivo**
  * **Dado** que o Jules fez uma pergunta de código ou enviou um log de erro contendo credenciais;
  * **Quando** o `CognitiveAdvisor` montar o prompt para o Gemini;
  * **Então** o texto de contexto deve ser sanitizado via `ModelArmorGuardrail.sanitize_prompt(...)` antes da chamada ao modelo.

* **Cenário 3: Ausência de ciclos de importação (Clean Architecture)**
  * **Dado** a hierarquia de camadas do AMB (`core` ➔ `integrations` / `agents`);
  * **Quando** ambos os módulos importarem `core.security.model_armor`;
  * **Então** nenhum `CircularImportError` deve ocorrer.

---

## 🛠️ Arquivos Alvo & Alterações Necessárias

### 1. `amb_cli/integrations/common/base_google_client.py`
Importe o guardrail e atualize o método `mask_sensitive_data`:
```python
from core.security.model_armor import ModelArmorGuardrail

    def mask_sensitive_data(self, text: str) -> str:
        """Ofusca dados sensíveis e credenciais via ModelArmorGuardrail."""
        if not text:
            return ""
        return ModelArmorGuardrail.sanitize_prompt(str(text))
```
> ⚠️ **ATENÇÃO:** Mantenha `base_google_client.py` abaixo de 240 linhas (atualmente tem 218 linhas).

### 2. `amb_cli/agents/auto_reply_core/cognitive_advisor.py`
Importe o guardrail e passe os logs/contextos pelo sanitizador antes da montagem final do prompt enviado ao Gemini:
```python
from core.security.model_armor import ModelArmorGuardrail
# No método de aconselhamento/geração:
safe_log = ModelArmorGuardrail.sanitize_prompt(raw_log)
```
> ⚠️ **ATENÇÃO:** Mantenha `cognitive_advisor.py` abaixo de 200 linhas (atualmente tem 179 linhas).

---

## 🔍 Comandos de Verificação Local
```bash
# Validar execução combinada do cliente base e advisor
python -c "from amb_cli.integrations.common.base_google_client import BaseGoogleClient; c = BaseGoogleClient(); print(c.mask_sensitive_data('key: AIzaSyD1234567890abcdefghijklmnopqrstuv'))"

# Executar testes existentes de base_google_client e auto_reply
pytest tests/test_base_google_client.py tests/test_auto_reply_srp.py -v

# Validar limites de linhas
python -m amb_cli.cli validate amb_cli/integrations/common/base_google_client.py
python -m amb_cli.cli validate amb_cli/agents/auto_reply_core/cognitive_advisor.py
```

---

## 📋 Definition of Done (DoD)
- [ ] `BaseGoogleClient.mask_sensitive_data` integrado ao `ModelArmorGuardrail`.
- [ ] `CognitiveAdvisor` higienizando contexto antes de chamar o modelo.
- [ ] Zero dependências circulares entre camadas.
- [ ] Ambos os arquivos mantidos rigorosamente dentro dos limites de linhas (< 250 linhas).
- [ ] Testes existentes em `test_base_google_client.py` e `test_auto_reply_srp.py` 100% verdes.
