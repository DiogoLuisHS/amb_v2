# US-11: Gerador de Automação CI/CD para Tarefas Agendadas (amb workflow schedule)

## 📌 Contexto e Objetivo
Permitir que projetos configurem manutenções automáticas e auditorias recorrentes do Jules e do AMB no GitHub Actions. O desenvolvedor deve poder executar um comando na CLI (`amb workflow schedule` ou `amb jules workflow`) que gera automaticamente um arquivo de workflow em `.github/workflows/amb-scheduled-tasks.yml` com suporte a cron personalizável, execução manual (`workflow_dispatch`), setup do ambiente e injeção de segredos.

---

## 📐 Requisitos Técnicos

1. **Módulo de Geração de Workflows (`amb_cli/workspace/workflow_generator.py`):**
   - Criar a classe `WorkflowGenerator` com método estático ou de instância:
     `generate_scheduled_workflow(cron_expression: str = "0 3 * * *", roles: Optional[list[str]] = None, output_path: Optional[Path] = None) -> Path`
   - O arquivo gerado deve conter:
     - `name: AMB Scheduled Maintenance`
     - `on: schedule: - cron: '<cron_expression>'` e `workflow_dispatch:`
     - `permissions: contents: write, pull-requests: write, issues: write`
     - Job com setup do Python 3.12, instalação via `pip install -e .` e execução de `python -m amb_cli.cli validate` ou execução com o Jules.
     - Mapeamento das variáveis de ambiente: `JULES_API_KEY`, `GEMINI_API_KEY`, `GITHUB_TOKEN`.
   - Tratamento seguro de caminhos: criar o diretório pai `.github/workflows/` se não existir.
   - Escrita com `encoding="utf-8", errors="replace"`.

2. **Parser e Handler na CLI:**
   - Adicionar subcomando `workflow` no parser principal (`amb_cli/cli_modules/cli_parsers.py`) com comando `schedule`:
     - Flags:
       - `--cron`, `-c`: Expressão cron de agendamento (Padrão: `"0 3 * * *"` — diário às 03:00 UTC).
       - `--role`, `-r`: Persona opcional a ser executada (ex: `engineer`, `qa`).
       - `--output`, `-o`: Caminho customizado para salvar o arquivo yaml.
   - Criar handler `workflow_handler.py` em `amb_cli/cli_modules/handlers_core/` invocando o gerador e exibindo confirmação no console.

3. **Validação e Tratamento de Erros:**
   - Validar que a expressão cron tem formato básico de 5 campos (ou disparar `AmbError` com mensagem amigável e dica de resolução).
   - Se o arquivo já existir, sobrescrever de forma limpa informando o usuário.

---

## 🧪 Critérios de Aceite
1. **Suíte de Testes:** Criar `tests/test_workflow_generator.py` cobrindo:
   - Geração com parâmetros padrão (cron diário, caminho `.github/workflows/amb-scheduled-tasks.yml`).
   - Geração com cron customizado e persona específica.
   - Validação de erro para cron com campos inválidos.
   - Teste de invocação via CLI (`amb workflow schedule`).
2. **Qualidade de Código:**
   - 100% dos testes unitários passando (`pytest -q`).
   - Limite estrito de no máximo 300 linhas por arquivo (Regra 02).
   - Tipagem estrita com `typing` e exceções `AmbError` (Regra 04).
   - Zero dependências externas novas (usar standard library).
