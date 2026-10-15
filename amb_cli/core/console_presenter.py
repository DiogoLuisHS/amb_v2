import json
import os
import sys
from typing import Any, Dict, List, Optional

from core.logger import Colors, log, log_error

class ConsolePresenter:
    """
    Camada de apresentação universal para suporte padronizado a saídas
    em modo texto (default), JSON (`--json`) ou silencioso (`--quiet`).
    """

    def __init__(self, json_mode: bool = False, quiet_mode: bool = False):
        self.json_mode = json_mode
        self.quiet_mode = quiet_mode

        # Fallback para variáveis de ambiente se as flags não forem passadas explicitamente
        if not self.json_mode:
            self.json_mode = os.environ.get("AMB_JSON_MODE", "false").lower() == "true"
        if not self.quiet_mode:
            self.quiet_mode = os.environ.get("AMB_QUIET_MODE", "false").lower() == "true"

    def print_message(self, message: str, color: str = Colors.RESET, bold: bool = False, tag: Optional[str] = None) -> None:
        """
        Imprime uma mensagem normal. Se json_mode=True, ignora (mensagens só saem em JSON estruturado via present_data).
        Se quiet_mode=True, também ignora (exceto se for erro crasso, mas para isso tem o print_error).
        """
        if self.json_mode or self.quiet_mode:
            return

        text = message
        if bold:
            text = f"{Colors.BOLD}{text}{Colors.RESET}"
        if color != Colors.RESET:
            text = f"{color}{text}{Colors.RESET}"

        if tag:
            log(tag, text, color)
        else:
            print(text, flush=True)

    def print_table(self, headers: List[str], rows: List[List[str]]) -> None:
        """
        Imprime uma tabela. Em json_mode ou quiet_mode, ignora silenciosamente.
        """
        if self.json_mode or self.quiet_mode:
            return

        if not headers or not rows:
            return

        # Calcula larguras
        col_widths = [len(str(h)) for h in headers]
        for row in rows:
            for i, cell in enumerate(row):
                if i < len(col_widths):
                    col_widths[i] = max(col_widths[i], len(str(cell)))

        # Formata
        header_row = " | ".join(str(h).ljust(w) for h, w in zip(headers, col_widths))
        separator = "-+-".join("-" * w for w in col_widths)

        print(header_row)
        print(separator)
        for row in rows:
            print(" | ".join(str(cell).ljust(w) for cell, w in zip(row, col_widths)))
        print()

    def print_json(self, data: Any) -> None:
        """
        Força a impressão de um objeto em JSON, independente das flags.
        """
        try:
            print(json.dumps(data, indent=2, ensure_ascii=False), flush=True)
        except TypeError:
            print(json.dumps({"error": "Unserializable data"}, indent=2), flush=True)

    def print_error(self, message: str, hint: Optional[str] = None) -> None:
        """
        Imprime erros. Em json_mode, emite um JSON com {"status": "error", "message": message}.
        Em quiet_mode normal, o erro AINDA deve ser impresso no stderr para indicar falha,
        salvo se implementarmos um strict quiet mode. Aqui manteremos o stderr.
        """
        if self.json_mode:
            err_obj = {"status": "error", "message": message}
            if hint:
                err_obj["hint"] = hint
            self.print_json(err_obj)
            return

        log_error("ERRO", message, hint)

    def present_data(self, data: Dict[str, Any]) -> None:
        """
        O método principal que agentes e scripts devem usar para receber dados de volta.
        Se json_mode=True, vai despejar `data` em formato JSON e finalizar a apresentação.
        Se quiet_mode=True e json_mode=False, não imprime nada (apenas retorna status code, o caller lida com exit).
        """
        if self.json_mode:
            self.print_json(data)
            return

        if self.quiet_mode:
            return

        # Default de fallback caso quem chamou não lidou com a versão não-JSON
        self.print_message(f"Data: {data}", Colors.CYAN)

    def render_executive_summary(self, metrics: Dict[str, Any]) -> None:
        """
        Renderiza no terminal o quadro executivo de produtividade formatado.
        """
        if self.json_mode:
            self.print_json(metrics)
            return

        if self.quiet_mode:
            return

        total_time_str = f"{int(metrics.get('total_duration_seconds', 0) // 60)}m {int(metrics.get('total_duration_seconds', 0) % 60)}s"
        qa_color = Colors.GREEN if metrics.get('qa_success_rate', 0) == 100 else Colors.YELLOW

        summary = (
            f"\n{Colors.BOLD}===========================================================================\n"
            f"🏆 RESUMO EXECUTIVO DE ORQUESTRAÇÃO AMB_V2\n"
            f"==========================================================================={Colors.RESET}\n"
            f"  • Tarefas Executadas:    {metrics.get('total_items', 0)} prompts processados\n"
            f"  • Telas Stitch Geradas:  {metrics.get('total_stitch_screens', 0)} interfaces visuais\n"
            f"  • Sessões Jules Cloud:   {metrics.get('total_sessions', 0)} sessões completadas com sucesso\n"
            f"  • Pull Requests:         {metrics.get('total_prs_opened', 0)} PRs abertos | {metrics.get('total_prs_merged', 0)} PRs integrados via Auto-Merge\n"
            f"  • Validação de QA Local: {qa_color}{metrics.get('qa_success_rate', 0)}% verde (Passou em typecheck, build e tests){Colors.RESET}\n"
            f"  • Tempo Total de Rodada: {total_time_str}\n"
            f"{Colors.BOLD}==========================================================================={Colors.RESET}\n"
        )
        print(summary, flush=True)
