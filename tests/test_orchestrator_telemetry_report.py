import pytest
import json
from unittest.mock import patch, MagicMock
from pathlib import Path
from core.local_telemetry import LocalTelemetry
from core.console_presenter import ConsolePresenter
from pipeline.pipeline import PipelineOrchestrator
from agents.autonomous_loop import run_autonomous_loop

def test_local_telemetry_get_round_metrics(tmp_path):
    telemetry_file = tmp_path / "telemetry.jsonl"
    with patch("core.local_telemetry.LocalTelemetry._get_telemetry_file", return_value=telemetry_file):
        LocalTelemetry.record_event("ROUND_COMPLETED", {
            "total_items": 5,
            "total_duration_seconds": 872.0, # 14m 32s
            "total_stitch_screens": 2
        })
        LocalTelemetry.record_event("SESSION_COMPLETED", {"duration": 100, "pr_url": "http://pr1"})
        LocalTelemetry.record_event("SESSION_COMPLETED", {"duration": 100, "pr_url": "http://pr2"})
        LocalTelemetry.record_event("SESSION_COMPLETED", {"duration": 100, "pr_url": "http://pr3"})
        LocalTelemetry.record_event("SESSION_COMPLETED", {"duration": 100, "pr_url": "http://pr4"})
        LocalTelemetry.record_event("SESSION_COMPLETED", {"duration": 100, "pr_url": "http://pr5"})
        LocalTelemetry.record_event("QA_RUN", {"success": True})
        LocalTelemetry.record_event("QA_RUN", {"success": True})
        LocalTelemetry.record_event("PR_MERGED", {"pr_url": "http://pr1"})
        LocalTelemetry.record_event("PR_MERGED", {"pr_url": "http://pr2"})
        LocalTelemetry.record_event("PR_MERGED", {"pr_url": "http://pr3"})
        LocalTelemetry.record_event("PR_MERGED", {"pr_url": "http://pr4"})
        LocalTelemetry.record_event("PR_MERGED", {"pr_url": "http://pr5"})

        metrics = LocalTelemetry.get_round_metrics()
        assert metrics["total_items"] == 5
        assert metrics["total_stitch_screens"] == 2
        assert metrics["total_sessions"] == 5
        assert metrics["total_prs_opened"] == 5
        assert metrics["total_prs_merged"] == 5
        assert metrics["qa_success_rate"] == 100.0
        assert metrics["total_duration_seconds"] == 872.0

def test_console_presenter_render_executive_summary_stdout(capsys):
    presenter = ConsolePresenter(json_mode=False)
    metrics = {
        "total_items": 5,
        "total_stitch_screens": 2,
        "total_sessions": 5,
        "total_prs_opened": 5,
        "total_prs_merged": 5,
        "qa_success_rate": 100.0,
        "total_duration_seconds": 872.0
    }
    presenter.render_executive_summary(metrics)
    captured = capsys.readouterr()
    assert "RESUMO EXECUTIVO DE ORQUESTRAÇÃO AMB_V2" in captured.out
    assert "5 prompts processados" in captured.out
    assert "2 interfaces visuais" in captured.out
    assert "5 sessões completadas com sucesso" in captured.out
    assert "5 PRs abertos | 5 PRs integrados via Auto-Merge" in captured.out
    assert "100.0% verde" in captured.out
    assert "14m 32s" in captured.out

def test_console_presenter_render_executive_summary_json(capsys):
    presenter = ConsolePresenter(json_mode=True)
    metrics = {
        "total_items": 5,
        "total_stitch_screens": 2,
        "total_sessions": 5,
        "total_prs_opened": 5,
        "total_prs_merged": 5,
        "qa_success_rate": 100.0,
        "total_duration_seconds": 872.0
    }
    presenter.render_executive_summary(metrics)
    captured = capsys.readouterr()
    data = json.loads(captured.out)
    assert data["total_items"] == 5
    assert data["total_stitch_screens"] == 2
    assert data["total_sessions"] == 5
    assert data["total_prs_opened"] == 5
    assert data["total_prs_merged"] == 5
    assert data["qa_success_rate"] == 100.0
    assert data["total_duration_seconds"] == 872.0

def test_local_telemetry_get_round_metrics_isolated(tmp_path):
    telemetry_file = tmp_path / "telemetry.jsonl"
    from datetime import datetime, timezone, timedelta

    past_time = datetime.now(timezone.utc) - timedelta(hours=1)
    current_time = datetime.now(timezone.utc)

    with patch("core.local_telemetry.LocalTelemetry._get_telemetry_file", return_value=telemetry_file):
        # old events
        old_event = {
            "timestamp": past_time.isoformat(),
            "event_type": "SESSION_COMPLETED",
            "data": {"duration": 500, "pr_url": "http://pr-old"}
        }
        with open(telemetry_file, "a") as f:
            f.write(json.dumps(old_event) + "\n")

        # Write new events properly
        LocalTelemetry.record_event("ROUND_COMPLETED", {
            "total_items": 1,
            "total_duration_seconds": 100.0,
            "total_stitch_screens": 1
        })
        LocalTelemetry.record_event("SESSION_COMPLETED", {"duration": 100, "pr_url": "http://pr-new"})

        metrics = LocalTelemetry.get_round_metrics(current_time.timestamp())

        assert metrics["total_sessions"] == 1
        assert metrics["total_prs_opened"] == 1
        assert metrics["total_duration_seconds"] == 100.0
