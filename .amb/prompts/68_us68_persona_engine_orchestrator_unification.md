# US-68: Unificação da PersonaEngine nos Orquestradores (DRY)

## 📌 Contexto e Objetivo
Atualmente, tanto o executor local de personas ([`local_agent_runner.py`](file:///c:/Users/DiogoHungaro/Desktop/Script/amb_v2/amb_cli/agents/local_agent_runner.py)) quanto o orquestrador do loop autônomo ([`autonomous_loop.py`](file:///c:/Users/DiogoHungaro/Desktop/Script/amb_v2/amb_cli/agents/autonomous_loop.py)) mantêm implementações próprias e duplicadas para localizar, ler e listar personas da pasta `.amb/personas/` (`discover_personas`, `load_persona_content`, `get_personas_directory`).
Além de duplicar mais de 100 linhas de código, essas rotinas legadas não utilizam a [`PersonaEngine`](file:///c:/Users/DiogoHungaro/Desktop/Script/amb_v2/amb_cli/agents/persona_engine.py), deixando de interpolar variáveis dinâmicas do projeto (`{repo_name}`, `{stack}`, `{qa_command}`) e ignorando validações arquiteturais.

Esta US unifica o motor de personas de ponta a ponta:
1. **Fonte Única da Verdade:** `PersonaEngine` passa a ser o único componente responsável por descobrir, validar, interpolar e fornecer personas para todos os executores e orquestradores.
2. **Eliminação de Código Duplicado:** Remove as rotinas duplicadas em `local_agent_runner.py` e `autonomous_loop.py`, substituindo por chamadas diretas a `PersonaEngine`.
3. **Interpolação Universal:** Todas as personas despachadas para o Jules ou Antigravity recebem o contexto do projeto resolvido dinamicamente.

---

## 📐 Requisitos Técnicos

### 1. Atualização do Autonomous Loop
- **Arquivo (`amb_cli/agents/autonomous_loop.py`):**
  - Substituir importações legadas de `local_agent_runner` por `from amb_cli.agents.persona_engine import PersonaEngine`.
  - Instanciar `engine = PersonaEngine(repo_root=repo_root)`.
  - Na resolução da fila de itens e no carregamento de personas (`load_persona_content`):
    - Utilizar `engine.load_persona(role)` e `engine.render_persona_template(content)`.
  - Manter o limite rígido de 300 linhas por arquivo (Regra 02).

### 2. Atualização do Local Agent Runner
- **Arquivo (`amb_cli/agents/local_agent_runner.py`):**
  - Refatorar `discover_personas`, `get_personas_directory` e `list_personas` para delegar para `PersonaEngine`.
  - Garantir que `execute_single_persona` utilize `engine.render_persona_template` no conteúdo base.
  - Manter o limite rígido de 300 linhas por arquivo (Regra 02).

---

## 🧪 Critérios de Aceite
1. **Suíte de Testes Unitários:**
   - Criar `tests/test_persona_engine_orchestrator.py` cobrindo:
     - Execução do loop autônomo carregando persona interpolada dinamicamente via `PersonaEngine`.
     - Execução do runner local consumindo personas validadas pela `PersonaEngine`.
     - Eliminação de rotinas legadas duplicadas sem quebra de comportamento.
2. **Qualidade de Código:**
   - 100% dos testes passando (`pytest -q`).
   - Teto rígido de 300 linhas por arquivo (Regra 02).
   - Tipagem estrita com `typing` (Regra 04).
