import os
from pathlib import Path
from typing import Optional

from core.exceptions import AmbError

class WorkflowGenerator:
    """
    Gerador de Automação CI/CD para Tarefas Agendadas no GitHub Actions.
    """

    @staticmethod
    def generate_scheduled_workflow(
        cron_expression: str = "0 3 * * *",
        roles: Optional[list[str]] = None,
        output_path: Optional[Path] = None
    ) -> Path:
        """
        Gera um arquivo de workflow YAML para manutenção agendada.
        """
        # Validate cron expression
        parts = cron_expression.strip().split()
        if len(parts) != 5:
            raise AmbError(
                f"Expressão cron inválida: '{cron_expression}'.",
                hint="Forneça uma expressão cron de 5 campos (ex: '0 3 * * *')."
            )

        if output_path is None:
            # Default output path relative to the current working directory
            output_path = Path(".github/workflows/amb-scheduled-tasks.yml")

        # Ensure parent directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Build job steps
        steps = [
            "      - name: Checkout Repository",
            "        uses: actions/checkout@v4",
            "",
            "      - name: Set up Python 3.12",
            "        uses: actions/setup-python@v5",
            "        with:",
            "          python-version: '3.12'",
            "",
            "      - name: Install AMB CLI",
            "        run: pip install -e .",
            "",
            "      - name: Run AMB Validate",
            "        env:",
            "          JULES_API_KEY: ${{ secrets.JULES_API_KEY }}",
            "          GEMINI_API_KEY: ${{ secrets.GEMINI_API_KEY }}",
            "          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}",
            "        run: python -m amb_cli.cli validate"
        ]

        if roles:
            for role in roles:
                steps.extend([
                    "",
                    f"      - name: Run AMB Agent ({role})",
                    "        env:",
                    "          JULES_API_KEY: ${{ secrets.JULES_API_KEY }}",
                    "          GEMINI_API_KEY: ${{ secrets.GEMINI_API_KEY }}",
                    "          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}",
                    f"        run: python -m amb_cli.cli agent --role {role}"
                ])

        steps_str = "\n".join(steps)

        yaml_content = f"""name: AMB Scheduled Maintenance

on:
  schedule:
    - cron: '{cron_expression}'
  workflow_dispatch:

permissions:
  contents: write
  pull-requests: write
  issues: write

jobs:
  amb-maintenance:
    runs-on: ubuntu-latest
    steps:
{steps_str}
"""

        with open(output_path, "w", encoding="utf-8", errors="replace") as f:
            f.write(yaml_content)

        return output_path
