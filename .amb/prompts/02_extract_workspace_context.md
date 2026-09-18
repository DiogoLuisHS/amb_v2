# 🎯 Task: Isolar Contexto do Projeto Consumidor em `amb_cli/workspace/`

## 📌 Contexto & Responsabilidade Única (SRP)
O AMB_V2 opera em repositórios de projetos clientes/consumidores (target workspaces).
Atualmente, as funções de localização do repositório, leitura de `.amb/amb_project.json`, identificação do nome do repositório GitHub e dispositivo alvo de prototipagem estão misturadas em `amb_cli/config/config.py`.
Sua missão é **isolar toda a gestão de contexto do repositório consumidor** no novo pacote `amb_cli/workspace/`.

---

## 🛠️ Arquivos Alvo & Alterações Necessárias

### 1. Criar novo pacote `amb_cli/workspace/`
Crie o diretório `amb_cli/workspace/` contendo:

- `amb_cli/workspace/__init__.py`:
  Reexporta de `project_context.py`:
  - `find_repo_root`
  - `load_project_json`
  - `get_project_metadata`
  - `get_repo_name`
  - `get_device_type`

- `amb_cli/workspace/project_context.py`:
  Mova e refine as funções de contexto de repositório:
  - `find_repo_root(start_dir: Optional[str] = None) -> str`: Localiza a raiz do repositório cliente (.git, .amb, .env, package.json, pyproject.toml, requirements.txt).
  - `load_project_json(repo_root: Optional[str] = None) -> dict`: Carrega o arquivo `.amb/amb_project.json` (com fallback defensivo).
  - `get_project_metadata() -> dict`: Retorna metadata em cache com suporte a reload se necessário.
  - `get_repo_name() -> str`: Obtém o nome do repositório do projeto consumidor (via GITHUB_REPOSITORY do .env ou do amb_project.json).
  - `get_device_type(default: Optional[str] = None) -> Optional[str]`: Obtém o dispositivo configurado para Stitch no projeto consumidor (DESKTOP, MOBILE, TABLET, AGNOSTIC).

### 2. Atualizar Bootstrap do AMB
- Em `amb_cli/core/bootstrap.py`, adicione `"workspace"` e `"workspace/project_context"` à lista `CANONICAL_SUBMODULES` para disponibilizar no `sys.path`.

### 3. Camada de Compatibilidade Reversa (Facade)
- Em `amb_cli/config/config.py`, substitua as implementações originais de `find_repo_root`, `load_project_json`, `get_repo_name` e `get_device_type` por importações e reexportações a partir de `amb_cli.workspace.project_context`.
- Em `amb_cli/config/__init__.py`, garanta que os símbolos continuem sendo exportados normalmente.

---

## 🛡️ Diretrizes e Regras Mandatórias
1. **Preservação de Comportamento**: Todos os caminhos de busca de `find_repo_root` e prioridades de fallback de `load_project_json` devem ser estritamente preservados.
2. **Tipagem e Imports**: Use anotações de tipo completas e trate `repo_root` opcional defensivamente.
3. **Validação de QA Local**:
   ```bash
   pytest tests/test_config.py
   python -m py_compile amb_cli/workspace/*.py
   ```
