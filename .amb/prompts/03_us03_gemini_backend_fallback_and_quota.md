# 🎯 US-03: Integrar Fallback para REST e Rotação de Quota no Backend Gemini

## 👤 User Story
> **Como** operador de pipelines autônomos no AMB,  
> **Quero** que o método principal `_generate_via_gemini_api` tente gerar primeiro via `google-genai` SDK e degrade graciosamente para REST caso o SDK falhe ou ocorra erro de quota 429,  
> **Para que** o sistema tenha resiliência ininterrupta durante longas execuções contínuas.

---

## 📌 Critérios de Aceitação BDD

* **Cenário 1: Tentativa primária via SDK com sucesso**
  * **Dado** que `HAS_GENAI_SDK` é `True`;
  * **Quando** `_generate_via_gemini_api` for invocado;
  * **Então** deve tentar primeiro `_generate_via_sdk(...)`;
  * **E** se retornar texto com sucesso, deve retornar o resultado imediatamente sem fazer requisição REST.

* **Cenário 2: Fallback transparente para REST em erro do SDK**
  * **Dado** que `HAS_GENAI_SDK` é `False` OU `_generate_via_sdk` disparou uma exceção inesperada de biblioteca;
  * **Quando** a exceção for capturada;
  * **Então** deve registrar log informativo de fallback;
  * **E** deve executar a requisição REST legada via `self.google_client.execute_request(...)`.

* **Cenário 3: Rotação de modelos em erro de limite de quota (429)**
  * **Dado** que o modelo atual retornou erro 429 ou Rate Limit;
  * **Quando** o erro for identificado;
  * **Então** deve tentar o próximo modelo da lista (`models_to_try = [model, "gemini-3.8-flash", "gemini-3.7-flash", "gemini-3.6-flash", "gemini-3.1-pro-preview"]`);
  * **E** se todos os modelos falharem, deve lançar `ApiExecutionError`.

---

## 🛠️ Arquivos Alvo & Alterações Necessárias

### `amb_cli/integrations/antigravity/antigravity_core/gemini_backend.py`
Atualizar o corpo do método `_generate_via_gemini_api`:
```python
    def _generate_via_gemini_api(
        self,
        prompt: str,
        model: str,
        system_instruction: Optional[str] = None,
        temperature: float = 0.2,
        max_output_tokens: int = 8192
    ) -> str:
        """Executa chamada do Gemini priorizando SDK oficial com fallback para REST."""
        if not self.api_key:
            require_env("GEMINI_API_KEY")

        models_to_try = [model]
        for fallback_m in ["gemini-3.8-flash", "gemini-3.7-flash", "gemini-3.6-flash", "gemini-3.1-pro-preview"]:
            if fallback_m not in models_to_try:
                models_to_try.append(fallback_m)

        last_err = None
        for current_m in models_to_try:
            # 1. Tentativa Primária via SDK Oficial
            if HAS_GENAI_SDK:
                try:
                    return self._generate_via_sdk(
                        prompt=prompt,
                        model=current_m,
                        system_instruction=system_instruction,
                        temperature=temperature,
                        max_output_tokens=max_output_tokens
                    )
                except Exception as sdk_err:
                    err_str = str(sdk_err)
                    if "429" in err_str or "503" in err_str or "RESOURCE_EXHAUSTED" in err_str:
                        log("ANTIGRAVITY", f"Limite de cota no modelo ({current_m}) via SDK. Tentando fallback...", Colors.YELLOW)
                        last_err = ApiExecutionError(f"Cota esgotada no modelo {current_m}: {sdk_err}")
                        continue
                    log("ANTIGRAVITY", f"Falha no SDK ({current_m}), alternando para REST: {sdk_err}", Colors.YELLOW)

            # 2. Fallback Secundário via REST Clássica
            try:
                return self._generate_via_rest(
                    prompt=prompt,
                    model=current_m,
                    system_instruction=system_instruction,
                    temperature=temperature,
                    max_output_tokens=max_output_tokens
                )
            except ApiExecutionError as e:
                last_err = e
                if "429" in str(e) or "503" in str(e) or "Rate Limit" in getattr(e, "hint", ""):
                    log("ANTIGRAVITY", f"Limite ou instabilidade no modelo REST ({current_m}). Tentando próximo...", Colors.YELLOW)
                    continue
                raise e
            except Exception as e:
                last_err = ApiExecutionError(f"Falha de conexão com a API do Gemini ({current_m}): {e}")
                continue

        raise last_err or ApiExecutionError("Falha na chamada dos modelos Gemini.")
```
(Nota: Renomeie o trecho original que montava o payload REST para `_generate_via_rest(...)` para manter o código limpo, modular e legível).

---

## 🔍 Comandos de Verificação Local
```bash
# Validar execução da CLI com fallback existente
python -m amb_cli.cli agy rules

# Executar suíte completa de testes
pytest -q

# Validar conformidade de tamanho (<= 250 linhas)
python -m amb_cli.cli validate amb_cli/integrations/antigravity/antigravity_core/gemini_backend.py
```

---

## 📋 Definition of Done (DoD)
- [ ] Orquestração SDK ➔ REST ➔ Rotação de modelos implementada.
- [ ] Método legado extraído de forma limpa para `_generate_via_rest(...)`.
- [ ] Arquivo `gemini_backend.py` mantido estritamente abaixo de 200 linhas.
- [ ] Todos os 159 testes existentes continuam passando no `pytest`.
