### 📅 [2026-09-02] Refatoração: cli.py
- **Alvo:** `cli.py`
- **Ação SRP:** Extraídos os handlers dos comandos para `cli_modules/cli_handlers.py` e a lógica do parser para `cli_modules/cli_parsers.py`. O arquivo `cli.py` foi simplificado para ser apenas um ponto de entrada (roteador delegando execução).
- **Melhoria DRY:** Removida a duplicação completa dos blocos argparse e functions `cmd_*`. Arquivo enxuto de mais de 500 para ~60 linhas.
- **Status de QA:** 0 erros de sintaxe/tipagem e testes validados (`pytest test_cli.py` passando e cli `--help` funcionando sem regressão).


### 📅 [2024-05-18] Refatoração: config/setup_project.py
- **Alvo:** `config/setup_project.py`
- **Ação SRP:** Extraídos submódulos `project_analyzer`, `amb_provisioner`, e `cognitive_synthesizer` para `config/setup_modules/`.
- **Melhoria DRY:** Classes monolíticas centralizadas e isoladas em módulos especializados.
- **Status de QA:** 0 erros de sintaxe/tipagem (Ruff check all pass) e contratos validados.

# 🧪 Pure Diário do Pure (`.amb/diarios/pure.md`)

Este diário consolida o histórico de aprendizados e padrões identificados no repositório DiogoLuisHS/amb_v2.

---

### 📅 [2026-09-11] Refatoração: architecture/ai_context_builder.py
- **Alvo:** `architecture/ai_context_builder.py`
- **Ação SRP:** Extraída a lógica condicional de classificação das camadas (`if-elif-else`) do método principal `classify_and_order_files` para um método helper privado `_determine_file_layer`. O dicionário base também foi extraído para um atributo estático de classe (`LAYERS_CONFIG`).
- **Melhoria DRY:** Removeu-se o boilerplate de dict duplicado e simplificou-se drasticamente o fluxo do laço `for` em `classify_and_order_files`, melhorando a legibilidade sem alterar o comportamento.
- **Status de QA:** 0 erros de sintaxe/tipagem (Ruff check all pass) e contratos validados sem alterar output final (`test_layer.py` mock verificado, `generate_context()` ok).

### 📅 [2024-09-02] Refatoração: cli.py (Limpeza Final)
- **Alvo:** `cli.py`
- **Ação SRP:** Utilizado o submódulo de parsing (`cli_modules/cli_parsers.py`) e apagada a redundância gigantesca de declarações `cmd_*` e inicialização de argumentos que ainda estava duplicada dentro de `cli.py`.
- **Melhoria DRY:** Reduziu o entrypoint `cli.py` de ~540 linhas para ~65 linhas, solidificando a responsabilidade única: rotear caminhos (sys.path) e capturar exceptions globais do parser principal.
- **Status de QA:** 0 erros de sintaxe/tipagem (Ruff com noqa aplicado) e suite pytest operando.

### 📅 [2024-09-02] Refatoração: cli.py
- **Alvo:** `cli.py`
- **Ação SRP:** Extraídos submódulos `cli_modules/cli_handlers.py` e `cli_modules/cli_parsers.py`.
- **Melhoria DRY:** Centralizadas declarações do argparse e os handlers `cmd_*` nos novos submódulos, deixando o `cli.py` com a responsabilidade apenas de carregar configurações globais, registrar paths e chamar `create_parser()`. Arquivo reduzido de 539 linhas para 64 linhas.
- **Status de QA:** 0 erros de sintaxe/tipagem. Validação com `amb check` e `cli.py --help` 100% verde.
