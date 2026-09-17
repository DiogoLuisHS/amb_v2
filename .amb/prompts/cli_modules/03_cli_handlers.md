# 🎯 Tarefa Jules: Modularização e Refatoração de `amb_cli/cli_modules/cli_handlers.py`

## 📌 Arquivo Alvo
- **Caminho:** `amb_cli/cli_modules/cli_handlers.py`
- **Estado Atual:** 605 linhas (Violação grave da Regra 02: teto de 300 linhas).
- **Responsabilidade Única (SRP - Regra 01):** Despachar os comandos da CLI para os módulos e integrações correspondentes do sistema.

---

## 📐 Regras Arquiteturais Obrigatórias (`.agents/rules/`)
1. **Regra 01 (SRP):** Desacoplar os handlers de subcomandos densos em submódulos especializados (ex: `amb_cli/cli_modules/handlers_core/`).
2. **Regra 02 (Atomização para IA):** `amb_cli/cli_modules/cli_handlers.py` DEVE ter menos de 300 linhas (meta: ~200-240 linhas). Nenhum submódulo criado de suporte pode exceder 300 linhas.
3. **Regra 03 (DRY & Imports Canônicos):** Utilizar sempre imports canônicos com `ensure_amb_env()`. Proibido imports planos legados.
4. **Regra 04 (Tipagem Estrita):** Anotar todas as funções `cmd_*(args: Any) -> None` com type hints.
5. **Regra 05 (Documentação Concisa):** Proibido banners gigantes decorativos ASCII. Docstrings concisas de 1 a 3 linhas.
6. **Regra 06 (Segurança Git & Testes):** 100% de compatibilidade retroativa com os testes existentes ([`test_jules_integration.py`](file:///c:/Users/DiogoHungaro/Desktop/Script/amb_v2/tests/test_jules_integration.py), [`test_git_service.py`](file:///c:/Users/DiogoHungaro/Desktop/Script/amb_v2/tests/test_git_service.py), [`test_antigravity_integration.py`](file:///c:/Users/DiogoHungaro/Desktop/Script/amb_v2/tests/test_antigravity_integration.py)).

---

## 🛠️ Itens Específicos a Verificar / Refatorar
1. **Preservação Obrigatória de Todas as Assinaturas de `cmd_*`:**
   - As seguintes 16 funções DEVEM ser mantidas no namespace de `cli_handlers.py`:
     - `cmd_setup`
     - `cmd_prompt`
     - `cmd_check`
     - `cmd_monitor`
     - `cmd_advisor`
     - `cmd_gui`
     - `cmd_config`
     - `cmd_agent`
     - `cmd_jules`
     - `cmd_stitch`
     - `cmd_antigravity`
     - `cmd_validate`
     - `cmd_pipeline`
     - `cmd_schema`
     - `cmd_context`
     - `cmd_git`
2. **Modularização de Subcomandos Densos:**
   - Os subcomandos densos de integrações (`cmd_jules`, `cmd_stitch`, `cmd_antigravity`) totalizam mais de 350 linhas.
   - Crie submódulos em `amb_cli/cli_modules/handlers_core/` (ex: `jules_handler.py`, `stitch_handler.py`, `antigravity_handler.py`) para encapsular essa lógica.
   - Em `cli_handlers.py`, importe ou delegue para essas funções, reduzindo `cli_handlers.py` para menos de 250 linhas.
3. **Compatibilidade dos Testes:**
   - Em `tests/test_jules_integration.py`: `from cli_modules.cli_handlers import cmd_jules` é chamado diretamente com mocks. A interface deve permanecer idêntica.
   - Em `tests/test_git_service.py`: `from cli_modules.cli_handlers import cmd_git` é testado.
   - Em `tests/test_antigravity_integration.py`: `from cli_modules.cli_handlers import cmd_antigravity` é testado.

---

## 🧪 Validação Obrigatória
Antes de abrir o Pull Request:
```bash
python -m py_compile amb_cli/cli_modules/cli_handlers.py
python -m pytest tests/test_jules_integration.py
python -m pytest tests/test_git_service.py
python -m pytest tests/test_antigravity_integration.py
python -m pytest
```
Todos os testes unitários devem passar (100% green).

---

## 🚀 Ação Final Obrigatória: Abertura do Pull Request
Ao concluir todas as alterações e validar os testes com sucesso (100% green):
1. Você DEVE submeter/abrir o Pull Request no GitHub imediatamente.
2. Não encerre a sessão apenas no estado "Ready for submission"; confirme a criação do PR diretamente no GitHub com título e descrição claros das alterações.
