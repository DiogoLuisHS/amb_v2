# 📐 Padrões e Diretrizes de Engenharia — AMB_V2

## 1. Arquitetura CLI Global
- O ponto de entrada unificado é o comando `amb` via [`cli.py`](cli.py).
- A CLI é instalada globalmente em modo editável (`pip install -e .`) e é agnóstica a projetos, detectando a raiz do repositório ativo com `find_repo_root()`.
- Projetos consumidores utilizam a pasta `.amb/` (com `amb_project.json`, `personas/` e `diarios/`).

## 2. Higiene de Repositório & Versionamento
- Nunca versionar arquivos em `__pycache__/`, `*.egg-info/`, `.env` ou artefatos temporários em `.amb/diarios/`.
- O [`.gitignore`](.gitignore) na raiz é mantido rigorosamente atualizado.

## 3. Princípio Fail-Fast & Tratamento de Erros
- Validações de chaves de API e variáveis mandatórias utilizam `require_env(key, hint=...)` lançando `ConfigurationError` com orientações claras de resolução.
- Não mascarar falhas de rede ou APIs com blocos `try/except` vazios.

