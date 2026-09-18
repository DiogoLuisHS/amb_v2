# 📚 Catálogo de Prompts Atômicos: Desacoplamento de `amb_cli/config`

Este diretório contém os prompts modulares específicos para orientar o **Google Jules** no refatoramento, desacoplamento e auditoria contínua da separação entre **AMB Framework Core** e **Workspace do Consumidor**.

Cada prompt é 100% focado em um único domínio, garantindo economia de tokens, precisão de contexto cirúrgica e ausência de alucinações cognitivas.

---

## 📑 Sequência de Prompts do Ciclo

| # | Arquivo Prompt | Módulo Alvo | Responsabilidade Principal |
|---|---|---|---|
| **01** | [`01_extract_core_primitives.md`](./01_extract_core_primitives.md) | `amb_cli/core/` | Isola logging (`Colors`, `log`), exceções (`AmbError`), env do AMB e `bootstrap.py`. |
| **02** | [`02_extract_workspace_context.md`](./02_extract_workspace_context.md) | `amb_cli/workspace/` | Isola raiz de repo (`find_repo_root`), metadados `amb_project.json`, `repo_name` e `device_type`. |
| **03** | [`03_relocate_scaffolding_and_setup.md`](./03_relocate_scaffolding_and_setup.md) | `amb_cli/workspace/setup/` | Realoca `project_analyzer`, `amb_provisioner`, `cognitive_synthesizer` e `setup_project`. |
| **04** | [`04_relocate_rules_and_design_tokens.md`](./04_relocate_rules_and_design_tokens.md) | `amb_cli/workspace/` | Realoca `rules_manager.py` e `design_tokens.py` mantendo pontes na camada legada. |
| **05** | [`05_consolidate_config_facade_and_diagnostics.md`](./05_consolidate_config_facade_and_diagnostics.md) | `amb_cli/config/` | Transforma `config.py` em Facade limpa e atualiza diagnósticos visuais do `amb check`. |

---

## 🚀 Como Executar com o AMB Agent Loop

### Execução Autônoma Sequencial Completa
```bash
python amb_cli/cli.py agent --prompt .amb/prompts --loop --max-cycles 1
```

O orquestrador executará os 5 prompts em ordem numérica estrita:
1. Cria VM isolada no Google Jules para cada prompt.
2. Monitora os logs e responde dúvidas via Consultor Cognitivo Gemini (Auto-Advisor).
3. Executa a suíte de testes de QA localmente (`pytest`).
4. Realiza auto-merge do Pull Request e sincroniza a branch (`git pull origin main`).
5. Transiciona suavemente para o próximo prompt até concluir o ciclo.
