import pytest
from unittest.mock import patch, MagicMock

# Importamos o handler que vamos testar
from cli_modules.handlers_core.jules_handler import handle_cmd_jules

class ArgsMock:
    def __init__(self, **kwargs):
        self.jules_cmd = "create"
        self.prompt = "Fix bug"
        for k, v in kwargs.items():
            setattr(self, k, v)


@patch("integrations.jules.tools.create_session.run_create_session")
def test_jules_create_with_require_approval(mock_run_create_session):
    """
    Testa se ao passar args.require_approval = True
    o repasse para run_create_session acontece com require_plan_approval=True
    """
    args = ArgsMock(require_approval=True)
    handle_cmd_jules(args)

    mock_run_create_session.assert_called_once_with(
        prompt="Fix bug",
        title=None,
        base_branch=None,
        source_name=None,
        as_json=False,
        auto_pr=True,
        require_plan_approval=True
    )


@patch("integrations.jules.tools.create_session.run_create_session")
def test_jules_create_without_require_approval(mock_run_create_session):
    """
    Testa se ao não passar args.require_approval (ou False)
    o repasse para run_create_session acontece com require_plan_approval=None
    """
    args = ArgsMock(require_approval=False)
    handle_cmd_jules(args)

    mock_run_create_session.assert_called_once_with(
        prompt="Fix bug",
        title=None,
        base_branch=None,
        source_name=None,
        as_json=False,
        auto_pr=True,
        require_plan_approval=None
    )
