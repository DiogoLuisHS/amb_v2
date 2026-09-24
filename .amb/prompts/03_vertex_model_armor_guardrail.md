# 🎯 Task: Guardrail de Segurança com Vertex AI Model Armor

## 📌 Contexto & Responsabilidade Única (SRP)
O **Vertex AI Model Armor** é a solução oficial do Google Cloud para proteção em tempo real contra prompt injection, jailbreaks e vazamento de informações pessoalmente identificáveis (PII) e credenciais em sistemas baseados em LLMs.
No AMB, os fluxos autônomos (`autonomous_loop` e `auto_reply`) enviam logs de compiladores, comandos bash e dúvidas de código para a IA. Em bases corporativas, é imperativo que segredos (`.env`, tokens, chaves JWT) e payloads maliciosos sejam neutralizados antes do envio ao modelo.

Sua missão é criar o módulo sanitizador `amb_cli/agents/auto_reply_core/model_armor.py` e integrá-lo ao `cognitive_advisor.py` e `BaseGoogleClient`.

---

## 🛠️ Arquivos Alvo & Alterações Necessárias

### 1. Novo Módulo: `amb_cli/agents/auto_reply_core/model_armor.py`
- Crie a classe `ModelArmorGuardrail`:
  - `sanitize_prompt(text: str) -> str`:
    - Remove/mascara credenciais sensíveis (chaves privadas, JWTs, senhas em strings de conexão, tokens `ghp_...`, `AQ.A...`).
    - Mascara dados de PII (e-mails com padrão `u***@d***.com`, IPs internos).
    - Detecta e neutraliza tentativas de prompt injection em mensagens de feedback (ex: "Ignore all previous instructions...").
  - `is_enabled() -> bool`: Verifica se a proteção está ativada via variável de ambiente `MODEL_ARMOR_ENABLED` (padrão: `True` para sanitização local regex/heurística; opcionalmente integrável com o endpoint remoto `modelarmor.googleapis.com` se configurado).
  - Teto do arquivo: <= 250 linhas.

### 2. Integrar em `amb_cli/agents/auto_reply_core/cognitive_advisor.py`
- No método que monta o prompt de aconselhamento para o Gemini:
  - Passe o texto dos logs e das dúvidas pelo `ModelArmorGuardrail.sanitize_prompt(...)`.
  - Garanta que mensagens enviadas ao Jules e ao Gemini estejam livres de segredos acidentais.

### 3. Integrar no `BaseGoogleClient`
- `amb_cli/integrations/common/base_google_client.py`:
  - Utilize o `ModelArmorGuardrail` para enriquecer a função `mask_sensitive_data`.

### 4. Testes Unitários
- `tests/test_auto_reply_srp.py`:
  - Crie testes unitários para `ModelArmorGuardrail`:
    - Validação de mascaramento de tokens GitHub e Google API Keys.
    - Validação de neutralização de strings com padrões de prompt injection.
    - Garantia de que texto legítimo de erro de código não seja danificado.

---

## 📋 Critérios de Aceite (DoD)
1. Logs com chaves e tokens acidentais são mascarados antes do envio ao Gemini.
2. Tentativas de jailbreak em inputs de feedback são sanitizadas.
3. Testes unitários com 100% de sucesso no `pytest`.
4. Arquivos estritamente abaixo do teto de 300 linhas.
