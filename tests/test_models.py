"""
Tests for data models.
"""

from datetime import datetime

import pytest

from gateway.models import AuditLogEntry, GatewayRequest, GatewayResponse, PIIDetection


def test_gateway_request_valid():
    """Test valid GatewayRequest."""
    request = GatewayRequest(prompt="Test prompt")
    assert request.prompt == "Test prompt"
    assert request.user_id is None
    assert request.session_id is None


def test_gateway_request_with_metadata():
    """Test GatewayRequest with optional fields."""
    request = GatewayRequest(prompt="Test", user_id="user123", session_id="session456")
    assert request.user_id == "user123"
    assert request.session_id == "session456"


def test_gateway_request_empty_prompt():
    """Test GatewayRequest validation."""
    # Empty prompt should be allowed by model (validation happens in gateway)
    request = GatewayRequest(prompt="")
    assert request.prompt == ""


def test_pii_detection_valid():
    """Test valid PIIDetection."""
    detection = PIIDetection(type="medicare", value="12****890", confidence=0.95)
    assert detection.type == "medicare"
    assert detection.confidence == 0.95


def test_pii_detection_confidence_validation():
    """Test PIIDetection confidence validation."""
    # Valid confidence
    detection = PIIDetection(type="tfn", value="123****", confidence=0.5)
    assert detection.confidence == 0.5

    # Invalid confidence (too high)
    with pytest.raises(Exception):  # Pydantic validation error
        PIIDetection(type="tfn", value="123****", confidence=1.5)

    # Invalid confidence (negative)
    with pytest.raises(Exception):
        PIIDetection(type="tfn", value="123****", confidence=-0.1)


def test_gateway_response_valid():
    """Test valid GatewayResponse."""
    response = GatewayResponse(
        response="AI response", route="cloud", pii_score=0.2, model_used="gpt-4o"
    )
    assert response.response == "AI response"
    assert response.route == "cloud"
    assert response.pii_score == 0.2
    assert isinstance(response.timestamp, datetime)


def test_gateway_response_pii_score_validation():
    """Test GatewayResponse PII score validation."""
    # Valid score
    response = GatewayResponse(
        response="Test", route="sovereign", pii_score=0.8, model_used="llama3"
    )
    assert response.pii_score == 0.8

    # Invalid score
    with pytest.raises(Exception):
        GatewayResponse(response="Test", route="cloud", pii_score=1.5, model_used="gpt-4o")


def test_audit_log_entry_valid():
    """Test valid AuditLogEntry."""
    entry = AuditLogEntry(
        route="sovereign",
        pii_score=0.85,
        pii_types=["medicare", "tfn"],
        model_used="llama3",
        prompt_length=100,
        response_length=500,
        processing_time_ms=1250.5,
    )
    assert entry.route == "sovereign"
    assert entry.pii_score == 0.85
    assert len(entry.pii_types) == 2
    assert isinstance(entry.timestamp, datetime)
