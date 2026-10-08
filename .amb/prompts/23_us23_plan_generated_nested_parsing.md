# US-23: Normalização de Parsing de Planos Aninhados (planGenerated) no Watcher

## 📌 Contexto e Objetivo
A documentação da API REST do Google Jules (`https://jules.google/docs/api/reference/activities`) estabelece o formato oficial do evento `planGenerated`:
```json
{
  "planGenerated": {
    "plan": {
      "id": "plan1",
      "steps": [
        {
          "id": "step1",
          "index": 0,
          "title": "Analyze existing code",
          "description": "Review the authentication module structure"
        }
      ],
      "createTime": "2024-01-15T10:31:00Z"
    }
  }
}
```

Observe que a lista de passos (`steps`) fica encapsulada dentro do objeto `planGenerated["plan"]["steps"]`. No AMB_V2, o watcher em `amb_cli/integrations/jules/jules_watcher.py` tenta extrair `steps` diretamente do nível superior de `act["planGenerated"]`, o que pode resultar em lista vazia se a API responder com o formato aninhado oficial.

Esta US padroniza a extração de planos gerados pelo agente, garantindo suporte tanto ao formato aninhado oficial quanto ao formato plano legado.

---

## 📐 Requisitos Técnicos

### 1. Extração Resiliente de Planos no Watcher
- **Arquivo (`amb_cli/integrations/jules/jules_watcher.py`):**
  - No bloco `if "planGenerated" in act:`:
    - Extrair `plan_data = act["planGenerated"]`.
    - Resolver o objeto interno: `actual_plan = plan_data.get("plan") if isinstance(plan_data, dict) and "plan" in plan_data else plan_data`.
    - Extrair `steps = actual_plan.get("steps", []) if isinstance(actual_plan, dict) else []`.
    - Ao iterar os passos para exibição no console:
      - Obter texto preferindo `step.get("title")` e se ausente `step.get("description")`. Se ambos existirem: `f"{title}: {description}"` ou a descrição concisa.
    - Manter o limite rígido de 300 linhas por arquivo (Regra 02).

---

## 🧪 Critérios de Aceite
1. **Suíte de Testes Unitários:**
   - Criar `tests/test_plan_generated_parsing.py` cobrindo:
     - Parsing de `planGenerated` no formato aninhado canônico (`{"plan": {"steps": [...]}}`).
     - Parsing de `planGenerated` no formato direto legado (`{"steps": [...]}`).
     - Extração correta dos títulos e descrições dos passos.
2. **Qualidade de Código e Limites Arquiteturais:**
   - 100% dos testes unitários passando (`pytest -q`).
   - Teto rígido de 300 linhas por arquivo (Regra 02).
   - Tipagem estrita com `typing` (Regra 04).
