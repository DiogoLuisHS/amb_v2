import json
from typing import Any
from core.logger import Colors
from core.local_telemetry import LocalTelemetry

def handle_cmd_stats(args: Any) -> None:
    """Handler for the 'amb stats' command."""
    metrics = LocalTelemetry.get_summary_metrics()

    if getattr(args, "json", False):
        print(json.dumps(metrics, indent=2))
        return

    # Formatted terminal output
    print(f"\n{Colors.BOLD}{Colors.CYAN}📊 AMB_V2 - Local Telemetry & Stats{Colors.RESET}")
    print(f"{Colors.BLUE}{'=' * 40}{Colors.RESET}")

    print(f"{Colors.BOLD}Total Sessions Run:{Colors.RESET}       {Colors.GREEN}{metrics['total_sessions']}{Colors.RESET}")
    print(f"{Colors.BOLD}QA Success Rate:{Colors.RESET}          {Colors.GREEN}{metrics['qa_success_rate']}%{Colors.RESET}")
    print(f"{Colors.BOLD}Total PRs Integrated:{Colors.RESET}     {Colors.GREEN}{metrics['total_prs']}{Colors.RESET}")
    print(f"{Colors.BOLD}Avg Cycle Duration:{Colors.RESET}       {Colors.GREEN}{metrics['avg_duration_seconds']}s{Colors.RESET}")

    print(f"{Colors.BLUE}{'=' * 40}{Colors.RESET}\n")
