import json
import os
import threading
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, Any, Optional

from workspace.project_context import find_repo_root


class LocalTelemetry:
    _lock = threading.Lock()

    @staticmethod
    def _get_telemetry_file() -> Path:
        repo_root_str = find_repo_root()
        if not repo_root_str:
            repo_root = Path.cwd()
        else:
            repo_root = Path(repo_root_str)
        amb_dir = repo_root / ".amb"
        amb_dir.mkdir(exist_ok=True, parents=True)
        return amb_dir / "telemetry.jsonl"

    @classmethod
    def record_event(cls, event_type: str, data: Dict[str, Any]) -> None:
        """Records an event structured as JSONL in a thread-safe manner."""
        filepath = cls._get_telemetry_file()
        event = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "event_type": event_type,
            "data": data,
        }

        with cls._lock:
            with open(filepath, "a", encoding="utf-8") as f:
                f.write(json.dumps(event) + "\n")

    @classmethod
    def record_session(cls, duration_seconds: float) -> None:
        cls.record_event("SESSION_COMPLETED", {"duration": duration_seconds})

    @classmethod
    def record_session_metrics(
        cls,
        session_id: str,
        runtime: float,
        files_changed: int = 0,
        lines_added: int = 0,
        lines_removed: int = 0,
        pr_url: Optional[str] = None
    ) -> None:
        """Registra métricas ricas de encerramento da sessão."""
        cls.record_event("SESSION_COMPLETED", {
            "session_id": session_id,
            "duration": runtime,
            "files_changed": files_changed,
            "lines_added": lines_added,
            "lines_removed": lines_removed,
            "pr_url": pr_url,
        })

    @classmethod
    def record_qa(cls, success: bool) -> None:
        cls.record_event("QA_RUN", {"success": success})

    @classmethod
    def record_merge(cls, pr_url: str) -> None:
        cls.record_event("PR_MERGED", {"pr_url": pr_url})

    @classmethod
    def get_summary_metrics(cls) -> Dict[str, Any]:
        """Computes summary metrics from the telemetry file."""
        filepath = cls._get_telemetry_file()
        if not filepath.exists():
            return cls._empty_metrics()

        total_sessions = 0
        total_duration = 0.0
        qa_runs = 0
        qa_successes = 0
        total_prs = 0
        total_files_changed = 0
        total_lines_added = 0
        total_lines_removed = 0

        with cls._lock:
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if not line:
                            continue
                        try:
                            event = json.loads(line)
                            etype = event.get("event_type")
                            data = event.get("data", {})

                            if etype == "SESSION_COMPLETED":
                                total_sessions += 1
                                total_duration += data.get("duration", 0.0)
                                total_files_changed += data.get("files_changed", 0)
                                total_lines_added += data.get("lines_added", 0)
                                total_lines_removed += data.get("lines_removed", 0)
                                if data.get("pr_url"):
                                    total_prs += 1
                            elif etype == "QA_RUN":
                                qa_runs += 1
                                if data.get("success"):
                                    qa_successes += 1
                            elif etype == "PR_MERGED":
                                total_prs += 1
                        except json.JSONDecodeError:
                            continue
            except Exception:
                return cls._empty_metrics()

        avg_duration = (total_duration / total_sessions) if total_sessions > 0 else 0.0
        qa_success_rate = (qa_successes / qa_runs * 100.0) if qa_runs > 0 else 0.0

        return {
            "total_sessions": total_sessions,
            "qa_success_rate": round(qa_success_rate, 2),
            "total_prs": total_prs,
            "avg_duration_seconds": round(avg_duration, 2),
            "total_files_changed": total_files_changed,
            "total_lines_added": total_lines_added,
            "total_lines_removed": total_lines_removed,
        }

    @staticmethod
    def _empty_metrics() -> Dict[str, Any]:
        return {
            "total_sessions": 0,
            "qa_success_rate": 0.0,
            "total_prs": 0,
            "avg_duration_seconds": 0.0,
            "total_files_changed": 0,
            "total_lines_added": 0,
            "total_lines_removed": 0,
        }

