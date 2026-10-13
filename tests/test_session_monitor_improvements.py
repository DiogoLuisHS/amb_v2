import pytest
from unittest.mock import MagicMock, patch
from amb_cli.integrations.jules.jules_core.session_extractor import SessionExtractor
from amb_cli.agents.loop_core.session_assistant import monitor_and_assist_session


def test_detect_activity_repetition():
    # Activities repeating changes on the same db file
    repeated_acts = [
        {
            "id": f"act_{i}",
            "artifacts": [
                {
                    "changeSet": {
                        "gitPatch": {
                            "unidiffPatch": "diff --git a/apps/api/database/nexushub.db b/apps/api/database/nexushub.db\n--- a/apps/api/database/nexushub.db\n+++ b/apps/api/database/nexushub.db\n"
                        }
                    }
                }
            ]
        }
        for i in range(10)
    ]

    res = SessionExtractor.detect_activity_repetition(repeated_acts, threshold=8)
    assert res is not None
    count, files = res
    assert count == 8
    assert files == ["apps/api/database/nexushub.db"]

    # Diverse activities: should return None
    diverse_acts = [
        {
            "id": f"act_{i}",
            "artifacts": [
                {
                    "changeSet": {
                        "gitPatch": {
                            "unidiffPatch": f"diff --git a/file_{i}.ts b/file_{i}.ts\n--- a/file_{i}.ts\n+++ b/file_{i}.ts\n"
                        }
                    }
                }
            ]
        }
        for i in range(10)
    ]
    assert SessionExtractor.detect_activity_repetition(diverse_acts, threshold=8) is None


def test_extract_review_rejection():
    acts_with_rejection = [
        {
            "id": "act_1",
            "progressUpdated": {
                "title": "Code reviewed",
                "description": "An analysis reveals issues.\nBecause the patch has regressions, it is not ready for production.\n### Final Rating: #Partially Correct#"
            }
        }
    ]
    rejection = SessionExtractor.extract_review_rejection(acts_with_rejection)
    assert rejection is not None
    assert "Code reviewed" in rejection
    assert "#Partially Correct#" in rejection

    clean_acts = [
        {
            "id": "act_1",
            "progressUpdated": {
                "title": "Tests passed",
                "description": "All unit tests pass 100% green."
            }
        }
    ]
    assert SessionExtractor.extract_review_rejection(clean_acts) is None


def test_extract_patch_from_activities_fallback():
    session_data = {"outputs": []}
    activities = [
        {
            "id": "act_1",
            "artifacts": [
                {
                    "changeSet": {
                        "gitPatch": {
                            "unidiffPatch": "diff --git a/test.ts b/test.ts\n--- a/test.ts\n+++ b/test.ts\n@@ -1 +1 @@\n-old\n+new"
                        }
                    }
                }
            ]
        }
    ]
    patch_str = SessionExtractor.extract_patch(session_data, activities=activities)
    assert "diff --git a/test.ts b/test.ts" in patch_str
    assert "+new" in patch_str


@patch("amb_cli.agents.loop_core.session_assistant.time.sleep", return_value=None)
@patch("amb_cli.agents.loop_core.session_assistant.log")
@patch("amb_cli.agents.loop_core.session_assistant.log_error")
def test_session_monitor_detects_review_rejection(mock_log_err, mock_log, mock_sleep):
    client = MagicMock()
    client.get_session.return_value = {"state": "COMPLETED", "outputs": []}
    client.list_activities.return_value = [
        {
            "progressUpdated": {
                "title": "Code reviewed",
                "description": "Regressions found. Final Rating: #Partially Correct#"
            }
        }
    ]

    state = monitor_and_assist_session(client, "sess_123", require_pr=True)
    assert state == "COMPLETED_WITHOUT_PR"


@patch("amb_cli.agents.loop_core.session_assistant.time.sleep", return_value=None)
@patch("amb_cli.agents.loop_core.session_assistant.log")
@patch("amb_cli.agents.loop_core.session_assistant.log_error")
def test_session_monitor_require_pr_blocks_empty_completed(mock_log_err, mock_log, mock_sleep):
    client = MagicMock()
    client.get_session.return_value = {"state": "COMPLETED", "outputs": []}
    client.list_activities.return_value = []

    state = monitor_and_assist_session(client, "sess_123", require_pr=True)
    assert state == "COMPLETED_WITHOUT_PR"


@patch("amb_cli.agents.loop_core.session_assistant.time.sleep", return_value=None)
@patch("amb_cli.agents.loop_core.session_assistant.log")
@patch("amb_cli.agents.loop_core.session_assistant.log_error")
def test_session_monitor_completed_with_pr_succeeds(mock_log_err, mock_log, mock_sleep):
    client = MagicMock()
    client.get_session.return_value = {
        "state": "COMPLETED",
        "outputs": [{"pullRequest": {"url": "https://github.com/org/repo/pull/1"}}]
    }
    client.list_activities.return_value = []

    state = monitor_and_assist_session(client, "sess_123", require_pr=True)
    assert state == "COMPLETED"
