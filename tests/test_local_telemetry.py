import json
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

from amb_cli.core.local_telemetry import LocalTelemetry

@pytest.fixture
def temp_telemetry_file(tmp_path):
    file_path = tmp_path / "telemetry.jsonl"
    with patch("amb_cli.core.local_telemetry.LocalTelemetry._get_telemetry_file", return_value=file_path):
        yield file_path

def test_record_event(temp_telemetry_file):
    LocalTelemetry.record_event("TEST_EVENT", {"key": "value"})
    assert temp_telemetry_file.exists()

    with open(temp_telemetry_file, "r") as f:
        line = f.readline().strip()
        data = json.loads(line)

    assert data["event_type"] == "TEST_EVENT"
    assert data["data"] == {"key": "value"}
    assert "timestamp" in data

def test_get_summary_metrics_empty(temp_telemetry_file):
    metrics = LocalTelemetry.get_summary_metrics()
    assert metrics == {
        "total_sessions": 0,
        "qa_success_rate": 0.0,
        "total_prs": 0,
        "avg_duration_seconds": 0.0
    }

def test_get_summary_metrics_with_data(temp_telemetry_file):
    LocalTelemetry.record_session(120.5)
    LocalTelemetry.record_session(80.0)
    LocalTelemetry.record_qa(True)
    LocalTelemetry.record_qa(False)
    LocalTelemetry.record_qa(True)
    LocalTelemetry.record_merge("https://github.com/pr/1")
    LocalTelemetry.record_merge("https://github.com/pr/2")

    metrics = LocalTelemetry.get_summary_metrics()

    assert metrics["total_sessions"] == 2
    assert metrics["avg_duration_seconds"] == 100.25
    assert metrics["qa_success_rate"] == 66.67
    assert metrics["total_prs"] == 2

def test_get_summary_metrics_malformed_data(temp_telemetry_file):
    with open(temp_telemetry_file, "w") as f:
        f.write("this is not json\n")
        f.write('{"event_type": "SESSION_COMPLETED", "data": {"duration": 100}}\n')
        f.write('{"event_type": "PR_MERGED"}\n')
        f.write('{"malformed": true\n')

    metrics = LocalTelemetry.get_summary_metrics()

    assert metrics["total_sessions"] == 1
    assert metrics["avg_duration_seconds"] == 100.0
    assert metrics["total_prs"] == 1

def test_get_summary_metrics_non_existent_file(tmp_path):
    file_path = tmp_path / "non_existent.jsonl"
    with patch("amb_cli.core.local_telemetry.LocalTelemetry._get_telemetry_file", return_value=file_path):
        metrics = LocalTelemetry.get_summary_metrics()
        assert metrics == {
            "total_sessions": 0,
            "qa_success_rate": 0.0,
            "total_prs": 0,
            "avg_duration_seconds": 0.0
        }
