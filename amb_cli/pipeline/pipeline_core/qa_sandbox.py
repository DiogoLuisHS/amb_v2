import os
import re
from datetime import datetime
from typing import Optional

from workspace import find_repo_root

class LocalQASandbox:
    """
    Sandbox para salvar logs de execução do QA de forma isolada,
    para que os agentes possam analisar o erro sem limite de contexto e para
    permitir que as falhas sejam sanitizadas.
    """

    @classmethod
    def get_logs_dir(cls, repo_root: Optional[str] = None) -> str:
        """Retorna e garante a existência do diretório `.amb/logs/qa/`."""
        root = os.path.abspath(repo_root or find_repo_root())
        logs_dir = os.path.join(root, ".amb", "logs", "qa")
        os.makedirs(logs_dir, exist_ok=True)
        return logs_dir

    @classmethod
    def save_run_log(cls, command: str, output: str, success: bool, repo_root: Optional[str] = None) -> str:
        """
        Salva a saída completa de um comando em `.amb/logs/qa/qa_<timestamp>.log`.
        """
        logs_dir = cls.get_logs_dir(repo_root)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        status_str = "SUCCESS" if success else "FAILED"
        filename = f"qa_{timestamp}.log"
        filepath = os.path.join(logs_dir, filename)

        header = f"Command: {command}\nStatus: {status_str}\nTimestamp: {datetime.now().isoformat()}\n"
        separator = "=" * 80 + "\n"

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(header)
            f.write(separator)
            f.write(output)
            f.write("\n" + separator)

        return filepath

    @classmethod
    def extract_sanitized_failure(cls, output: str, max_lines: int = 30) -> str:
        """
        Filtra o ruído de um log grande e retorna as linhas mais essenciais do erro/stacktrace
        (linhas com "Error", "FAIL", "Traceback", etc.), otimizadas para envio a agentes cognitivos.
        """
        if not output:
            return ""

        lines = output.splitlines()
        if len(lines) <= max_lines:
            return output

        # Palavras-chave que indicam o centro do problema
        keywords = ["error", "fail", "traceback", "exception", "failed", "fatal"]

        important_lines = []
        for i, line in enumerate(lines):
            line_lower = line.lower()
            if any(kw in line_lower for kw in keywords):
                # Guarda o índice para capturarmos um bloco de contexto
                important_lines.append(i)

        if not important_lines:
            # Se não achou nenhuma keyword, retorna o final do log (geralmente onde fica o sumário de falha)
            return "\n".join(lines[-max_lines:])

        # Coleta as linhas de contexto ao redor das importantes
        selected_indices = set()
        for idx in important_lines:
            # 2 linhas antes, e 5 linhas depois do ponto de erro costumam ser úteis
            for j in range(max(0, idx - 2), min(len(lines), idx + 6)):
                selected_indices.add(j)

        sorted_indices = sorted(list(selected_indices))

        # Se mesmo com filtro passou do max_lines, nós limitamos o final da lista filtrada,
        # ou retornamos apenas as linhas exatas de keyword, até estourar.
        if len(sorted_indices) > max_lines:
            # Tenta pegar apenas do meio para o final, onde geralmente está o erro mais relevante (ex: sumário)
            sorted_indices = sorted_indices[-max_lines:]

        result_lines = []
        last_idx = -2
        for idx in sorted_indices:
            if idx > last_idx + 1 and last_idx != -2:
                result_lines.append("... [snip] ...")
            result_lines.append(lines[idx])
            last_idx = idx

        return "\n".join(result_lines)
