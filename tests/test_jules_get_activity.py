import pytest
from unittest.mock import patch, MagicMock

from amb_cli.integrations.jules.jules_client import JulesClient

@pytest.fixture
def jules_client():
    with patch("amb_cli.integrations.jules.jules_client.require_env", return_value="dummy_key"):
        client = JulesClient(api_key="test_key")
        return client

def test_get_activity_simple_ids(jules_client):
    """Test get_activity with simple ID."""
    with patch.object(jules_client, "_request", return_value={"id": "act1"}) as mock_req:
        res = jules_client.get_activity("sess123", "act1")

        mock_req.assert_called_once_with("GET", "sessions/sess123/activities/act1")
        assert res == {"id": "act1"}

def test_get_activity_normalized_session_id(jules_client):
    """Test get_activity with normalized session ID."""
    with patch.object(jules_client, "_request", return_value={"id": "act1"}) as mock_req:
        res = jules_client.get_activity("sessions/sess123", "act1")

        mock_req.assert_called_once_with("GET", "sessions/sess123/activities/act1")
        assert res == {"id": "act1"}

def test_get_activity_with_path_in_activity_id(jules_client):
    """Test get_activity with full path in activity ID."""
    with patch.object(jules_client, "_request", return_value={"id": "act1"}) as mock_req:
        # Just activities/...
        res = jules_client.get_activity("sess123", "activities/act1")
        mock_req.assert_called_with("GET", "sessions/sess123/activities/act1")
        assert res == {"id": "act1"}

        # sessions/.../activities/...
        res = jules_client.get_activity("sess123", "sessions/sess123/activities/act1")
        mock_req.assert_called_with("GET", "sessions/sess123/activities/act1")
        assert res == {"id": "act1"}

def test_get_activity_error_propagation(jules_client):
    """Test get_activity propagates error on failed request."""
    with patch.object(jules_client, "_request", side_effect=Exception("HTTP 404")):
        with pytest.raises(Exception, match="HTTP 404"):
            jules_client.get_activity("sess123", "nonexistent")
