# US-46: Desacoplamento Cirúrgico de amb jules reply para amb advisor

## 📌 Contexto e Objetivo
Atualmente, quando o desenvolvedor executa `amb jules reply` sem especificar o ID da sessão, o sistema invoca uma rotina legada de conselheiro (`run_auto_advisor()`).
Com a consolidação do comando de alto nível `amb advisor` como o Hub Central e Interativo de Chat Contínuo (US-40), manter essa mesma lógica duplicada sob `amb jules reply` confunde o usuário sobre qual comando utilizar.

Esta US desacopla cirurgicamente as responsabilidades:
1. **`amb jules reply <id>` (Pontual / Scriptável):** Mantém-se estritamente focado no envio pontual ou na auto-resposta direta para a sessão informada (`--message "<texto>"` ou `-y` para auto-aprovação com IA).
2. **`amb jules reply` (Sem ID):** Em vez de executar uma rotina duplicada, delega diretamente para o Hub central unificado `cmd_advisor`, exibindo um redirecionamento claro e mantendo DRY absoluto.

---

## 📐 Requisitos Técnicos

### 1. Atualização do Handler do Jules
- **Arquivo (`amb_cli/cli_modules/handlers_core/jules_handler.py`):**
  - No bloco `sub in ["reply", "advisor", "ask"]`:
    - Se `sid` fornecido:
      - Se `getattr(args, "message", None)`:
        - Invocar `run_send_message(session_id=sid, message=args.message, force=getattr(args, "force", False))`
      - Caso contrário:
        - Invocar `advise_and_reply(session_id=sid, auto_approve=getattr(args, "auto_approve", False))`
    - Se `not sid`:
      - Se `getattr(args, "message", None)`:
        - Exibir `log_error("JULES", "Informe o ID da sessão ao usar --message direta.")`
        - Retornar.
      - Caso contrário (invocação interativa sem parâmetros):
        - Delegar diretamente para o Hub central:
          ```python
          from cli_modules.cli_handlers import cmd_advisor
          cmd_advisor(args)
          ```
  - Manter o limite rígido de 300 linhas por arquivo (Regra 02).

---

## 🧪 Critérios de Aceite
1. **Suíte de Testes Unitários:**
   - Criar `tests/test_jules_reply_decouple.py` cobrindo:
     - Chamada a `amb jules reply` sem ID delegando com sucesso para `cmd_advisor`.
     - Chamada a `amb jules reply <id>` mantendo o comportamento de consulta e resposta pontual.
     - Chamada a `amb jules reply <id> -m "msg"` mantendo o envio direto da mensagem.
     - Erro amigável ao tentar passar `--message` sem especificar o ID da sessão.
2. **Qualidade de Código:**
   - 100% dos testes passando (`pytest -q`).
   - Teto rígido de 300 linhas por arquivo (Regra 02).
   - Tipagem estrita com `typing` (Regra 04).
