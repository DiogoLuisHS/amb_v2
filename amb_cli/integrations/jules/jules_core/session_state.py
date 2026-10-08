from enum import Enum

class SessionState(str, Enum):
    IDLE = "IDLE"
    IN_PROGRESS = "IN_PROGRESS"
    AWAITING_INPUT = "AWAITING_INPUT"
    AWAITING_PLAN_APPROVAL = "AWAITING_PLAN_APPROVAL"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"

    def is_terminal(self) -> bool:
        return self in (SessionState.COMPLETED, SessionState.FAILED)

    def is_awaiting_feedback(self) -> bool:
        return self in (SessionState.AWAITING_INPUT, SessionState.AWAITING_PLAN_APPROVAL)

    def is_success(self) -> bool:
        return self == SessionState.COMPLETED

    @classmethod
    def from_api_string(cls, raw: str) -> "SessionState":
        normalized = (raw or "").upper().strip()
        if normalized in ("COMPLETED", "SUCCEEDED", "CLOSED"):
            return cls.COMPLETED
        if normalized in ("FAILED", "ERROR", "ABORTED", "CANCELLED"):
            return cls.FAILED
        if normalized in ("AWAITING_INPUT", "AWAITING_USER_INPUT", "AWAITING_USER_FEEDBACK"):
            return cls.AWAITING_INPUT
        if normalized in ("AWAITING_PLAN_APPROVAL", "PLAN_PENDING"):
            return cls.AWAITING_PLAN_APPROVAL
        if normalized in ("IN_PROGRESS", "RUNNING", "PLANNING", "EXECUTING", "STARTING"):
            return cls.IN_PROGRESS
        return cls.IDLE

    @staticmethod
    def extract_metrics(session_dict: dict, duration_seconds: float = 0.0) -> dict:
        """Extrai métricas consolidadas (arquivos alterados, linhas +/- e runtime) da sessão."""
        outputs = session_dict.get("outputs", [])
        if isinstance(outputs, dict):
            outputs = [outputs]

        files_changed = 0
        lines_added = 0
        lines_removed = 0
        pr_url = None

        for item in outputs:
            if not isinstance(item, dict):
                continue
            pr_info = item.get("pullRequest")
            if isinstance(pr_info, dict) and pr_info.get("url"):
                pr_url = pr_info["url"]

            change_set = item.get("changeSet")
            if isinstance(change_set, dict):
                f_list = change_set.get("filesChanged", [])
                if isinstance(f_list, list) and f_list:
                    files_changed = max(files_changed, len(f_list))

                git_patch = change_set.get("gitPatch", {})
                if isinstance(git_patch, dict):
                    diff = git_patch.get("unidiffPatch", "")
                    if diff:
                        diff_files = set()
                        for line in diff.splitlines():
                            if line.startswith("+++ b/"):
                                diff_files.add(line[6:].strip())
                            elif line.startswith("+") and not line.startswith("+++"):
                                lines_added += 1
                            elif line.startswith("-") and not line.startswith("---"):
                                lines_removed += 1
                        if diff_files and files_changed == 0:
                            files_changed = len(diff_files)

        sess_id = session_dict.get("id") or session_dict.get("name", "").split("/")[-1]
        state = session_dict.get("state", "UNKNOWN")

        return {
            "session_id": sess_id,
            "state": state,
            "runtime": round(duration_seconds, 2),
            "files_changed": files_changed,
            "lines_added": lines_added,
            "lines_removed": lines_removed,
            "pr_url": pr_url,
        }

