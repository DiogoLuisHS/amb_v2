# 🎯 Task: Realocar RulesManager e Design Tokens para `amb_cli/workspace/`

## 📌 Contexto & Responsabilidade Única (SRP)
O gerenciamento de regras arquiteturais do repositório (`rules_manager.py`) e a extração de tokens visuais do projeto consumidor (`design_tokens.py` que lê `design.md`, cores e fontes) são propriedades estritas do **Workspace do Consumidor**.
Sua missão é migrar esses componentes para `amb_cli/workspace/`, mantendo pontes de retrocompatibilidade em `amb_cli/config/`.

---

## 🛠️ Arquivos Alvo & Alterações Necessárias

### 1. Migrar para `amb_cli/workspace/`
- `amb_cli/workspace/rules_manager.py`:
  - Transfira a classe `RulesManager` e funções utilitárias `get_rules_manager()`, `load_project_rules()`.
  - Garanta que a busca de diretórios de regras continue cobrindo `.antigravity/rules`, `.gemini/rules`, `.agents/rules`, `rules/`, `AGENTS.md`, `GEMINI.md`.
  - Importe `find_repo_root` diretamente de `amb_cli.workspace.project_context` e `Colors`, `log` de `amb_cli.core.logger`.

- `amb_cli/workspace/design_tokens.py`:
  - Transfira as funções `parse_design_tokens_from_text(text)` e `get_design_system_config(default_file)`.
  - Importe `find_repo_root`, `load_project_json` de `amb_cli.workspace.project_context` e `get_env` de `amb_cli.core.env`.

- Atualize `amb_cli/workspace/__init__.py` para reexportar:
  - `RulesManager`, `get_rules_manager`, `load_project_rules`
  - `parse_design_tokens_from_text`, `get_design_system_config`

### 2. Camada de Compatibilidade Reversa (Facade)
- `amb_cli/config/rules_manager.py`:
  Substitua o conteúdo por uma fachada limpa que importa e reexporta `RulesManager`, `get_rules_manager` e `load_project_rules` de `amb_cli.workspace.rules_manager`.
- `amb_cli/config/config_core/design_tokens.py`:
  Substitua o conteúdo por uma fachada limpa que reexporta `parse_design_tokens_from_text` e `get_design_system_config` de `amb_cli.workspace.design_tokens`.
- `amb_cli/config/config.py`:
  Delegue `parse_design_tokens_from_text` e `get_design_system_config` para `amb_cli.workspace.design_tokens`.

---

## 🛡️ Diretrizes e Regras Mandatórias
1. **Zero Quebra de Contratos**: Nenhum dos 20+ testes em `test_rules_manager.py` ou `test_config.py` pode falhar.
2. **Preservação de Fences Markdown**: O algoritmo de fechamento de blocos de código não finalizados em `rules_manager.py` deve ser preservado integralmente.
3. **Validação de QA Local**:
   ```bash
   pytest tests/test_rules_manager.py tests/test_config.py
   python -m py_compile amb_cli/workspace/*.py
   ```

---

## 🚀 Ação Final Obrigatória: Commit e Abertura do Pull Request
Ao concluir as alterações e validar os testes locais com 100% de sucesso:
1. Você DEVE commitar todos os novos arquivos e os arquivos modificados.
2. Você DEVE submeter formalmente o Pull Request no GitHub para que o pipeline do AMB realize a validação de QA e o auto-merge na branch `main`.

