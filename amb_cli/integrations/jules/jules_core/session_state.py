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
