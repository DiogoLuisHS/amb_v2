# Task: Audit and Validate `amb_cli/integrations/common/base_google_client.py` (Rule 04 & Rule 06)

## Context and Goal
`amb_cli/integrations/common/base_google_client.py` (217 lines) is the foundational HTTP client providing authenticated requests, exponential backoff, jitter, timeout handling, and fail-fast diagnostics for Google APIs (Jules, Gemini).
The goal is to audit this module against Rules 01-05 (strict typing, concise docstrings without giant ASCII banners, <=250 lines) and ensure 100% green tests in `tests/test_base_google_client.py`.

---

## Architectural Requirements

1. **Rule 01 (SRP) & Rule 02 (Atomicity <= 300 lines):**
   - Keep `amb_cli/integrations/common/base_google_client.py` under 230 lines.
   - Maintain core class `BaseGoogleClient`:
     - `__init__(self, base_url: str = "", api_key: Optional[str] = None, service_name: str = "GOOGLE", timeout: int = 40, max_retries: int = 3, base_delay: float = 1.0)`
     - `execute_request(self, method: str, path_or_url: str, params: Optional[Dict[str, Any]] = None, data: Optional[Dict[str, Any]] = None, headers: Optional[Dict[str, str]] = None) -> Dict[str, Any]`
     - Exponential backoff with jitter and transient status code handling (429, 500, 502, 503, 504).

2. **Rule 04 & Rule 05 (Type Annotations & Clean Docstrings):**
   - Verify complete type annotations across all methods and internal helpers.
   - Concise docstrings explaining behavior without decorative ASCII headers.

3. **Rule 06 (Green Tests):**
   - Run `pytest tests/test_base_google_client.py` and full suite `pytest`.
   - Ensure all existing tests pass with zero regressions.
