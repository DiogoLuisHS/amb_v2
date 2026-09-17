# Task: Refactor and Atomize `amb_cli/config/config.py` (Rule 02 & Rule 01)

## Context and Goal
`amb_cli/config/config.py` currently has 507 lines, which exceeds our architectural hard limit of 300 lines per file (Rule 02) and violates Single Responsibility Principle (Rule 01) by combining terminal styling, error hierarchies, environment loading, design tokens parsing, and environment diagnostic reporting in a single module.

The goal is to refactor `amb_cli/config/config.py` down to strictly **less than 250 lines**, extracting specialized helper modules into `amb_cli/config/config_core/`, while preserving 100% backward compatibility for all exported symbols and adding a comprehensive unit test suite in `tests/test_config.py`.

---

## Architectural Requirements

1. **Rule 01 (SRP) & Rule 02 (Atomicity <= 300 lines):**
   - Create package `amb_cli/config/config_core/`:
     - `amb_cli/config/config_core/__init__.py`
     - `amb_cli/config/config_core/design_tokens.py`:
       - Contains `parse_design_tokens_from_text(text: str) -> Dict[str, Any]`
       - Contains `get_design_system_config(default_file: Optional[str] = None) -> Dict[str, Any]`
       - Keeps all regexes and logic for hex colors, colorMode, fonts, and roundness.
     - `amb_cli/config/config_core/env_diagnostics.py`:
       - Contains `run_environment_diagnostics(as_json: bool = False) -> Dict[str, Any]`
       - Implements the complete repository environment and health check report (Git status, GH CLI auth, API keys masked status, QA commands, personas count, visual terminal output).
   - In `amb_cli/config/config.py`:
     - Keep under 250 lines.
     - Contains:
       - `Colors`
       - `AmbError`, `ConfigurationError`, `ApiExecutionError`
       - `log`, `log_error`
       - `find_repo_root`, `load_env_file`, `load_project_json`
       - `get_env`, `require_env`, `get_repo_name`, `get_device_type`
       - Re-export `parse_design_tokens_from_text` and `get_design_system_config` from `amb_cli.config.config_core.design_tokens`.
       - Implement `main(as_json: bool = False)` by calling `run_environment_diagnostics(as_json=as_json)` from `amb_cli.config.config_core.env_diagnostics`.

2. **Rule 03 (Canonical Imports & Backward Compatibility):**
   - The following symbols MUST be directly importable from `amb_cli.config.config` and `config` as before:
     `Colors`, `AmbError`, `ConfigurationError`, `ApiExecutionError`, `log`, `log_error`, `find_repo_root`, `load_env_file`, `load_project_json`, `get_env`, `require_env`, `get_repo_name`, `get_device_type`, `parse_design_tokens_from_text`, `get_design_system_config`, `main`.
   - In `amb_cli/config/bootstrap.py`, ensure `"config/config_core"` is added to `CANONICAL_SUBMODULES`.

3. **Rule 04 & 05 (Type Hints & Clean Docstrings):**
   - Strict type hints on every function and method.
   - Clean, concise docstrings. No giant ASCII banners.

4. **Rule 06 (Green Tests):**
   - Create `tests/test_config.py` verifying:
     - `Colors` ANSI strings.
     - `AmbError`, `ConfigurationError`, `ApiExecutionError` message and hint formatting.
     - `find_repo_root` with start_dir.
     - `get_env` and `require_env` (including ConfigurationError when mandatory var missing).
     - `parse_design_tokens_from_text` with mock markdown text (color, mode, font, roundness).
     - `get_design_system_config` behavior.
     - `main(as_json=True)` returning dictionary report.
   - Run `pytest` and ensure all 110+ tests pass with zero regressions.
