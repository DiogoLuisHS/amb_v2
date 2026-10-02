# 🎯 US-09: Módulo Fundamental `ModelArmorGuardrail` e Padrões de Mascaramento

## 👤 User Story
> **Como** engenheiro de segurança corporativa do AMB_V2,  
> **Quero** criar o pacote fundamental `amb_cli/core/security/model_armor.py`,  
> **Para que** tenhamos um módulo centralizado capaz de ofuscar tokens GitHub, chaves Google, JWTs e senhas em URLs de banco de dados antes do envio a provedores de LLM.

---

## 📌 Critérios de Aceitação BDD

* **Cenário 1: Mascaramento de tokens GitHub e chaves Google API**
  * **Dado** um texto contendo tokens como `ghp_abcdef1234567890` ou `AIzaSyD1234567890abcdefghijklmnopqrstuv`;
  * **Quando** `ModelArmorGuardrail.sanitize_prompt(text)` for executado;
  * **Então** os tokens devem ser substituídos por identificadores ofuscados como `ghp_***[REDACTED_GH_TOKEN]` e `AIza***[REDACTED_GKEY]`.

* **Cenário 2: Mascaramento de senhas em URLs de banco de dados**
  * **Dado** uma connection string como `postgres://admin:segredo123@localhost:5432/app`;
  * **Quando** o sanitizador for acionado;
  * **Então** a senha deve ser ofuscada resultando em `postgres://admin:***@localhost:5432/app`.

* **Cenário 3: Respeito à variável de ambiente `MODEL_ARMOR_ENABLED`**
  * **Dado** que `MODEL_ARMOR_ENABLED="false"` foi configurada no ambiente;
  * **Quando** `sanitize_prompt(text)` for chamado;
  * **Então** o texto deve ser retornado intacto sem modificações.

---

## 🛠️ Arquivos Alvo & Alterações Necessárias

### 1. Criar `amb_cli/core/security/__init__.py`
```python
# -*- coding: utf-8 -*-
"""Pacote de segurança e guardrails do AMB_V2."""
from .model_armor import ModelArmorGuardrail

__all__ = ["ModelArmorGuardrail"]
```

### 2. Criar `amb_cli/core/security/model_armor.py`
```python
# -*- coding: utf-8 -*-
"""Módulo sanitizador de credenciais e guardrail cognitivo."""

import os
import re
from typing import List, Tuple, Pattern


class ModelArmorGuardrail:
    """Guardrail local para higienização de credenciais e segredos em prompts."""

    PATTERNS: List[Tuple[Pattern, str]] = [
        # Tokens GitHub (ghp, gho, ghu, ghs, ghr)
        (re.compile(r"gh[pousr]_[A-Za-z0-9_]{16,255}"), "ghp_***[REDACTED_GH_TOKEN]"),
        # Chaves de API Google Cloud (AIza...)
        (re.compile(r"AIza[0-9A-Za-z-_]{35}"), "AIza***[REDACTED_GKEY]"),
        # JSON Web Tokens (JWT)
        (re.compile(r"eyJ[A-Za-z0-9-_=]+\.eyJ[A-Za-z0-9-_=]+\.[A-Za-z0-9-_.+/=]*"), "[REDACTED_JWT]"),
        # Senhas em Connection Strings (Postgres, MySQL, MariaDB, Mongo)
        (re.compile(r"(postgres(?:ql)?|mysql|mariadb|mongodb(?:\+srv)?)://([^:]+):([^@]+)@"), r"\1://\2:***@"),
    ]

    @classmethod
    def is_enabled(cls) -> bool:
        """Verifica se o guardrail está ativo (padrão: True)."""
        return os.getenv("MODEL_ARMOR_ENABLED", "true").lower() in ("1", "true", "yes")

    @classmethod
    def sanitize_prompt(cls, text: str) -> str:
        """Sanitiza segredos e tokens sensíveis do texto."""
        if not text or not cls.is_enabled():
            return text or ""
        sanitized = str(text)
        for pattern, replacement in cls.PATTERNS:
            sanitized = pattern.sub(replacement, sanitized)
        return sanitized
```
Teto do arquivo: <= 120 linhas.

---

## 🔍 Comandos de Verificação Local
```bash
# Validar importação e sanitização básica
python -c "from amb_cli.core.security.model_armor import ModelArmorGuardrail; print(ModelArmorGuardrail.sanitize_prompt('Token: ghp_12345678901234567890'))"

# Garantir integridade da suíte pytest
pytest -q

# Validar conformidade de tamanho
python -m amb_cli.cli validate amb_cli/core/security/model_armor.py
```

---

## 📋 Definition of Done (DoD)
- [ ] Pacote `amb_cli/core/security/` criado com `__init__.py` e `model_armor.py`.
- [ ] Classe `ModelArmorGuardrail` com padrões de mascaramento para GitHub tokens, Google API keys, JWTs e DB URLs.
- [ ] Suporte à variável `MODEL_ARMOR_ENABLED`.
- [ ] Arquivo com menos de 100 linhas.
- [ ] Suíte global `pytest` continua 100% verde.
