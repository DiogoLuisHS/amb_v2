# Task: Audit and Validate `amb_cli/config/setup_project.py` (Rule 01, 04, 05, 06)

## Context and Goal
`amb_cli/config/setup_project.py` (245 lines) orchestrates the setup workflow for onboarding external repositories into AMB_V2 by coordinating `ProjectAnalyzer`, `AmbProvisioner`, and `CognitiveSynthesizer`.
The goal is to audit this module, verify strict typing, clean docstrings, ensure full dry-run safety and non-interactive determinism, and expand test verification in `tests/test_setup_and_analyzer.py`.

---

## Architectural Requirements

1. **Rule 01 (SRP) & Rule 02 (Atomicity <= 300 lines):**
   - Keep `amb_cli/config/setup_project.py` strictly under 260 lines.
   - Maintain the orchestrator role of `run_setup()` delegating:
     - Inspection to `ProjectAnalyzer`.
     - Scaffolding to `AmbProvisioner`.
     - Synthesis to `CognitiveSynthesizer` (if configured).
   - Ensure `dry_run=True` NEVER mutates the disk or creates files, returning pure dictionary metadata preview.

2. **Rule 04 & Rule 05 (Type Hints & Clean Docstrings):**
   - Verify complete type annotations across parameters and return values.
   - Replace any long ASCII decorative banners with standard concise docstrings.

3. **Rule 06 (Green Tests & Test Expansion):**
   - Run existing tests: `pytest tests/test_setup_and_analyzer.py`.
   - Add/verify assertions for:
     - `run_setup(interactive=False, dry_run=True, target_dir=...)` returning schema-compliant dict without writing files.
     - `run_setup(interactive=False, dry_run=False, force=True, target_dir=...)` provisioning `.amb/` and `amb_project.json`.
   - Ensure the entire test suite (`pytest`) remains 100% green.
