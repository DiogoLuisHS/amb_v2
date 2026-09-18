# Task: Refactor and Atomize `amb_cli/gui/wizard_app.py` (Rule 02 & Rule 01)

## Context and Goal
`amb_cli/gui/wizard_app.py` currently contains 476 lines, making it the **last remaining module in the entire AMB_V2 source codebase that violates Rule 02 (> 300 lines)**.
It accumulates multiple responsibilities (Rule 01):
1. Command extraction and tree traversal from `argparse` subparsers (`_extract_commands`).
2. Tkinter Runner Tab UI with canvas scrolling, dynamic parameter inputs, and command construction (`_build_runner_tab`, `_render_action`, `execute_cmd`).
3. Tkinter Settings Tab UI with `.env` parameter loading, editing, custom variable insertion, and file saving (`_build_settings_tab`, `_load_env_fields`, `save_env`).
4. Main Tkinter application window (`DynamicWizard`) and launcher (`start_wizard`).

The goal is to refactor `amb_cli/gui/wizard_app.py` down to strictly **less than 150 lines**, extracting specialized components into `amb_cli/gui/wizard_core/`, while preserving 100% functionality and adding a unit test suite in `tests/test_gui_wizard.py`.

---

## Architectural Requirements

1. **Rule 01 (SRP) & Rule 02 (Atomicity <= 300 lines):**
   - Create package `amb_cli/gui/wizard_core/`:
     - `amb_cli/gui/wizard_core/__init__.py`
     - `amb_cli/gui/wizard_core/parser_extractor.py`:
       - `extract_commands(parser, prefix="") -> Dict[str, Any]`
       - `clean_command_map(command_map: Dict[str, Any]) -> Dict[str, Any]`
       - `detect_repo_name(project_root: str, env_path: str) -> str`
     - `amb_cli/gui/wizard_core/runner_tab.py`:
       - Class or helper functions managing the Runner Tab (`build_runner_tab`, `on_command_select`, `render_action`, `build_command_string`).
     - `amb_cli/gui/wizard_core/settings_tab.py`:
       - Class or helper functions managing the Settings Tab (`build_settings_tab`, `choose_project_dir`, `load_env_fields`, `render_env_row`, `add_custom_env_var`, `save_env_file`).
   - In `amb_cli/gui/wizard_app.py`:
     - Keep under 150 lines.
     - Maintain class `DynamicWizard(tk.Tk)` orchestrating the tabs.
     - Maintain entry point `start_wizard()`.
     - Maintain execution block `if __name__ == "__main__": start_wizard()`.

2. **Rule 03 (Canonical Imports & Backward Compatibility):**
   - Must remain 100% compatible with existing entry point:
     `python -m amb_cli gui` (which calls `from gui.wizard_app import start_wizard; start_wizard()`).
   - In `amb_cli/config/bootstrap.py`, ensure `"gui/wizard_core"` is registered in `CANONICAL_SUBMODULES`.

3. **Rule 04 & Rule 05 (Type Annotations & Clean Docstrings):**
   - Complete type annotations across all methods and functions.
   - Clean docstrings without ASCII banners.

4. **Rule 06 (Green Tests):**
   - Create `tests/test_gui_wizard.py` verifying:
     - `extract_commands` and `clean_command_map` with `create_parser()`.
     - `detect_repo_name` with mock `.env` and directory paths.
     - Command building and `.env` parsing logic without requiring a physical display.
   - Run full suite `pytest` and ensure all 139+ tests pass with zero regressions.
