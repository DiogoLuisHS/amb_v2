import sys
import os
import json
from typing import Dict, Any, Optional

from core.bootstrap import ensure_amb_env
ensure_amb_env()

from core import Colors, log, log_error
from integrations.jules.jules_client import JulesClient
from integrations.jules.tools.create_session import run_create_session

def run_rerun_session(
    session_id: str,
    new_prompt: Optional[str] = None,
    new_branch: Optional[str] = None,
    as_json: bool = False
) -> Dict[str, Any]:
    """Recria e reinicia uma sessão anterior preservando prompt e contexto."""
    client = JulesClient()
    clean_id = client.normalize_session_id(session_id)

    try:
        sess = client.get_session(clean_id)
    except Exception as e:
        err_str = str(e)
        if "404" in err_str or "NOT_FOUND" in err_str or "not found" in err_str.lower():
            if as_json:
                print(json.dumps({"error": "Sessão não encontrada", "details": err_str}))
            else:
                log_error("JULES", f"Sessão '{clean_id}' não encontrada na nuvem.")
            return {}
        raise

    prompt = new_prompt
    if not prompt:
        prompt = sess.get("prompt")
        if not prompt:
            try:
                activities_data = client.list_activities(clean_id, page_size=5, fetch_all=False)
                activities = activities_data.get("activities", []) if isinstance(activities_data, dict) else (activities_data if isinstance(activities_data, list) else [])
                for act in activities:
                    if act.get("type") == "PROMPT" and act.get("prompt"):
                        prompt = act.get("prompt")
                        break
            except Exception as e:
                pass

        if not prompt:
            if as_json:
                print(json.dumps({"error": "Não foi possível recuperar o prompt original da sessão."}))
            else:
                log_error("JULES", "Não foi possível recuperar o prompt original da sessão. Tente usar --prompt para forçar um novo prompt.")
            return {}

    source_context = sess.get("sourceContext", {})
    git_context = source_context.get("gitContext", {})
    source_name = source_context.get("source")

    branch = new_branch or git_context.get("targetBranch")

    old_title = sess.get("title", "Sessão sem título")
    title = f"[Rerun] {old_title}"

    if not as_json:
        log("JULES", f"Reiniciando sessão: {clean_id} -> {title}", Colors.CYAN)

    return run_create_session(
        prompt=prompt,
        title=title,
        base_branch=branch,
        source_name=source_name,
        as_json=as_json,
        client=client
    )
