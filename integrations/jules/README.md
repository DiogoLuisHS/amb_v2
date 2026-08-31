# Jules Integration

This directory contains the integration with the Jules API.

## Tools

### `approve_plan.py`

This script is used to approve a plan in a Jules session.

**Validation Rule (Guardrail):**
To ensure a plan actually exists before blindly attempting to approve it, `approve_plan.py` includes a guardrail.
Before approving a plan, the script fetches the session's activities and examines the most recent one (determined by `createTime`).
It verifies that the `originator` of this activity is 'agent' and that it contains a `planGenerated` key.
If these conditions are not met, or if there are no activities, the script will abort and return the following error message:
> "Error: There is no pending plan to approve."

**Usage:**
```bash
python3 tools/approve_plan.py --session-id <session_id>
```

### `send_message.py`

This script is used to send a message to a Jules session.

**Validation Rule (Guardrail):**
To prevent confusing the session state by sending consecutive messages before the agent has replied, `send_message.py` includes a guardrail.
Before sending a message, the script checks the most recent activity in the session. If the most recent activity was originated by the user, the script will abort and return the following error message:
> "Error: Please wait for the agent to reply before sending another message."

It allows the message to be sent if the originator is 'agent', 'system', or if there are no prior activities.

**Usage:**
```bash
python3 tools/send_message.py --session-id <session_id> --message "<your message>"
```

### `jules_client.py`

This is the main REST API client for interacting with Jules.

### `cleanup_sessions.py`

This script is used to audit and safely clean up Jules sessions for the current repository.

**Validation Rule (Guardrail):**
To prevent accidentally deleting a session that is still running, `cleanup_sessions.py` includes a state validation guardrail.
Before deleting a session, it verifies that the session is in a terminal state (`COMPLETED`, `SUCCEEDED`, `FAILED`, or `CANCELED`).
If a session is in an active state like `RUNNING` or `PENDING`, the script will log a skip message and safely ignore it. This rule is enforced across all deletion methods, including bulk operations and explicit ID targeting (`--delete-id`).

**Usage:**
```bash
# Simulate deletion of sessions with merged PRs
python3 tools/cleanup_sessions.py --delete-merged --dry-run

# Delete sessions with merged PRs
python3 tools/cleanup_sessions.py --delete-merged

# Delete all completed sessions (merged or unmerged)
python3 tools/cleanup_sessions.py --delete-all-completed

# Delete a specific session by ID
python3 tools/cleanup_sessions.py --delete-id <session_id>
```
