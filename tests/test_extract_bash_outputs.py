import pytest
import argparse
from typing import List, Dict, Any

from amb_cli.integrations.jules.jules_core.session_extractor import SessionExtractor
from amb_cli.cli_modules.cli_parsers import create_parser

class TestExtractBashOutputs:

    def test_extract_bash_outputs_success(self):
        activities = [
            {
                "artifacts": [
                    {
                        "bashOutput": {
                            "command": "pytest -q",
                            "output": "246 passed in 4.28s",
                            "exitCode": 0
                        }
                    },
                    {
                        "bashOutput": {
                            "command": "flake8 .",
                            "output": "./file.py:1:1: F401 'os' imported but unused",
                            "exitCode": 1
                        }
                    }
                ]
            },
            {
                "artifacts": [
                    {
                        "someOtherArtifact": {}
                    }
                ]
            }
        ]

        result = SessionExtractor.extract_bash_outputs(activities)
        assert len(result) == 2
        assert result[0]["command"] == "pytest -q"
        assert result[0]["output"] == "246 passed in 4.28s"
        assert result[0]["exitCode"] == 0
        assert result[1]["command"] == "flake8 ."
        assert result[1]["output"] == "./file.py:1:1: F401 'os' imported but unused"
        assert result[1]["exitCode"] == 1

    def test_extract_bash_outputs_empty(self):
        activities = [
            {"artifacts": [{"someOtherArtifact": {}}]},
            {"no_artifacts": True}
        ]
        result = SessionExtractor.extract_bash_outputs(activities)
        assert len(result) == 0

        result = SessionExtractor.extract_bash_outputs([])
        assert len(result) == 0

        result = SessionExtractor.extract_bash_outputs(None)
        assert len(result) == 0

    def test_cli_parser_bash_flag(self):
        parser = create_parser()
        args = parser.parse_args(["jules", "extract", "test-session-id", "--bash"])
        assert args.bash is True

        args_no_bash = parser.parse_args(["jules", "extract", "test-session-id"])
        assert args_no_bash.bash is False
