# Task: Audit and Validate `amb_cli/config/rules_manager.py` (Rule 04 & Rule 06)

## Context and Goal
`amb_cli/config/rules_manager.py` (236 lines) is the centralized rule manager responsible for discovering, reading, caching, sanitizing, and filtering architectural rules for AI prompts.
The goal is to audit this module against Rules 01-05 (strict typing, fence closure safety, concise docstrings, max 300 lines) and create a dedicated, comprehensive unit test suite in `tests/test_rules_manager.py`.

---

## Architectural Requirements

1. **Rule 01 (SRP) & Rule 02 (Atomicity <= 300 lines):**
   - Keep `amb_cli/config/rules_manager.py` under 250 lines.
   - Maintain its core singleton design:
     - `RulesManager.get_instance(custom_rules_dir: Optional[str] = None) -> RulesManager`
     - `RulesManager.invalidate_cache() -> None`
     - `resolve_rules_dir(custom_dir: Optional[str] = None, root: Optional[str] = None) -> Optional[str]`
     - `list_rules(rules_dir: Optional[str] = None, root: Optional[str] = None) -> List[Dict[str, Any]]`
     - `clean_markdown_snippet(text: str, max_chars: int = 3000) -> str`
     - `load_rules(rules_dir: Optional[str] = None, max_chars: int = 8000, root: Optional[str] = None) -> str`
     - `filter_rules_for_agent(rules_text: Optional[str] = None, role: Optional[str] = None, max_chars: int = 6000) -> str`
   - Preserve convenience functions:
     - `get_rules_manager(custom_dir: Optional[str] = None) -> RulesManager`
     - `load_project_rules(rules_dir: Optional[str] = None, max_chars: int = 8000) -> str`

2. **Rule 04 & Rule 05 (Type Hints & Markdown Safety):**
   - Ensure complete return types and parameter types on all functions.
   - Verify that `clean_markdown_snippet` properly closes open triple-backtick fences if the snippet is truncated mid-block.
   - Ensure clean docstrings without excessive ASCII headers.

3. **Rule 06 (Green Test Suite):**
   - Create `tests/test_rules_manager.py` covering:
     - Singleton instance and cache invalidation.
     - `resolve_rules_dir` matching candidate directories (`.agents/rules`, `.antigravity/rules`, `rules/`, `AGENTS.md`).
     - `list_rules` reading `.md` files and generating snippets.
     - `clean_markdown_snippet` stripping YAML frontmatter (`--- ... ---`), stripping HTML comments (`<!-- ... -->`), and closing open code fences.
     - `load_rules` per-file budget and caching.
     - `filter_rules_for_agent` prioritizing blocks matching the agent role.
   - Run `pytest` and ensure all tests pass.
