# -*- coding: utf-8 -*-
import os
import pytest
from pathlib import Path

from amb_cli.workspace.rules_manager import RulesManager, get_rules_manager, load_project_rules

@pytest.fixture(autouse=True)
def clear_rules_manager_cache():
    """Ensure cache is clear before and after each test."""
    RulesManager.invalidate_cache()
    RulesManager._instance = None
    yield
    RulesManager.invalidate_cache()
    RulesManager._instance = None


def test_singleton_and_cache_invalidation():
    # Test Singleton behavior
    rm1 = RulesManager.get_instance()
    rm2 = RulesManager.get_instance()
    assert rm1 is rm2

    # Provide a custom_rules_dir, it should replace the instance or update it?
    # Wait, get_instance logic:
    # if cls._instance is None or custom_rules_dir is not None:
    #     cls._instance = cls(custom_rules_dir=custom_rules_dir)
    # Let's test that
    rm3 = RulesManager.get_instance(custom_rules_dir="/tmp/custom_dir")
    assert rm3 is not rm1
    assert rm3.custom_rules_dir == "/tmp/custom_dir"

    # Test cache invalidation
    RulesManager._cached_rules_by_dir["dummy_key"] = "dummy_data"
    RulesManager._cached_list_by_dir["dummy_key"] = [{"dummy": "data"}]
    RulesManager.invalidate_cache()
    assert len(RulesManager._cached_rules_by_dir) == 0
    assert len(RulesManager._cached_list_by_dir) == 0


def test_resolve_rules_dir_explicit_dir(tmp_path):
    custom_dir = tmp_path / "custom"
    custom_dir.mkdir()

    rm = RulesManager(custom_rules_dir=str(custom_dir))
    resolved = rm.resolve_rules_dir()
    assert resolved == str(custom_dir)


def test_resolve_rules_dir_fallback_dirs(tmp_path):
    # Candidates order:
    # 2. .antigravity/rules/
    # 3. .gemini/rules/
    # 4. .agents/rules/ ou rules/
    # 5. Root se contiver AGENTS.md ou GEMINI.md

    root_dir = tmp_path / "repo_root"
    root_dir.mkdir()

    rm = RulesManager()

    # Case 5: Root with AGENTS.md
    agents_md = root_dir / "AGENTS.md"
    agents_md.touch()
    assert rm.resolve_rules_dir(root=str(root_dir)) == str(root_dir)

    # Case 4: rules/
    rules_dir = root_dir / "rules"
    rules_dir.mkdir()
    assert rm.resolve_rules_dir(root=str(root_dir)) == str(rules_dir)

    # Case 4: .agents/rules/
    agents_rules_dir = root_dir / ".agents" / "rules"
    agents_rules_dir.parent.mkdir()
    agents_rules_dir.mkdir()
    assert rm.resolve_rules_dir(root=str(root_dir)) == str(agents_rules_dir)

    # Case 3: .gemini/rules/
    gemini_rules_dir = root_dir / ".gemini" / "rules"
    gemini_rules_dir.parent.mkdir()
    gemini_rules_dir.mkdir()
    assert rm.resolve_rules_dir(root=str(root_dir)) == str(gemini_rules_dir)

    # Case 2: .antigravity/rules/
    antigravity_rules_dir = root_dir / ".antigravity" / "rules"
    antigravity_rules_dir.parent.mkdir()
    antigravity_rules_dir.mkdir()
    assert rm.resolve_rules_dir(root=str(root_dir)) == str(antigravity_rules_dir)


def test_list_rules(tmp_path):
    rules_dir = tmp_path / "rules"
    rules_dir.mkdir()

    # Create valid md files
    file1 = rules_dir / "rule1.md"
    file1.write_text("This is the first line.\nThis is the second.", encoding="utf-8")

    file2 = rules_dir / "rule2.md"
    # Starting with # shouldn't be the summary
    file2.write_text("# Title\n\nActual summary line.", encoding="utf-8")

    # Create ignored files
    (rules_dir / "_ignored.md").touch()
    (rules_dir / "not_md.txt").touch()

    rm = RulesManager(custom_rules_dir=str(rules_dir))
    rules = rm.list_rules()

    assert len(rules) == 2

    # Check rule1
    r1 = next(r for r in rules if r["name"] == "rule1.md")
    assert r1["path"] == str(file1)
    assert r1["summary"] == "This is the first line."

    # Check rule2
    r2 = next(r for r in rules if r["name"] == "rule2.md")
    assert r2["path"] == str(file2)
    assert r2["summary"] == "Actual summary line."


def test_list_rules_direct_file(tmp_path):
    direct_file = tmp_path / "AGENTS.md"
    direct_file.write_text("direct rules", encoding="utf-8")

    rm = RulesManager()
    rules = rm.list_rules(rules_dir=str(direct_file))

    assert len(rules) == 1
    assert rules[0]["name"] == "AGENTS.md"
    assert rules[0]["path"] == str(direct_file)
    assert rules[0]["summary"] == "Arquivo de regras direto."


def test_clean_markdown_snippet_strips_yaml_and_html():
    markdown = """---
title: Rule
author: test
---
<!-- This is a comment -->
# Rule
Content
"""
    cleaned = RulesManager.clean_markdown_snippet(markdown)
    assert "---" not in cleaned
    assert "title: Rule" not in cleaned
    assert "<!-- This is a comment -->" not in cleaned
    assert "# Rule\nContent" in cleaned


def test_clean_markdown_snippet_truncates_and_closes_fences():
    markdown = """Some text before code block
```python
def foo():
    pass
"""
    # Max chars to force truncation in the middle of code block
    cleaned = RulesManager.clean_markdown_snippet(markdown, max_chars=40)
    assert len(cleaned) > 40  # because of the added closing fences and ellipsis

    # Count fences
    fences_count = cleaned.count("```")
    assert fences_count % 2 == 0  # Even number of fences means they are closed
    assert "... [regras truncadas para concisão]" in cleaned


def test_load_rules_consolidates_and_caches(tmp_path):
    rules_dir = tmp_path / "rules"
    rules_dir.mkdir()

    file1 = rules_dir / "rule1.md"
    file1.write_text("Rule 1 content.", encoding="utf-8")

    file2 = rules_dir / "rule2.md"
    file2.write_text("Rule 2 content.", encoding="utf-8")

    rm = RulesManager(custom_rules_dir=str(rules_dir))

    # Load and cache
    combined = rm.load_rules(max_chars=8000)

    assert "### 📋 Regra: rule1.md" in combined
    assert "Rule 1 content." in combined
    assert "### 📋 Regra: rule2.md" in combined
    assert "Rule 2 content." in combined

    # Verify it is in cache
    cache_key = f"{str(rules_dir)}_8000"
    assert cache_key in rm._cached_rules_by_dir
    assert rm._cached_rules_by_dir[cache_key] == combined


def test_load_rules_per_file_budget(tmp_path):
    rules_dir = tmp_path / "rules"
    rules_dir.mkdir()

    file1 = rules_dir / "rule1.md"
    file1.write_text("Rule 1 content that is quite long " * 100, encoding="utf-8")

    file2 = rules_dir / "rule2.md"
    file2.write_text("Rule 2 content that is quite long " * 100, encoding="utf-8")

    rm = RulesManager(custom_rules_dir=str(rules_dir))

    # Force max_chars to be small enough so per_file_budget truncates
    # per_file_budget = max(500, max_chars // len(rule_files))
    # Let max_chars be 1500, so per_file_budget is 750.
    combined = rm.load_rules(max_chars=1500)

    # Because of truncation, it will append "... [regras truncadas para concisão]" to rule blocks
    assert "... [regras truncadas para concisão]" in combined


def test_filter_rules_for_agent():
    rm = RulesManager()

    # In `filter_rules_for_agent`, the split string is "\n\n### 📋 Regra: ".
    # If the text starts directly with `### 📋 Regra: `, the first paragraph
    # (header) will be `### 📋 Regra: rule1.md...` and rule1 won't be treated as a block.
    # So we should prepend a header or empty space.
    rules_text = """HEADER TEXT

### 📋 Regra: rule1.md
This rule is about Backend and database stuff.

### 📋 Regra: rule2.md
This rule is about Frontend and React stuff.

### 📋 Regra: rule3.md
General rules."""

    filtered = rm.filter_rules_for_agent(rules_text=rules_text, role="frontend")

    # Frontend rule should appear first after header
    # blocks[0] will be HEADER TEXT
    # blocks[1] will be rule2
    # blocks[2] will be rule1
    # blocks[3] will be rule3
    blocks = filtered.split("### 📋 Regra: ")
    assert "rule2.md" in blocks[1]
    assert "rule1.md" in blocks[2]
    assert "rule3.md" in blocks[3]

def test_convenience_functions(tmp_path):
    custom_dir = tmp_path / "rules"
    custom_dir.mkdir()

    file1 = custom_dir / "rule1.md"
    file1.write_text("Convenience Rule.", encoding="utf-8")

    rm = get_rules_manager(custom_dir=str(custom_dir))
    assert rm.custom_rules_dir == str(custom_dir)

    combined = load_project_rules(rules_dir=str(custom_dir))
    assert "### 📋 Regra: rule1.md\nConvenience Rule." in combined
