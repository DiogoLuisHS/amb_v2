# Task: Audit and Enhance `amb_cli/config/bootstrap.py` (Rule 03 & Rule 04)

## Context and Goal
`amb_cli/config/bootstrap.py` is the deterministic entry point that configures `sys.path` and submodule resolution across both standalone development and consumer repository contexts.
During recent architectural atomizations, new decoupled packages were introduced:
- `architecture/context_core`
- `cli_modules/handlers_core`
- `config/config_core`
- `agents/loop_core`

The goal is to audit `amb_cli/config/bootstrap.py`, ensure all active submodules are explicitly registered in `CANONICAL_SUBMODULES`, enforce strict typing and concise docstrings (Rule 04 & 05), and ensure full test coverage in `tests/test_bootstrap.py`.

---

## Architectural Requirements

1. **Rule 03 (Canonical Submodule Discovery):**
   - Ensure `CANONICAL_SUBMODULES` in `amb_cli/config/bootstrap.py` includes:
     ```python
     CANONICAL_SUBMODULES: List[str] = [
         "config",
         "config/config_core",
         "config/setup_modules",
         "agents",
         "agents/auto_reply_core",
         "agents/loop_core",
         "architecture",
         "architecture/context_core",
         "pipeline",
         "gui",
         "integrations",
         "integrations/common",
         "integrations/git",
         "integrations/git/tools",
         "integrations/jules",
         "integrations/jules/tools",
         "integrations/stitch",
         "integrations/stitch/tools",
         "integrations/antigravity",
         "integrations/antigravity/tools",
         "cli_modules",
         "cli_modules/handlers_core",
     ]
     ```
   - Ensure `get_amb_root()`, `get_amb_package_dir()`, `add_to_sys_path()`, and `ensure_amb_env()` retain deterministic, idempotent behavior.

2. **Rule 02 & Rule 05 (Atomicity & Docstrings):**
   - Keep file length <= 160 lines.
   - Clean docstrings, no giant banners or ASCII art.

3. **Rule 04 (Strict Type Annotations):**
   - Verify typing across all functions (`Path`, `List[str]`, `Optional[List[str]]`, `bool`, etc.).

4. **Rule 06 (Green Tests):**
   - Run `pytest tests/test_bootstrap.py` and full suite `pytest`.
   - Update `tests/test_bootstrap.py` if needed to verify that the newly added submodules are present in `CANONICAL_SUBMODULES`.
   - Ensure 100% tests pass.
