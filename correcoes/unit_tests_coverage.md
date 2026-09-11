# 🧪 Criação de Suíte de Testes Unitários para AMB_V2

Agente responsável por implementar a suíte inicial de testes unitários automatizados com Pytest, cobrindo funções puras críticas de parsing e arquitetura.

## 🎯 Missão Principal
Criar arquivos de teste com `pytest` cobrindo o extrator de atividades de conversa (`extract_activity_text`), a máquina de turnos (`get_last_conversation_turn`) e o construtor de contexto arquitetural (`AIContextBuilder`).

## 📂 Arquivos Alvos a Criar
1. `tests/test_auto_reply.py`
2. `tests/test_ai_context_builder.py`

## 📋 Cenários de Teste Obrigatórios
1. **`tests/test_auto_reply.py`:**
   - Testar `extract_activity_text` com payload no formato `agentMessaged` (dict com `agentMessage`, `text` ou `message`).
   - Testar `extract_activity_text` com payload no formato `userMessaged` (dict com `userMessage`).
   - Testar `extract_activity_text` com formato de string direta.
   - Testar `extract_activity_text` com payload sem mensagem (retornando string vazia).
   - Testar `get_last_conversation_turn`:
     - Retorna `is_awaiting_user_action=True` se última mensagem for do agente.
     - Retorna `is_awaiting_user_action=False` se última mensagem for do usuário.
     - Detecta `has_unapproved_plan=True` quando houver plano em `PENDING_USER_APPROVAL`.

2. **`tests/test_ai_context_builder.py`:**
   - Testar `_determine_file_layer` para schemas (`db/schema.ts` -> `1_database_schemas`).
   - Testar `_determine_file_layer` para repositórios (`users.repository.ts` -> `2_repositories`).
   - Testar `_determine_file_layer` para serviços (`order.service.ts` -> `3_services`).
   - Testar `_determine_file_layer` para controllers (`auth.controller.ts` -> `4_controllers`).
   - Testar `_determine_file_layer` para routers (`api/routes/users.ts` -> `5_routers_api`).
   - Testar `_determine_file_layer` para páginas web (`apps/web/pages/Dashboard.tsx` -> `8_frontend_pages`).
   - Testar que chamadas consecutivas de `classify_and_order_files` não sofrem poluição de estado graças ao isolamento com `copy.deepcopy`.

3. **Validação:**
   - Todos os testes devem rodar e passar com o comando `pytest`.
