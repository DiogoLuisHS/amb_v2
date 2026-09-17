# 🚀 Tarefa de Engenharia: Refatoração e Alinhamento Arquitetural de `amb_cli/agents/`

## 🎯 Objetivo Geral
Refatorar todos os módulos do diretório `amb_cli/agents/` para que estejam em 100% de conformidade com as regras de desenvolvimento do projeto definidas em `.agents/rules/`:
1. **Regra 01 (SRP):** Desacoplar apresentação/CLI de lógica de serviço. Todo arquivo deve ter docstring com "Responsabilidade Única".
2. **Regra 02 (Atomização para IA):** Manter arquivos granulares (100 a 250 linhas, teto máximo de 300 linhas). Decompor `autonomous_loop.py` (que possui 490 linhas) em submódulos atômicos dentro de `amb_cli/agents/loop_core/`.
3. **Regra 03 (DRY & Zero Redundância):** Proibido imports planos legados (`from jules_client import ...`); usar sempre imports absolutos canônicos do pacote (`from integrations.jules.jules_client import JulesClient`, `from agents.auto_reply import advise_and_reply`, etc.).
4. **Regra 04 (Qualidade e Tipagem):** Type Hints estritos em 100% das funções e métodos públicos (`typing`, `Path`), hierarquia `AmbError` e tratamento defensivo sem capturar exceções silenciosamente.
5. **Regra 05 (Documentação Concisa):** Eliminar banners decorativos gigantes (`# ======...`), remover imports não utilizados (código morto) e manter docstrings declarativas de 1 a 3 linhas.
6. **Regra 06 (Segurança e Testes):** Garantir que a suíte completa de testes (`pytest`) continue passando com 100% de sucesso (92/92 testes green).

---

## 📋 Detalhamento dos Módulos a Ajustar

### 1. `amb_cli/agents/monitor.py`
- Remover imports mortos: `os`, `sys`, `argparse`.
- Mover a chamada `from agents.auto_reply import advise_and_reply` para o topo do arquivo (proibido import tardio dentro do loop).
- Adicionar anotações de tipo de retorno em todas as funções/métodos: `run_monitor(...) -> None`, `UnifiedMonitor.run(...) -> None`, `main() -> None`.
- Atualizar cabeçalho para `Localização: amb_cli/agents/monitor.py`.
- Tratar exceções específicas com log limpo.

### 2. `amb_cli/agents/auto_reply.py`
- Remover todos os separadores e banners decorativos ASCII gigantes (`# =================...`) conforme a Regra 05.
- Atualizar cabeçalho para `Localização: amb_cli/agents/auto_reply.py`.
- Adicionar anotações explícitas de retorno (`-> None`, etc.) em `main()` e funções de despacho.

### 3. `amb_cli/agents/auto_reply_core/`
- `turn_extractor.py`:
  - Substituir anotações genéricas `activity: dict` e `acts: list` por `activity: Dict[str, Any]` e `acts: List[Dict[str, Any]]`.
  - Atualizar cabeçalho para `amb_cli/agents/auto_reply_core/turn_extractor.py`.
- `cognitive_advisor.py`:
  - Remover `import os` não utilizado e variável morta `return_content`.
  - Atualizar cabeçalho para `amb_cli/agents/auto_reply_core/cognitive_advisor.py`.
- `feedback_dispatcher.py`:
  - Garantir docstrings declarativas concisas e assinaturas tipadas.
  - Atualizar cabeçalho para `amb_cli/agents/auto_reply_core/feedback_dispatcher.py`.

### 4. `amb_cli/agents/local_agent_runner.py`
- Adicionar anotações de retorno em todas as funções (`-> None`, `-> int`, `-> Dict[str, Dict[str, str]]`).
- Atualizar cabeçalho para `amb_cli/agents/local_agent_runner.py`.
- Limpar docstrings e assegurar tratamento defensivo com `ApiExecutionError`.

### 5. `amb_cli/agents/autonomous_loop.py` (Decomposição Modular - Regra 02)
- O arquivo atual possui 490 linhas, violando a Regra 02. Decompô-lo criando o subpacote `amb_cli/agents/loop_core/`:
  - `amb_cli/agents/loop_core/__init__.py`
  - `amb_cli/agents/loop_core/session_assistant.py` (~120-140 linhas): Encapsular a lógica de `monitor_and_assist_session`, acompanhando a sessão, aprovando planos pendentes (`approve_plan`) e disparando o auto-reply (`advise_and_reply`).
  - `amb_cli/agents/loop_core/cycle_dispatcher.py` (~110-130 linhas): Encapsular `_build_ai_context` (enriquecimento com `AIContextBuilder`), `_dispatch_jules_session` (criação da sessão na API Jules) e `_handle_pr_merge` (aprovação e merge do PR no Git).
  - `amb_cli/agents/autonomous_loop.py`: Manter apenas a coordenação central dos ciclos (`run_autonomous_loop` e `load_persona_content`), reduzindo o arquivo para menos de 220 linhas!
- Corrigir todos os imports planos legados:
  - `from integrations.jules.jules_client import JulesClient`
  - `from integrations.git.git_service import GitService`
  - `from agents.auto_reply import advise_and_reply, get_last_conversation_turn`
  - `from agents.local_agent_runner import get_personas_directory, discover_personas`
  - `from integrations.jules.tools.merge_session_pr import approve_and_merge_pr`

---

## 🧪 Validação Obrigatória
Antes de abrir o Pull Request ou finalizar a tarefa:
1. Compile todos os arquivos modificados:
   `python -m py_compile amb_cli/agents/*.py amb_cli/agents/loop_core/*.py amb_cli/agents/auto_reply_core/*.py`
2. Execute a suíte completa de testes:
   `pytest`
3. Todos os 92 testes unitários existentes DEVEM passar (100% green).
