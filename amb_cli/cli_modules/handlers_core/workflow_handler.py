from typing import Any
from pathlib import Path
from core import Colors, log
from workspace.workflow_generator import WorkflowGenerator

def handle_cmd_workflow(args: Any) -> None:
    """Roteia comandos do gerador de workflows (CI/CD)."""
    if getattr(args, "workflow_cmd") == "schedule":
        cron = getattr(args, "cron", "0 3 * * *")
        roles = getattr(args, "role", None)
        out_path = getattr(args, "output", None)

        output_path = None
        if out_path:
            output_path = Path(out_path)

        path_saved = WorkflowGenerator.generate_scheduled_workflow(
            cron_expression=cron,
            roles=roles,
            output_path=output_path
        )

        print(f"\n{Colors.GREEN}✅ Workflow agendado gerado com sucesso!{Colors.RESET}")
        print(f"📁 Salvo em: {Colors.CYAN}{path_saved}{Colors.RESET}\n")
    else:
        print(f"{Colors.RED}Subcomando workflow inválido ou não fornecido.{Colors.RESET}")
