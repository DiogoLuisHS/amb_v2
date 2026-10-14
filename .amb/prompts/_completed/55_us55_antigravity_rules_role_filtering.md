# US-55: Filtragem de Regras Arquiteturais por Papel em amb agy rules (--role)

## 📌 Contexto e Objetivo
O framework AMB_V2 possui um mecanismo em [`RulesManager`](file:///c:/Users/DiogoHungaro/Desktop/Script/amb_v2/amb_cli/workspace/rules_manager.py) capaz de filtrar regras arquiteturais com base no papel da persona de IA (ex: `frontend`, `backend`, `qa`, `security`).
No entanto, na CLI pública, o comando `amb agy rules` lista todas as regras do repositório de forma monolítica, sem permitir ao desenvolvedor auditar ou inspecionar quais regras serão efetivamente aplicadas a um agente específico.

Esta US conecta o recurso existente à CLI:
```bash
amb agy rules --role frontend
# ou alias:
amb agy rules -r backend
```
Exibindo apenas o subconjunto priorizado de regras associado àquela especialidade de engenharia.

---

## 📐 Requisitos Técnicos

### 1. Atualização do Parser CLI
- **Arquivo (`amb_cli/cli_modules/cli_parsers.py`):**
  - No subparser `rules` do Antigravity:
    - Adicionar a flag `--role` / `-r`:
      ```python
      a.add_argument("--role", "-r", help="Filtra e prioriza regras relevantes para uma especialidade (ex: frontend, backend, qa, security).")
      ```

### 2. Atualização do Handler
- **Arquivo (`amb_cli/cli_modules/handlers_core/antigravity_handler.py`):**
  - No bloco `sub == "rules"`:
    - Obter `role = getattr(args, "role", None)`.
    - Se `role`:
      - Filtrar a lista utilizando `mgr.filter_rules_for_agent(role, rules=rules_list)`.
    - No modo `--content`, consolidar apenas as regras filtradas pela especialidade.
    - Suportar a flag `--json` retornando a estrutura filtrada.

---

## 🧪 Critérios de Aceite
1. **Suíte de Testes Unitários:**
   - Criar `tests/test_antigravity_rules_role.py` cobrindo:
     - `amb agy rules` sem flag listando todas as regras (comportamento padrão).
     - `amb agy rules --role frontend` retornando apenas regras aplicáveis a frontend.
     - `amb agy rules --role backend --content` consolidando o texto apenas das regras de backend.
     - Suporte a `--json` com a lista filtrada.
2. **Qualidade de Código:**
   - 100% dos testes passando (`pytest -q`).
   - Teto rígido de 300 linhas por arquivo (Regra 02).
   - Tipagem estrita com `typing` (Regra 04).
