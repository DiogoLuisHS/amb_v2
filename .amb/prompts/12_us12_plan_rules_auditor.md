# US-12: Auditoria Automática de Planos do Jules contra as Regras do AGENTS.md

## 📌 Contexto e Objetivo
Quando o Google Jules gera um plano inicial de execução (`PLAN_GENERATED`), o AMB atualmente pode executar a auto-aprovação do plano. No entanto, o Jules por vezes elabora planos que omitem a criação de testes unitários ou planejam criar arquivos extensos que violam as regras canônicas de engenharia do repositório (ex: Regra 02: limite rígido de 300 linhas, Regra 04: tipagem estrita e testes).
Esta demanda introduz um auditor de planos pré-aprovação (`PlanAuditor`), permitindo que o AMB analise o plano do Jules e, se houver omissões críticas, envie feedback corretivo via chat antes de aprovar.

---

## 📐 Requisitos Técnicos

1. **Módulo Auditor de Planos (`amb_cli/integrations/jules/jules_core/plan_auditor.py`):**
   - Criar a classe `PlanAuditor`:
     - Método `audit_plan(plan_text: str) -> tuple[bool, str]`:
       - Avalia se o plano contempla testes unitários (palavras-chave como `test`, `tests`, `pytest`, `unit test`).
       - Avalia menções a modularização atômica e respeito ao limite de linhas (Regra 02).
       - Retorna `(is_compliant: bool, feedback: str)`.
       - Se o plano omitir testes ou regras críticas, gera mensagem de feedback concisa e profissional para ser enviada ao Jules via `client.send_message`.
       - Exemplo de feedback: *"Atenção às regras de engenharia do AGENTS.md: certifique-se de incluir a criação de testes unitários em pytest e garantir que nenhum arquivo ultrapasse o limite de 300 linhas."*

2. **Integração no Fluxo de Monitoramento (`SessionMonitor`):**
   - No `session_monitor.py` (ou manipulador de atividades do Jules):
     - Ao detectar plano aguardando aprovação (`PLAN_GENERATED` ou atividade com plano):
     - Se a auditoria de planos estiver ativa (ou por padrão no auto-approve):
       - Executa `PlanAuditor.audit_plan(...)`.
       - Se `is_compliant is False` e ainda não enviou feedback corretivo para este plano:
         - Envia a mensagem de feedback corretivo via `client.send_message(session_id, feedback)`.
         - Registra no log que o plano foi contestado para ajustes.
       - Se `is_compliant is True` (ou após a rodada de feedback):
         - Executa `client.approve_plan(session_id)`.

3. **Garantia de Não-Bloqueio (Circuit Breaker):**
   - Limitar a 1 tentativa de contestação por plano, para evitar loops infinitos caso o modelo não reescreva o plano. Na segunda passagem, aprova para dar andamento à execução.

---

## 🧪 Critérios de Aceite
1. **Suíte de Testes:**
   - Criar `tests/test_plan_auditor.py` validando:
     - Plano válido com etapas de desenvolvimento e testes retorna `(True, "")`.
     - Plano que omite testes retorna `(False, mensagem_de_feedback)`.
     - Integração de `PlanAuditor` com o fluxo do `SessionMonitor`.
2. **Qualidade de Código:**
   - 100% dos testes unitários passando (`pytest -q`).
   - Nenhum arquivo pode ultrapassar 300 linhas de código (Regra 02).
   - Tipagem estrita com `typing` (Regra 04).
   - Zero dependências externas novas.
