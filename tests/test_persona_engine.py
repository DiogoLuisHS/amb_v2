import os
import pytest
from amb_cli.agents.persona_engine import PersonaEngine

@pytest.fixture
def mock_repo_root(tmp_path):
    # Setup mock repo root
    repo_root = tmp_path / "mock_repo"
    repo_root.mkdir()

    # Setup .amb/personas
    personas_dir = repo_root / ".amb" / "personas"
    personas_dir.mkdir(parents=True)

    # Setup amb_project.json
    project_json = repo_root / "amb_project.json"
    project_json.write_text('{"stack": "python", "qa_command": "pytest"}')

    # Setup some personas
    valid_persona = personas_dir / "valid.md"
    valid_persona.write_text("# Missão\n## Arquivos\n## Regras\n{repo_name} {stack} {qa_command}")

    invalid_persona = personas_dir / "invalid.md"
    invalid_persona.write_text("Hello World")

    return str(repo_root)

def test_load_persona(mock_repo_root):
    engine = PersonaEngine(repo_root=mock_repo_root)

    # Load existing persona
    content = engine.load_persona("valid")
    assert content is not None
    assert "# Missão" in content

    # Load non-existing persona (should fallback or return None)
    content = engine.load_persona("non_existent")
    assert content is None

def test_render_persona_template(mock_repo_root):
    engine = PersonaEngine(repo_root=mock_repo_root)

    content = "Repo: {repo_name}, Stack: {stack}, QA: {qa_command}, Extra: {extra_var}"
    rendered = engine.render_persona_template(content, context_vars={"extra_var": "123"})

    assert "mock_repo" in rendered
    assert "python" in rendered
    assert "pytest" in rendered
    assert "123" in rendered

def test_validate_persona_file(mock_repo_root):
    engine = PersonaEngine(repo_root=mock_repo_root)

    valid_path = os.path.join(engine.personas_dir, "valid.md")
    errors = engine.validate_persona_file(valid_path)
    assert len(errors) == 0

    invalid_path = os.path.join(engine.personas_dir, "invalid.md")
    errors = engine.validate_persona_file(invalid_path)
    assert len(errors) == 3
    assert any("Título/Missão" in e for e in errors)
    assert any("Foco de Arquivos" in e for e in errors)
    assert any("Regras de Implementação" in e for e in errors)

def test_validate_non_existent_file(mock_repo_root):
    engine = PersonaEngine(repo_root=mock_repo_root)

    invalid_path = os.path.join(engine.personas_dir, "non_existent.md")
    errors = engine.validate_persona_file(invalid_path)
    assert len(errors) == 1
    assert "Arquivo não encontrado" in errors[0]
