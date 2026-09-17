# Task: Refactor and Atomize `amb_cli/integrations/git/git_service.py` (Rule 02 & Rule 01)

## Context and Goal
`amb_cli/integrations/git/git_service.py` currently has 636 lines, which is a major violation of our 300-line limit (Rule 02) and Single Responsibility Principle (Rule 01) by combining local Git command execution with extensive GitHub CLI (`gh`) automation (PR listing, PR creation, PR checks, PR merge, release management, auth checking).

The goal is to refactor `amb_cli/integrations/git/git_service.py` down to strictly **less than 250 lines**, extracting GitHub CLI operations into `amb_cli/integrations/git/git_core/gh_cli.py`, while preserving 100% backward compatibility for all methods and ensuring all tests in `tests/test_git_service.py` pass.

---

## Architectural Requirements

1. **Rule 01 (SRP) & Rule 02 (Atomicity <= 300 lines):**
   - Create package `amb_cli/integrations/git/git_core/`:
     - `amb_cli/integrations/git/git_core/__init__.py`
     - `amb_cli/integrations/git/git_core/gh_cli.py`:
       - Encapsulate GitHub CLI commands:
         - `check_gh_auth(cwd: Optional[str] = None, fail_silently: bool = False) -> bool`
         - `list_prs(state: str = "open", limit: int = 30, cwd: Optional[str] = None) -> List[Dict[str, Any]]`
         - `get_pr_details(pr_number: int, cwd: Optional[str] = None) -> Dict[str, Any]`
         - `create_pr(title: str, body: str, base: str = "main", head: Optional[str] = None, draft: bool = False, cwd: Optional[str] = None) -> Dict[str, Any]`
         - `merge_pr(pr_number: int, method: str = "squash", delete_branch: bool = True, cwd: Optional[str] = None) -> bool`
         - `get_pr_checks(pr_number: int, cwd: Optional[str] = None) -> Dict[str, Any]`
         - `create_release(tag: str, title: str, notes: str, draft: bool = False, cwd: Optional[str] = None) -> str`
   - In `amb_cli/integrations/git/git_service.py`:
     - Keep under 250 lines.
     - Maintain public class `GitService`:
       - Local Git operations: `get_current_branch`, `get_remote_url`, `detect_github_repo`, `get_log_oneline`, `is_clean`, `get_status_porcelain`, `get_diff_summary`, `get_untracked_files`, `fetch`, `checkout_branch`, `create_and_checkout_branch`, `add_and_commit`, `push`, `pull`, `sync_with_remote`, `create_tag`, `reset_hard`.
       - Delegate GitHub CLI operations directly to `gh_cli` functions, keeping exact signatures and return types!

2. **Rule 03 (Canonical Imports & Backward Compatibility):**
   - Must remain 100% compatible with imports from `from integrations.git.git_service import GitService` and `from amb_cli.integrations.git.git_service import GitService`.

3. **Rule 04 & Rule 05 (Type Annotations & Clean Docstrings):**
   - Complete type annotations across all methods.
   - Clean docstrings without ASCII banners.

4. **Rule 06 (Green Tests):**
   - Run `pytest tests/test_git_service.py` and `pytest tests/test_merge_session_pr.py`.
   - Ensure all tests pass with zero regressions.
