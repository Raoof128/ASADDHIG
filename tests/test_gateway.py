"""
Integration tests for the FastAPI gateway.
"""
import pytest
from fastapi.testclient import TestClient
from gateway.gateway import app


@pytest.fixture
def client():
    """Create a test client."""
    # TestClient needs to be imported correctly
    try:
        from fastapi.testclient import TestClient
        return TestClient(app)
    except ImportError:
        # Fallback for older versions
        from starlette.testclient import TestClient
        return TestClient(app)


def test_root_endpoint(client):
    """Test root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["service"] == "Sovereign AI Gateway"
    assert data["status"] == "operational"


def test_health_endpoint(client):
    """Test health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "components" in data


def test_gateway_endpoint_clean_prompt(client):
    """Test gateway endpoint with clean prompt."""
    payload = {
        "prompt": "What is the capital of Australia?",
        "user_id": "test_user",
        "session_id": "test_session"
    }
    
    response = client.post("/gateway", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "response" in data
    assert "route" in data
    assert "pii_score" in data
    assert data["route"] in ["cloud", "sovereign"]


def test_gateway_endpoint_sensitive_prompt(client):
    """Test gateway endpoint with sensitive prompt."""
    payload = {
        "prompt": "My Medicare number is 1234 567 890",
        "user_id": "test_user"
    }
    
    response = client.post("/gateway", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "response" in data
    assert data["pii_score"] > 0
    assert len(data["pii_detected"]) > 0


def test_gateway_endpoint_empty_prompt(client):
    """Test gateway endpoint with empty prompt."""
    payload = {"prompt": ""}
    
    response = client.post("/gateway", json=payload)
    assert response.status_code == 400


def test_gateway_endpoint_missing_prompt(client):
    """Test gateway endpoint with missing prompt."""
    payload = {}
    
    response = client.post("/gateway", json=payload)
    assert response.status_code == 422


def test_audit_endpoint(client):
    """Test audit log endpoint."""
    response = client.get("/audit/recent")
    assert response.status_code == 200
    data = response.json()
    assert "logs" in data
    assert "count" in data
    assert isinstance(data["logs"], list)


def test_audit_endpoint_with_limit(client):
    """Test audit log endpoint with custom limit."""
    response = client.get("/audit/recent?limit=10")
    assert response.status_code == 200
    data = response.json()
    assert data["limit"] == 10


def test_audit_endpoint_invalid_limit(client):
    """Test audit log endpoint with invalid limit."""
    response = client.get("/audit/recent?limit=0")
    assert response.status_code == 400
    
    response = client.get("/audit/recent?limit=2000")
    assert response.status_code == 400

