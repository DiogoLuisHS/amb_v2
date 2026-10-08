import pytest
from amb_cli.integrations.jules.jules_core.session_helpers import extract_pull_request

def test_extract_pull_request_from_outputs_list_without_number():
    session_dict = {
        "outputs": [
            {
                "pullRequest": {
                    "url": "https://github.com/bobalover/boba/pull/35",
                    "title": "Create a boba app",
                    "description": "This change adds the initial implementation of a boba app."
                }
            }
        ]
    }
    pr_info = extract_pull_request(session_dict)
    assert pr_info is not None
    assert pr_info["url"] == "https://github.com/bobalover/boba/pull/35"
    assert pr_info["number"] == 35
    assert pr_info["title"] == "Create a boba app"

def test_extract_pull_request_from_outputs_dict_without_number():
    session_dict = {
        "outputs": {
            "pullRequest": {
                "url": "https://github.com/bobalover/boba/pull/42",
                "title": "Fix a bug",
                "description": "Fixes a bug in the app."
            }
        }
    }
    pr_info = extract_pull_request(session_dict)
    assert pr_info is not None
    assert pr_info["url"] == "https://github.com/bobalover/boba/pull/42"
    assert pr_info["number"] == 42
    assert pr_info["title"] == "Fix a bug"

def test_extract_pull_request_with_existing_number():
    session_dict = {
        "outputs": [
            {
                "pullRequest": {
                    "url": "https://github.com/bobalover/boba/pull/35",
                    "number": 99,
                    "title": "Create a boba app"
                }
            }
        ]
    }
    pr_info = extract_pull_request(session_dict)
    assert pr_info is not None
    assert pr_info["number"] == 99

def test_extract_pull_request_from_activities_fallback():
    session_dict = {}
    activities = [
        {"text": "Created PR at https://github.com/bobalover/boba/pull/123 successfully"}
    ]
    pr_info = extract_pull_request(session_dict, activities=activities)
    assert pr_info is not None
    assert pr_info["url"] == "https://github.com/bobalover/boba/pull/123"
    assert pr_info["number"] == 123
