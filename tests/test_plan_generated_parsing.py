"""
Testes unitários para o parsing e formatação resiliente de planos gerados (planGenerated).
US-23: Normalização de Parsing de Planos Aninhados no Watcher.
"""

import pytest
from integrations.jules.jules_core.session_helpers import extract_plan_steps, format_plan_step


def test_extract_plan_steps_nested_format():
    """Valida extração quando planGenerated contém objeto aninhado 'plan'."""
    raw = {
        "plan": {
            "id": "plan-123",
            "steps": [
                {"id": "s1", "title": "Setup", "description": "Install dependencies"},
                {"id": "s2", "title": "Test", "description": "Run pytest -q"}
            ]
        }
    }
    steps = extract_plan_steps(raw)
    assert len(steps) == 2
    assert steps[0]["title"] == "Setup"
    assert steps[1]["title"] == "Test"


def test_extract_plan_steps_legacy_flat_format():
    """Valida extração quando planGenerated contém 'steps' diretamente no nível superior."""
    raw = {
        "steps": [
            {"id": "step-a", "description": "Analyze structure"}
        ]
    }
    steps = extract_plan_steps(raw)
    assert len(steps) == 1
    assert steps[0]["description"] == "Analyze structure"


def test_extract_plan_steps_resilience():
    """Valida resiliência contra payloads vazios, inválidos ou nulos."""
    assert extract_plan_steps(None) == []
    assert extract_plan_steps({}) == []
    assert extract_plan_steps({"plan": None}) == []
    assert extract_plan_steps("invalid_type") == []
    assert extract_plan_steps({"plan": {"steps": "not_a_list"}}) == []


def test_format_plan_step_title_and_description():
    """Valida formatação combinada quando título e descrição existem."""
    step = {"title": "Setup", "description": "Install dependencies"}
    formatted = format_plan_step(step)
    assert formatted == "Setup: Install dependencies"


def test_format_plan_step_title_only():
    """Valida formatação quando apenas title existe."""
    step = {"title": "Build Project"}
    formatted = format_plan_step(step)
    assert formatted == "Build Project"


def test_format_plan_step_description_only():
    """Valida formatação quando apenas description existe."""
    step = {"description": "Running unit tests"}
    formatted = format_plan_step(step)
    assert formatted == "Running unit tests"


def test_format_plan_step_fallback():
    """Valida fallbacks para estruturas vazias ou primitivas."""
    assert format_plan_step({}) == "Passo sem descrição"
    assert format_plan_step("Passo em texto puro") == "Passo em texto puro"
