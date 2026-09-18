# 🎯 Task: Realocar Módulos de Setup e Scaffolding para `amb_cli/workspace/setup/`

## 📌 Contexto & Responsabilidade Única (SRP)
Os utilitários de inspeção de stack de repositório (`project_analyzer.py`), provisionamento da estrutura `.amb/` (`amb_provisioner.py`), geração de prompts cognitivos (`cognitive_synthesizer.py`) e orquestração do assistente (`setup_project.py`) residem atualmente dentro de `amb_cli/config/`.
Como pertencem diretamente ao domínio de integração e onboarding de projetos consumidores (Workspaces), devem ser realocados para `amb_cli/workspace/setup/`.

---

## 🛠️ Arquivos Alvo & Alterações Necessárias

### 1. Criar `amb_cli/workspace/setup/`
Copie/mova a lógica dos submódulos de setup para:
- `amb_cli/workspace/setup/__init__.py`:
  Reexporta:
  - `ProjectAnalyzer`
  - `AmbProvisioner`
  - `CognitiveSynthesizer`
  - `run_setup`
  - `print_setup_prompt`

- `amb_cli/workspace/setup/project_analyzer.py`:
  Detecta stack, linguagem primária, gerenciador de pacotes e infere comandos de QA (`pytest`, `npm test`, `vitest`, etc.).

- `amb_cli/workspace/setup/amb_provisioner.py`:
  Provisiona as pastas `.amb/personas/`, `.amb/diarios/`, `.amb/prompts/`, `.gitkeep`, persona de exemplo `engineer.md` e `.env.example`.

- `amb_cli/workspace/setup/cognitive_synthesizer.py`:
  Síntese cognitiva de personas e templates.

- `amb_cli/workspace/setup/setup_project.py`:
  Orquestrador CLI de `amb setup` (suporte a `--interactive`, `--auto`, `--dry-run`, `--force`).

### 2. Atualizar Bootstrap
- Em `amb_cli/core/bootstrap.py`, inclua `"workspace/setup"` em `CANONICAL_SUBMODULES`.

### 3. Criar Camada Facade em `amb_cli/config/`
Para garantir que chamadas legadas e testes existentes não quebrem:
- Em `amb_cli/config/setup_project.py`:
  Reexportar `run_setup` e `print_setup_prompt` a partir de `amb_cli.workspace.setup.setup_project`.
- Em `amb_cli/config/setup_modules/amb_provisioner.py`:
  Reexportar `AmbProvisioner` a partir de `amb_cli.workspace.setup.amb_provisioner`.
- Em `amb_cli/config/setup_modules/project_analyzer.py`:
  Reexportar `ProjectAnalyzer` a partir de `amb_cli.workspace.setup.project_analyzer`.
- Em `amb_cli/config/setup_modules/cognitive_synthesizer.py`:
  Reexportar a partir de `amb_cli.workspace.setup.cognitive_synthesizer`.

---

## 🛡️ Diretrizes e Regras Mandatórias
1. **Zero Regressão**: `tests/test_setup_and_analyzer.py` deve passar completamente tanto importando do caminho novo quanto dos caminhos legados em `config.setup_modules`.
2. **Compatibilidade com CLI**: O comando `amb setup --dry-run` deve executar com precisão.
3. **Validação de QA Local**:
   ```bash
   pytest tests/test_setup_and_analyzer.py
   python -m py_compile amb_cli/workspace/setup/*.py
   ```

