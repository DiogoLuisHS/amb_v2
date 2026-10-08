# US-16: Repasse da Flag --require-approval em amb jules create

## 📌 Contexto e Objetivo
A documentação oficial da API do Google Jules (`https://jules.google/docs/api/reference/`) estabelece que por padrão as sessões criadas via API têm aprovação automática de plano, a menos que o campo `requirePlanApproval: true` seja explicitamente enviado no payload de criação.

No AMB_V2, o subcomando `amb jules create` possui a flag `--require-approval` declarada no parser (`cli_parsers.py`), e `run_create_session` suporta o argumento `require_plan_approval`. No entanto, o manipulador em `amb_cli/cli_modules/handlers_core/jules_handler.py` não está repassando esse argumento para a função `run_create_session`.

Esta US corrige essa lacuna, permitindo que o desenvolvedor crie sessões pausadas para aprovação de plano diretamente via CLI.

---

## 📐 Requisitos Técnicos

### 1. Repasse da Flag no Handler do Jules
- **Arquivo (`amb_cli/cli_modules/handlers_core/jules_handler.py`):**
  - No bloco `elif sub == "create":`, capturar o valor de `getattr(args, "require_approval", False)`.
  - Passar `require_plan_approval=True if getattr(args, "require_approval", False) else None` para `run_create_session`.
  - Manter o limite de 300 linhas estritamente respeitado.

### 2. Validação e Feedback Visual
- **Arquivo (`amb_cli/integrations/jules/tools/create_session.py`):**
  - Garantir que a mensagem no terminal confirme claramente quando a sessão for criada exigindo aprovação manual:
    `• Aprovação: Exige aprovação manual do plano de execução`.

---

## 🧪 Critérios de Aceite
1. **Suíte de Testes Unitários:**
   - Criar ou atualizar `tests/test_jules_create_approval.py` cobrindo:
     - Chamada de `handle_cmd_jules` com `args.require_approval = True` repassando corretamente para `run_create_session`.
     - Chamada sem a flag repassando `require_plan_approval=None`.
2. **Qualidade de Código e Limites Arquiteturais:**
   - 100% dos testes unitários passando (`pytest -q`).
   - Teto rígido de 300 linhas por arquivo (Regra 02).
   - Tipagem estrita com `typing` (Regra 04).
