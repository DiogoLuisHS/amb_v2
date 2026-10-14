import json
import pytest
from unittest.mock import patch, MagicMock
from amb_cli.cli_modules.handlers_core.antigravity_handler import handle_cmd_antigravity

class DummyArgs:
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)

@pytest.fixture
def mock_rules_manager():
    # Patch it globally at its definition
    with patch("amb_cli.workspace.rules_manager.get_rules_manager") as mock_get_mgr, patch("amb_cli.workspace.get_rules_manager") as mock_ws_get_mgr:
        mgr = MagicMock()
        mock_get_mgr.return_value = mgr
        mock_ws_get_mgr.return_value = mgr

        # Setup fake rules directory
        mgr.resolve_rules_dir.return_value = "/fake/rules"

        # Setup fake rules list
        mgr.list_rules.return_value = [
            {"name": "frontend_rule.md", "path": "/fake/rules/frontend_rule.md", "size_bytes": 100, "summary": "Regras de frontend"},
            {"name": "backend_rule.md", "path": "/fake/rules/backend_rule.md", "size_bytes": 120, "summary": "Regras de backend"},
            {"name": "general_rule.md", "path": "/fake/rules/general_rule.md", "size_bytes": 80, "summary": "Regras gerais"}
        ]

        # Setup fake text load
        mgr.load_rules.return_value = "### 📋 Regra: frontend_rule.md\nRegras de frontend\n\n### 📋 Regra: backend_rule.md\nRegras de backend\n\n### 📋 Regra: general_rule.md\nRegras gerais"

        # Implement dynamic filter_rules_for_agent logic similar to original
        def fake_filter(rules_text=None, role=None, rules=None, max_chars=6000):
            if role is None:
                if rules is not None:
                    return rules
                return rules_text

            role_lower = role.lower()

            if rules is not None:
                return [r for r in rules if role_lower in r.get("name", "").lower() or role_lower in r.get("summary", "").lower()]

            if rules_text is not None:
                paragraphs = rules_text.split("\n\n### 📋 Regra: ")
                header = paragraphs[0]
                blocks = ["### 📋 Regra: " + p for p in paragraphs[1:]]
                matched = [b for b in blocks if role_lower in b.lower()]
                unmatched = [b for b in blocks if role_lower not in b.lower()]
                return (header + "\n\n" if header.strip() else "") + "\n\n".join(matched + unmatched)

        mgr.filter_rules_for_agent.side_effect = fake_filter
        yield mgr


def test_antigravity_rules_standard(mock_rules_manager, capsys):
    args = DummyArgs(agy_cmd="rules")
    handle_cmd_antigravity(args)

    out, _ = capsys.readouterr()
    assert "frontend_rule.md" in out
    assert "backend_rule.md" in out
    assert "general_rule.md" in out
    assert "3 arquivo(s)" in out


def test_antigravity_rules_role_frontend(mock_rules_manager, capsys):
    args = DummyArgs(agy_cmd="rules", role="frontend")
    handle_cmd_antigravity(args)

    out, _ = capsys.readouterr()
    assert "frontend_rule.md" in out
    assert "backend_rule.md" not in out
    assert "general_rule.md" not in out
    assert "1 arquivo(s)" in out


def test_antigravity_rules_role_backend_content(mock_rules_manager, capsys):
    args = DummyArgs(agy_cmd="rules", role="backend", content=True)
    handle_cmd_antigravity(args)

    out, _ = capsys.readouterr()
    assert "CONTEÚDO CONSOLIDADO DAS REGRAS:" in out
    # Verify the rule was ordered at the top or content contains backend
    assert "backend_rule.md" in out


def test_antigravity_rules_role_json(mock_rules_manager, capsys):
    args = DummyArgs(agy_cmd="rules", role="frontend", json=True)
    handle_cmd_antigravity(args)

    out, _ = capsys.readouterr()
    data = json.loads(out)
    assert "rules" in data
    assert len(data["rules"]) == 1
    assert data["rules"][0]["name"] == "frontend_rule.md"
    assert "consolidated_content" not in data


def test_antigravity_rules_role_json_content(mock_rules_manager, capsys):
    args = DummyArgs(agy_cmd="rules", role="backend", json=True, content=True)
    handle_cmd_antigravity(args)

    out, _ = capsys.readouterr()
    data = json.loads(out)
    assert "rules" in data
    assert len(data["rules"]) == 1
    assert data["rules"][0]["name"] == "backend_rule.md"
    assert "consolidated_content" in data
    assert "backend_rule.md" in data["consolidated_content"]
