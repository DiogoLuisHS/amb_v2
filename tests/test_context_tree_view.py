import pytest
from unittest.mock import patch, MagicMock
from amb_cli.architecture.ai_context_builder import AIContextBuilder, generate_context

@pytest.fixture
def mock_layers():
    return {
        "1_database_schemas": {
            "title": "1. Banco de Dados & Schemas (Drizzle / DB Tables)",
            "icon": "🗄️",
            "files": [{"path": "schema.ts"}],
        },
        "2_repositories": {
            "title": "2. Repositórios de Acesso a Dados (SQL / Queries)",
            "icon": "💾",
            "files": [{"path": "repo.ts"}, {"path": "repo2.ts"}],
        },
        "3_services": {
            "title": "3. Regras de Negócio & Serviços (Business Logic)",
            "icon": "⚙️",
            "files": [{"path": "service.ts"}, {"path": "service2.ts"}, {"path": "service3.ts"}],
        },
        "4_controllers": {
            "title": "4. Controladores & Validações de Entrada (Zod / Schemas)",
            "icon": "🎮",
            "files": [],
        },
        "5_routers_api": {
            "title": "5. Rotas & Endpoints da API (HTTP / Hono / Express)",
            "icon": "🌐",
            "files": [{"path": "api.ts"}],
        },
        "6_frontend_hooks_api": {
            "title": "6. Frontend Services, Hooks & Chamadas de API",
            "icon": "🪝",
            "files": [],
        },
        "7_frontend_components": {
            "title": "7. Componentes de UI & Modais",
            "icon": "🧩",
            "files": [{"path": "comp.tsx"}, {"path": "comp2.tsx"}],
        },
        "8_frontend_pages": {
            "title": "8. Páginas Web & Views Principais",
            "icon": "🖥️",
            "files": [{"path": "page.tsx"}],
        },
        "9_entrypoints_config": {
            "title": "9. Pontos de Entrada & Configurações Globais",
            "icon": "🚀",
            "files": [],
        },
    }

def test_generate_tree_view_output(mock_layers):
    builder = AIContextBuilder(MagicMock())
    output = builder.generate_tree_view("kanban", mock_layers)

    assert "🧭 FLUXO ARQUITETURAL EM CAMADAS: KANBAN" in output
    assert "├── 🗄️  1. Banco de Dados & Schemas: 1 arquivo" in output
    assert "├── 💾  2. Repositórios de Acesso a Dados: 2 arquivos" in output
    assert "├── ⚙️  3. Regras de Negócio & Serviços: 3 arquivos" in output
    assert "├── 🌐  5. Rotas & Endpoints da API: 1 arquivo" in output
    assert "├── 🧩  7. Componentes de UI & Modais: 2 arquivos" in output
    assert "└── 🖥️  8. Páginas Web & Views Principais: 1 arquivo" in output
    assert "Total: 10 arquivos mapeados (DB ➔ Services ➔ UI)" in output
    assert "Controladores" not in output

@patch("amb_cli.architecture.ai_context_builder.find_repo_root", return_value=".")
@patch("amb_cli.architecture.ai_context_builder.AIContextBuilder")
@patch("builtins.print")
def test_generate_context_tree_flag(mock_print, MockBuilder, mock_find_repo, mock_layers):
    mock_builder_instance = MockBuilder.return_value
    mock_builder_instance.trace_module_chain.return_value = set()
    mock_builder_instance.classify_and_order_files.return_value = mock_layers
    mock_builder_instance.generate_tree_view.return_value = "TREE_VIEW_OUTPUT"
    mock_builder_instance.generate_markdown.return_value = "MARKDOWN_OUTPUT"

    # Test --tree
    generate_context(target="kanban", tree_view=True)
    mock_builder_instance.generate_tree_view.assert_called_once_with("kanban", mock_layers)
    mock_print.assert_called_with("TREE_VIEW_OUTPUT")

    mock_print.reset_mock()
    mock_builder_instance.generate_markdown.reset_mock()

    # Test fallback markdown
    generate_context(target="kanban", tree_view=False)
    mock_builder_instance.generate_markdown.assert_called_once_with("kanban", mock_layers)
    mock_print.assert_called_with("MARKDOWN_OUTPUT")
