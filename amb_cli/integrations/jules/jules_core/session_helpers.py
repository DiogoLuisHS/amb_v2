from typing import Dict, Any, List, Optional
import re

def normalize_session_id(session_id: str) -> str:
    """Normaliza strings de ID de sessão."""
    if not session_id:
        return ""
    raw = str(session_id).strip().rstrip("/")
    if "jules.google.com/session/" in raw:
        raw = raw.split("jules.google.com/session/")[-1].split("/")[0].split("?")[0]
    elif "sessions/" in raw:
        raw = raw.split("sessions/")[-1].split("/")[0].split("?")[0]
    return raw.strip()

def extract_pull_request(
    session_dict: Dict[str, Any],
    activities: Optional[List[Dict[str, Any]]] = None
) -> Optional[Dict[str, Any]]:
    """Extrai metadados do Pull Request."""
    outputs = session_dict.get("outputs", [])
    if isinstance(outputs, list):
        for item in outputs:
            if isinstance(item, dict) and "pullRequest" in item:
                pr_info = item["pullRequest"]
                if isinstance(pr_info, dict) and pr_info.get("url"):
                    return pr_info
    elif isinstance(outputs, dict) and "pullRequest" in outputs:
        pr_info = outputs["pullRequest"]
        if isinstance(pr_info, dict) and pr_info.get("url"):
            return pr_info

    if activities and isinstance(activities, list):
        for act in activities:
            txt = str(act)
            m = re.search(r"(https://github\.com/[^/]+/[^/]+/pull/(\d+))", txt)
            if m:
                return {
                    "url": m.group(1),
                    "number": int(m.group(2))
                }

    return None

def compute_status(sources: List[Dict[str, Any]], sessions: List[Dict[str, Any]], key: str, target_repo: str) -> Dict[str, Any]:
    status: Dict[str, Any] = {
        "api_key_configured": bool(key),
        "api_reachable": True,
        "sources_count": len(sources),
        "active_repo": target_repo,
        "repo_connected": False,
        "sessions_total": len(sessions),
        "sessions_awaiting_feedback": 0,
        "sessions_in_progress": 0,
        "sessions_completed": 0,
        "sessions_failed": 0,
        "error": None,
    }

    if target_repo:
        target_norm = target_repo.lower().strip()
        status["repo_connected"] = any(
            target_norm in (s.get("name") or "").lower() for s in sources
        )

    for s in sessions:
        st = (s.get("state") or "UNKNOWN").upper()
        if "AWAITING" in st:
            status["sessions_awaiting_feedback"] += 1
        elif "IN_PROGRESS" in st or "RUNNING" in st or "STARTING" in st:
            status["sessions_in_progress"] += 1
        elif "COMPLETED" in st or "SUCCEEDED" in st:
            status["sessions_completed"] += 1
        elif "FAIL" in st or "CANCEL" in st:
            status["sessions_failed"] += 1

    return status
