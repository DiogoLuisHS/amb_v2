# 🎯 US-02: Implementar Geração via SDK Oficial `google-genai`

## 👤 User Story
> **Como** desenvolvedor executando inferências cognitivas no AMB,  
> **Quero** que `GeminiBackend` possua um método dedicado `_generate_via_sdk` utilizando `genai.Client`,  
> **Para que** as chamadas aproveitem a tipagem nativa de `GenerateContentConfig` e os modelos mais recentes do Gemini.

---

## 📌 Critérios de Aceitação BDD

* **Cenário 1: Chamada de geração com o SDK oficial**
  * **Dado** que `HAS_GENAI_SDK` é `True` e a `api_key` foi fornecida;
  * **Quando** `_generate_via_sdk(prompt, model, system_instruction, temperature, max_output_tokens)` for executado;
  * **Então** deve instanciar `genai.Client(api_key=self.api_key)`;
  * **E** deve invocar `client.models.generate_content(...)` com `GenerateContentConfig`;
  * **E** deve retornar a string de texto limpa (`response.text.strip()`).

* **Cenário 2: Tratamento de resposta vazia do SDK**
  * **Dado** que o modelo Gemini retornou uma resposta sem texto (`response.text` vazio ou None);
  * **Quando** o retorno for inspecionado;
  * **Então** deve lançar `ApiExecutionError("Resposta vazia retornada pelo modelo Gemini via SDK.")`.

* **Cenário 3: Configuração correta de System Instruction e Temperature**
  * **Dado** que foram fornecidos `system_instruction="Você é o Jules"` e `temperature=0.2`;
  * **Quando** o payload de configuração for gerado;
  * **Então** `types.GenerateContentConfig` deve conter esses valores correspondentes.

---

## 🛠️ Arquivos Alvo & Alterações Necessárias

### `amb_cli/integrations/antigravity/antigravity_core/gemini_backend.py`
Adicionar o método auxiliar privado na classe `GeminiBackend`:
```python
    def _generate_via_sdk(
        self,
        prompt: str,
        model: str,
        system_instruction: Optional[str] = None,
        temperature: float = 0.2,
        max_output_tokens: int = 8192
    ) -> str:
        """Executa a geração de conteúdo usando o SDK oficial google-genai."""
        if not HAS_GENAI_SDK or genai is None or types is None:
            raise ApiExecutionError("SDK google-genai não está disponível no ambiente.")

        client = genai.Client(api_key=self.api_key)
        config = types.GenerateContentConfig(
            temperature=temperature,
            max_output_tokens=max_output_tokens,
            system_instruction=system_instruction if system_instruction else None
        )
        response = client.models.generate_content(
            model=model,
            contents=prompt,
            config=config
        )
        if response and response.text:
            return response.text.strip()
        raise ApiExecutionError("Resposta vazia retornada pelo modelo Gemini via SDK.")
```
Mantenha o método `_generate_via_gemini_api` existente intacto por enquanto.

---

## 🔍 Comandos de Verificação Local
```bash
# Validar sintaxe da classe GeminiBackend
python -c "from amb_cli.integrations.antigravity.antigravity_core.gemini_backend import GeminiBackend; print('Método presente:', hasattr(GeminiBackend, '_generate_via_sdk'))"

# Garantir que a suíte existente de testes permanece verde
pytest -q

# Validar conformidade de tamanho (<= 250 linhas)
python -m amb_cli.cli validate amb_cli/integrations/antigravity/antigravity_core/gemini_backend.py
```

---

## 📋 Definition of Done (DoD)
- [ ] Método `_generate_via_sdk` implementado na classe `GeminiBackend`.
- [ ] Tipagem estrita com `Optional[str]`, `float`, `int` e retorno `str`.
- [ ] Validação de resposta vazia disparando `ApiExecutionError`.
- [ ] Arquivo `gemini_backend.py` mantido estritamente abaixo de 150 linhas.
- [ ] Toda a suíte `pytest` continua 100% verde.
