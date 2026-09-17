# Task: Refactor and Atomize `amb_cli/integrations/antigravity/antigravity_client.py` (Rule 02 & Rule 01)

## Context and Goal
`amb_cli/integrations/antigravity/antigravity_client.py` currently has 324 lines, exceeding our hard architectural limit of 300 lines (Rule 02). It combines local CLI subprocess execution, direct Google Gemini REST invocation, architectural validation, and prompt synthesis in a single file.
The goal is to refactor `antigravity_client.py` down to strictly **less than 240 lines**, extracting backend helpers into `amb_cli/integrations/antigravity/antigravity_core/`, while preserving 100% backward compatibility with existing tests in `tests/test_antigravity_integration.py`.

---

## Architectural Requirements

1. **Rule 01 (SRP) & Rule 02 (Atomicity <= 300 lines):**
   - Create package `amb_cli/integrations/antigravity/antigravity_core/`:
     - `amb_cli/integrations/antigravity/antigravity_core/__init__.py`
     - `amb_cli/integrations/antigravity/antigravity_core/gemini_backend.py`:
       - Encapsulate the direct REST Gemini payload formatting and HTTP execution (`_generate_via_gemini_api`).
   - In `amb_cli/integrations/antigravity/antigravity_client.py`:
     - Keep under 240 lines.
     - Maintain public class `AntigravityClient`:
       - `__init__(self, model: Optional[str] = None)`
       - `generate_content(self, prompt: str, system_instruction: Optional[str] = None, json_mode: bool = False) -> str`
       - `synthesize_prompt(self, base_prompt: str, task_type: str = "feature", rules_dir: Optional[str] = None, include_context: bool = True) -> str`
       - `validate_architecture(self, file_paths: Optional[List[str]] = None, rules_dir: Optional[str] = None) -> Dict[str, Any]`

2. **Rule 03 (Canonical Imports & Backward Compatibility):**
   - Must remain 100% compatible with existing imports:
     `from integrations.antigravity.antigravity_client import AntigravityClient` and `from amb_cli.integrations.antigravity.antigravity_client import AntigravityClient`.

3. **Rule 04 & Rule 05 (Type Annotations & Clean Docstrings):**
   - Strict typing across all methods (`Optional[str]`, `Dict[str, Any]`, `List[str]`, etc.).
   - Clean docstrings without ASCII banners.

4. **Rule 06 (Green Tests):**
   - Run `pytest tests/test_antigravity_integration.py` and full suite `pytest`.
   - Ensure all 12+ Antigravity tests pass without regression.
