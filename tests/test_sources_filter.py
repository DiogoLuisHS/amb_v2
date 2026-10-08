import pytest
from unittest.mock import patch, MagicMock

from amb_cli.integrations.jules.jules_client import JulesClient
from amb_cli.integrations.jules.tools.list_sources import run_list_sources
from amb_cli.cli_modules.cli_parsers import create_parser

class TestSourcesFilter:

    @patch('amb_cli.integrations.jules.jules_client.JulesClient._request')
    def test_jules_client_list_sources_with_filter(self, mock_request):
        mock_request.return_value = {"sources": [{"name": "sources/test-repo"}]}
        client = JulesClient(api_key="fake-key")

        result = client.list_sources(filter_expr="name=sources/test-repo")

        mock_request.assert_called_once_with(
            "GET", "sources", params={"pageSize": 50, "filter": "name=sources/test-repo"}
        )
        assert result == [{"name": "sources/test-repo"}]

    @patch('amb_cli.integrations.jules.jules_client.JulesClient._request')
    def test_jules_client_list_sources_without_filter(self, mock_request):
        mock_request.return_value = {"sources": [{"name": "sources/test-repo"}]}
        client = JulesClient(api_key="fake-key")

        result = client.list_sources()

        mock_request.assert_called_once_with(
            "GET", "sources", params={"pageSize": 50}
        )
        assert result == [{"name": "sources/test-repo"}]

    @patch('amb_cli.integrations.jules.jules_client.JulesClient._request')
    def test_jules_client_list_sources_empty_filter(self, mock_request):
        mock_request.return_value = {"sources": [{"name": "sources/test-repo"}]}
        client = JulesClient(api_key="fake-key")

        result = client.list_sources(filter_expr="   ")

        mock_request.assert_called_once_with(
            "GET", "sources", params={"pageSize": 50}
        )
        assert result == [{"name": "sources/test-repo"}]

    @patch('amb_cli.integrations.jules.tools.list_sources.JulesClient')
    def test_run_list_sources_with_filter(self, MockClient):
        mock_client = MockClient.return_value
        mock_client.list_sources.return_value = [{"name": "sources/test-repo"}]

        result = run_list_sources(as_json=True, filter_expr="name=sources/test-repo", client=mock_client)

        mock_client.list_sources.assert_called_once_with(filter_expr="name=sources/test-repo")
        assert result == [{"name": "sources/test-repo"}]

    def test_cli_parser_sources_filter_flag(self):
        parser = create_parser()
        args = parser.parse_args(["jules", "sources", "--filter", "name=sources/test-repo"])

        assert args.command == "jules"
        assert args.jules_cmd == "sources"
        assert args.filter == "name=sources/test-repo"
