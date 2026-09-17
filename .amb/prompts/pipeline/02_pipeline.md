# Task: Refactor and Atomize `amb_cli/pipeline/pipeline.py` (Rule 02 & Rule 01)

## Context and Goal
`amb_cli/pipeline/pipeline.py` currently has 476 lines, which violates our hard limit of 300 lines (Rule 02). It combines overall pipeline stage coordination with markdown prompt splitting, HTML/DOM scrubbing, UI synthesis via Antigravity, interactive CLI prompt menus (Gatekeeper 1), and executive prompt synthesis.

The goal is to refactor `amb_cli/pipeline/pipeline.py` down to strictly **less than 240 lines**, extracting helper logic into `amb_cli/pipeline/pipeline_core/`, preserving 100% backward compatibility for `PipelineOrchestrator` and CLI `main()`, and creating a comprehensive unit test suite in `tests/test_pipeline.py`.

---

## Architectural Requirements

1. **Rule 01 (SRP) & Rule 02 (Atomicity <= 300 lines):**
   - Create package `amb_cli/pipeline/pipeline_core/`:
     - `amb_cli/pipeline/pipeline_core/__init__.py`
     - `amb_cli/pipeline/pipeline_core/prompt_builder.py`:
       - `parse_single_prompt(markdown_text: str) -> tuple[str, str]`
       - `clean_html_for_summary(html: str) -> str`
       - `synthesize_stitch_ui(client_agy: Any, stitch_prompt: str, stitch_html: str, screen_title: str) -> str`
       - `build_executive_prompt(repo_name: str, starting_branch: str, file_label: str, jules_prompt: str, stitch_prompt: str, current_screen_id: Optional[str], screen_title: Optional[str], screenshot_url: Optional[str], stitch_summary: Optional[str], rules_summary: Optional[str], skip_stitch: bool) -> str`
     - `amb_cli/pipeline/pipeline_core/design_stage.py`:
       - `process_design_stage(stitch_prompt: str, current_screen_id: Optional[str], edit_screen_id: Optional[str], device_type: Optional[str], auto_approve: bool, sync_ds: bool) -> Dict[str, Any]`
   - In `amb_cli/pipeline/pipeline.py`:
     - Keep under 240 lines.
     - Maintain public class `PipelineOrchestrator`:
       - `run(cls, prompt_file=None, stitch_prompt_file=None, jules_prompt_file=None, auto_approve=False, skip_stitch=False, no_qa=False, resume_session=None, device_type=None, edit_screen_id=None, screen_id=None, sync_ds=False, starting_branch=None)`
       - Retain backward-compatible helper methods delegating to `pipeline_core` (e.g. `_parse_single_prompt`, `_clean_html_for_summary`, `_synthesize_stitch_ui`, `_extract_clean_rules`, `_monitor_jules_session`).
       - `main()` with CLI argument parsing.

2. **Rule 03 (Canonical Imports & Backward Compatibility):**
   - Must remain 100% compatible with imports from `from pipeline.pipeline import PipelineOrchestrator` and `from amb_cli.pipeline.pipeline import PipelineOrchestrator`.

3. **Rule 04 & Rule 05 (Type Annotations & Clean Docstrings):**
   - Complete type annotations across all methods.
   - Clean docstrings without decorative ASCII headers.

4. **Rule 06 (Green Tests):**
   - Create `tests/test_pipeline.py` verifying:
     - `parse_single_prompt` with visual + engineering sections, and single markdown text.
     - `clean_html_for_summary` removing scripts, styles, SVGs, base64 images.
     - `build_executive_prompt` assembling requirements, stitch spec, and architectural guidelines.
     - `PipelineOrchestrator.run` mocked behavior.
   - Run full suite `pytest` and ensure all tests pass with zero regressions.
