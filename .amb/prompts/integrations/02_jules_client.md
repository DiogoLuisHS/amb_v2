# Task: Refactor and Atomize `amb_cli/integrations/jules/jules_client.py` (Rule 02)

## Context and Goal
`amb_cli/integrations/jules/jules_client.py` is currently 310 lines, slightly exceeding our strict limit of 300 lines per file (Rule 02).
The goal is to streamline and refactor `amb_cli/integrations/jules/jules_client.py` to strictly **less than 250 lines**, preserving all existing API signatures and behavior, and ensuring all tests in `tests/test_jules_integration.py` pass with 100% success.

---

## Architectural Requirements

1. **Rule 01 (SRP) & Rule 02 (Atomicity <= 300 lines):**
   - Keep `amb_cli/integrations/jules/jules_client.py` under 250 lines.
   - Maintain the complete `JulesClient(BaseGoogleClient)` interface:
     - `normalize_session_id(session_id: str) -> str`
     - `list_sources(page_size: int = 50) -> List[Dict[str, Any]]`
     - `get_source(source_name: str) -> Dict[str, Any]`
     - `create_session(prompt: str, source_name: str, starting_branch: str = "main", title: Optional[str] = None, auto_pr_creation: bool = True) -> Dict[str, Any]`
     - `get_session(session_id: str) -> Dict[str, Any]`
     - `list_sessions(page_size: int = 20, page_token: Optional[str] = None) -> Dict[str, Any]`
     - `send_message(session_id: str, prompt: str) -> Dict[str, Any]`
     - `approve_plan(session_id: str) -> Dict[str, Any]`
     - `list_activities(session_id: str, page_size: int = 50, page_token: Optional[str] = None) -> Dict[str, Any]`
   - If needed, extract URL normalization or session ID parsing into `amb_cli/integrations/jules/jules_core/session_helpers.py`.

2. **Rule 03 (Canonical Imports & Backward Compatibility):**
   - Must remain 100% compatible with imports from `amb_cli.integrations.jules.jules_client import JulesClient` and `integrations.jules.jules_client import JulesClient`.

3. **Rule 04 & Rule 05 (Type Annotations & Clean Docstrings):**
   - Verify complete type annotations across all methods.
   - Concise docstrings explaining behavior without decorative ASCII headers.

4. **Rule 06 (Green Tests):**
   - Run `pytest tests/test_jules_integration.py` and full suite `pytest`.
   - Ensure all 15+ Jules integration tests pass without modification.
