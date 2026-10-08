import os
import re
from typing import List, Dict, Any, Optional

from amb_cli.core import Colors, log, log_error
from amb_cli.workspace.project_context import find_repo_root, load_project_json

class PersonaEngine:
    """Engine unificada de personas com descoberta, interpolação e validação."""

    def __init__(self, repo_root: Optional[str] = None):
        self.repo_root = repo_root or find_repo_root()
        self.personas_dir = os.path.join(self.repo_root, ".amb", "personas")
        self.project_context = load_project_json(self.repo_root)

    def load_persona(self, name: str) -> Optional[str]:
        """
        Busca prioritariamente no diretório .amb/personas/ do projeto.
        Se não existir, recorre aos fallbacks.
        """
        if not name.endswith(".md"):
            name += ".md"

        filepath = os.path.join(self.personas_dir, name)
        if os.path.exists(filepath):
            with open(filepath, "r", encoding="utf-8", errors="replace") as f:
                return f.read()

        # Fallback para o diretório de agentes do próprio AMB
        amb_pkg_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".agents", "skills"))

        # Vamos assumir que as personas de fallback possam estar em .agents/skills ou .amb/prompts ou hardcoded
        # A issue pede: "recorrer aos fallbacks padrão de engenharia sem quebrar o fluxo".

        fallback_dir = os.path.join(amb_pkg_dir)
        # Se tentarmos encontrar nas skills
        if os.path.exists(fallback_dir):
            for skill_dir in os.listdir(fallback_dir):
                if name.replace(".md", "") in skill_dir:
                    skill_file = os.path.join(fallback_dir, skill_dir, "SKILL.md")
                    if os.path.exists(skill_file):
                        with open(skill_file, "r", encoding="utf-8") as f:
                            return f.read()

        # Se não encontrar nada, retorna None silenciosamente ou uma string genérica
        return None

    def render_persona_template(self, content: str, context_vars: Optional[Dict[str, Any]] = None) -> str:
        """Interpola valores a partir do contexto do projeto."""
        vars_to_interpolate = {
            "repo_name": os.path.basename(self.repo_root),
            "stack": self.project_context.get("stack", "unknown"),
            "qa_command": self.project_context.get("qa_command", "npm test")
        }

        if context_vars:
            vars_to_interpolate.update(context_vars)

        rendered_content = content
        for key, value in vars_to_interpolate.items():
            placeholder = "{" + key + "}"
            rendered_content = rendered_content.replace(placeholder, str(value))

        return rendered_content

    def validate_persona_file(self, filepath: str) -> List[str]:
        """
        Verifica se a persona possui:
        - Título/Missão (#)
        - Foco de Arquivos (## Arquivos)
        - Regras de Implementação (## Regras)
        Retorna lista de erros.
        """
        errors = []
        if not os.path.exists(filepath):
            errors.append(f"Arquivo não encontrado: {filepath}")
            return errors

        with open(filepath, "r", encoding="utf-8", errors="replace") as f:
            content = f.read()

        if not re.search(r"^#\s+.*", content, re.MULTILINE):
            errors.append("Falta a seção de Título/Missão (# Título)")

        if not re.search(r"^##\s+Arquivos.*", content, re.MULTILINE):
            errors.append("Falta a seção de Foco de Arquivos (## Arquivos)")

        if not re.search(r"^##\s+Regras.*", content, re.MULTILINE):
            errors.append("Falta a seção de Regras de Implementação (## Regras)")

        return errors
