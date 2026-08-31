# Jules Integration

This directory contains the integration with the Jules API.

## Tools

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
