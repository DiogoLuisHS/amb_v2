import typing

class SetupSanitizer:
    """Audita e sanitiza scripts de setup contra processos bloqueantes."""

    BLOCKED_COMMANDS = [
        "npm run dev",
        "npm start",
        "yarn dev",
        "yarn start",
        "pnpm dev",
        "flask run",
        "uvicorn",
        "manage.py runserver",
        "nodemon",
        "vite",
        "next dev",
        "http.server"
    ]

    @staticmethod
    def sanitize_script(script_text: str) -> typing.Tuple[str, typing.List[str]]:
        """
        Analisa o script linha por linha, removendo comandos bloqueantes.
        Retorna o script sanitizado e a lista de comandos removidos.
        """
        if not script_text:
            return "", []

        lines = script_text.splitlines()
        sanitized_lines = []
        removed_commands = []

        for line in lines:
            stripped = line.strip()
            if not stripped:
                sanitized_lines.append(line)
                continue

            # Check if any blocked command is in the current line
            is_blocked = False
            for blocked_cmd in SetupSanitizer.BLOCKED_COMMANDS:
                if blocked_cmd in stripped:
                    is_blocked = True
                    removed_commands.append(stripped)
                    break

            if not is_blocked:
                sanitized_lines.append(line)

        return "\n".join(sanitized_lines), removed_commands

    @staticmethod
    def has_blocking_commands(script_text: str) -> bool:
        """Verifica se há algum comando bloqueante no script."""
        _, removed = SetupSanitizer.sanitize_script(script_text)
        return len(removed) > 0
