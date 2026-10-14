# US-43: Subcomando Direto de Streaming amb jules watch (ou logs)

## 📌 Contexto e Objetivo
Para acompanhar a execução ao vivo de uma tarefa na nuvem do Google Jules, o desenvolvedor atualmente precisa digitar:
```bash
amb jules get <session_id> --watch
```
Como o acompanhamento contínuo de logs e streaming de saídas da VM é a ação mais recorrente no ciclo diário de desenvolvimento com o Jules, exigir o subcomando `get` junto à flag `--watch` (ou `-w`) cria fricção desnecessária.

Esta US introduz o subcomando ergonômico direto:
```bash
amb jules watch <session_id>
# ou o alias intuitivo:
amb jules logs <session_id>
```

---

## 📐 Requisitos Técnicos

### 1. Atualização do Parser CLI
- **Arquivo (`amb_cli/cli_modules/cli_parsers.py`):**
  - No subparser `jules`:
    - Adicionar o subcomando `watch` com aliases `["logs"]`:
      ```python
      j = _sc(js, "watch", "Acompanha streaming contínuo de atividades e saídas da sessão em tempo real.", ["logs"])
      _sid(j, "ID ou URL da sessão do Jules.")
      _j(j)
      ```

### 2. Atualização do Handler
- **Arquivo (`amb_cli/cli_modules/handlers_core/jules_handler.py`):**
  - Incluir no roteamento de subcomandos:
    ```python
    elif sub in ["watch", "logs"]:
        sid = getattr(args, "session_id", None) or getattr(args, "session_id_flag", None)
        if not sid:
            log_error("JULES", "Informe o ID da sessão para acompanhar os logs.")
            return
        from integrations.jules.tools.get_session import run_get_session
        run_get_session(
            session_id=sid,
            watch=True,
            as_json=getattr(args, "json", False)
        )
    ```

---

## 🧪 Critérios de Aceite
1. **Suíte de Testes Unitários:**
   - Criar `tests/test_jules_watch_direct.py` cobrindo:
     - Parsing do subcomando `watch` e do alias `logs` com repasse de `session_id`.
     - Invocação correta de `run_get_session` com `watch=True`.
     - Tratamento amigável quando `session_id` não é fornecido.
2. **Qualidade de Código:**
   - 100% dos testes passando (`pytest -q`).
   - Teto rígido de 300 linhas por arquivo (Regra 02).
   - Tipagem estrita com `typing` (Regra 04).
