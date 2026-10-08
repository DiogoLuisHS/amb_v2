import re
from typing import Tuple

class PlanAuditor:
    """Auditor of Jules execution plans against AGENTS.md rules."""

    @staticmethod
    def audit_plan(plan_text: str) -> Tuple[bool, str]:
        """
        Evaluates whether a plan contemplates unit tests and respects lines limits (Rule 02).
        Returns a boolean for compliance, and a feedback string if non-compliant.
        """
        text_lower = plan_text.lower()

        has_tests = any(keyword in text_lower for keyword in ["test", "tests", "pytest", "unit test"])

        has_300_lines_rule = "300" in text_lower

        if not has_tests or not has_300_lines_rule:
            return False, "Atenção às regras de engenharia do AGENTS.md: certifique-se de incluir a criação de testes unitários em pytest e garantir que nenhum arquivo ultrapasse o limite de 300 linhas."

        return True, ""
