# US-40: Modo Conversacional Contínuo no Hub do Advisor (amb advisor --chat)

## 📌 Contexto e Objetivo
Atualmente, o comando `amb advisor` ([`auto_reply.py`](file:///c:/Users/DiogoHungaro/Desktop/Script/amb_v2/amb_cli/agents/auto_reply.py)) atua estritamente de forma pontual (one-shot): ele detecta a dúvida pendente, gera ou solicita a resposta, despacha a mensagem via API e encerra o processo no terminal.

Caso o desenvolvedor queira manter um diálogo contínuo de alinhamento com a Cloud VM do Jules (ex: esclarecer requisitos, fornecer orientações arquiteturais iterativas ou tirar dúvidas complementares), ele é forçado a reexecutar o comando repetidamente ou abandonar a CLI para usar o navegador web.

Esta US enriquece o comando `amb advisor` com a flag `--chat` (`-c`), introduzindo um modo de conversação contínuo (REPL interativo) que permite trocar mensagens sequenciais com o Jules com exibição das respostas diretamente no console até que o desenvolvedor decida encerrar.

---

## 📐 Requisitos Técnicos

### 1. Loop Interativo de Chat no Dispatcher
- **Arquivo (`amb_cli/agents/auto_reply_core/jules_feedback_dispatcher.py`):**
  - Adicionar o método:
    ```python
    def run_continuous_chat(self, session_id: str) -> None:
        """Mantém um REPL conversacional contínuo com a sessão do Jules."""
    ```
  - Exibir cabeçalho: `=== 💬 AMB ADVISOR: CHAT INTERATIVO COM GOOGLE JULES ===`
  - Iniciar loop `while True`:
    - Exibir prompt: `\n💬 Você (ou 'exit' / 'sair' para encerrar) > `
    - Se entrada vazia: continuar.
    - Se entrada for 'exit', 'sair', 'q': emitir mensagem de despedida e encerrar loop.
    - Se for texto:
      - Despachar mensagem via `self.client.send_message(session_id=session_id, prompt=user_msg)`.
      - Exibir: `✔ Mensagem enviada ao Jules. Aguardando processamento...`
      - Aguardar brevemente (polling de 3 a 5s) pelas novas atividades emitidas pelo Jules e imprimir a resposta do agente assim que disponível.
  - Manter o limite rígido de 300 linhas por arquivo (Regra 02).

### 2. Integração no `auto_reply.py` e Handler
- **Arquivo (`amb_cli/agents/auto_reply.py`):**
  - Expor a função `start_advisor_chat(session_id: Optional[str] = None) -> None`:
    - Se `session_id` for fornecido: invocar `dispatcher.run_continuous_chat(session_id)`.
    - Se omitido: listar as sessões pendentes, solicitar que o usuário selecione uma pelo índice numérico e iniciar o chat.
- **Arquivo (`amb_cli/cli_modules/cli_parsers.py`):**
  - No subparser `advisor`:
    ```python
    p.add_argument("--chat", "-c", action="store_true", help="Inicia sessão de chat conversacional contínuo (REPL) com o agente Jules.")
    ```
- **Arquivo (`amb_cli/cli_modules/handlers_core/jules_handler.py` ou `cli_handlers.py`):**
  - Se `getattr(args, "chat", False)` for True, invocar `start_advisor_chat(session_id=args.session_id)`.

---

## 🧪 Critérios de Aceite
1. **Suíte de Testes Unitários:**
   - Criar `tests/test_advisor_continuous_chat.py` cobrindo:
     - Envio de mensagem e encerramento ao receber 'exit' ou EOF.
     - Resolução de `session_id` específico e seleção a partir de sessões pendentes.
     - Tratamento gracioso de `KeyboardInterrupt` encerrando o chat sem quebras.
     - Parsing da flag `--chat` / `-c` no parser de CLI de `amb advisor`.
2. **Qualidade de Código e Limites Arquiteturais:**
   - 100% dos testes unitários passando (`pytest -q`).
   - Teto rígido de 300 linhas por arquivo (Regra 02).
   - Tipagem estrita com `typing` (Regra 04).
