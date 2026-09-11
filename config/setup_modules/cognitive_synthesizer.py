import subprocess
from typing import Dict, Any
from config import get_env


class CognitiveSynthesizer:
    """Usa o Antigravity SDK ou Gemini para resumir regras e especificações do projeto."""

    @staticmethod
    def infer_project_specs(root: str, stack: Dict[str, Any]) -> str:
        """Gera um resumo técnico conciso das diretrizes do projeto."""
        gemini_key = get_env("GEMINI_API_KEY")
        if not gemini_key:
            return "Stack identificada: " + ", ".join(stack.get("frameworks", []))

        prompt = f"""Analise este resumo técnico de um projeto de software e gere 3 diretrizes essenciais de desenvolvimento em 1 parágrafo:
- Tipo: {stack.get("type")}
- Gerenciador: {stack.get("package_manager")}
- Frameworks: {", ".join(stack.get("frameworks", [])) or "Genérico"}
- Render Deploy: {"Sim" if stack.get("has_render_yaml") else "Não"}
"""
        try:
            res = subprocess.run(
                ["agy", "-p", prompt],
                cwd=root,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=20,
                check=False,
            )
            if res.returncode == 0 and res.stdout.strip():
                return res.stdout.strip()
        except Exception:
            pass

        return f"Projeto {stack.get('type')} com {', '.join(stack.get('frameworks', [])) or 'stack padrão'} utilizando {stack.get('package_manager')}."
