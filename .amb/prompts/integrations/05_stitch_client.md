# Task: Refactor and Atomize `amb_cli/integrations/stitch/stitch_client.py` (Rule 02 & Rule 01)

## Context and Goal
`amb_cli/integrations/stitch/stitch_client.py` currently has 456 lines, exceeding our hard limit of 300 lines (Rule 02) and combining Node.js SDK process bridging, screen generation/variant workflows, asset download (HTML/PNG), and design system synchronization in one file.

The goal is to refactor `amb_cli/integrations/stitch/stitch_client.py` down to strictly **less than 250 lines**, extracting asset downloading and design token sync into `amb_cli/integrations/stitch/stitch_core/`, while keeping 100% backward compatibility with all tests in `tests/test_stitch_integration.py`.

---

## Architectural Requirements

1. **Rule 01 (SRP) & Rule 02 (Atomicity <= 300 lines):**
   - Create package `amb_cli/integrations/stitch/stitch_core/`:
     - `amb_cli/integrations/stitch/stitch_core/__init__.py`
     - `amb_cli/integrations/stitch/stitch_core/asset_manager.py`:
       - Encapsulate file writing, HTML export, screenshot downloading, and local asset storage (`download_screen_assets`).
     - `amb_cli/integrations/stitch/stitch_core/design_sync.py`:
       - Encapsulate design system configuration merging, token synthesis, and synchronization (`sync_design_system`).
   - In `amb_cli/integrations/stitch/stitch_client.py`:
     - Keep under 250 lines.
     - Maintain public class `StitchClient`:
       - `_resolve_runner() -> str`
       - `_run_node_command(action: str, payload: Dict[str, Any]) -> Dict[str, Any]`
       - `generate_screen(prompt: str, project_id: Optional[str] = None, device_type: Optional[str] = None, design_tokens: Optional[Dict[str, Any]] = None) -> Dict[str, Any]`
       - `edit_screen(screen_id: str, prompt: str, project_id: Optional[str] = None) -> Dict[str, Any]`
       - `generate_variants(screen_id: str, prompt: str, project_id: Optional[str] = None, count: int = 3) -> Dict[str, Any]`
       - `list_screens(project_id: Optional[str] = None) -> List[Dict[str, Any]]`
       - `get_screen(screen_id: str, project_id: Optional[str] = None) -> Dict[str, Any]`
       - `download_screen_assets(...)` (delegates to `asset_manager`)
       - `sync_design_system(...)` (delegates to `design_sync`)

2. **Rule 03 (Canonical Imports & Backward Compatibility):**
   - Must remain 100% compatible with imports from `from integrations.stitch.stitch_client import StitchClient` and `from amb_cli.integrations.stitch.stitch_client import StitchClient`.

3. **Rule 04 & Rule 05 (Type Annotations & Clean Docstrings):**
   - Complete type annotations across all parameters and return types.
   - Concise docstrings without ASCII banners.

4. **Rule 06 (Green Tests):**
   - Run `pytest tests/test_stitch_integration.py` and full suite `pytest`.
   - Ensure all 16 tests in `test_stitch_integration.py` pass without regression.
