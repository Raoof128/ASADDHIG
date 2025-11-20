"""
Integration tests for the complete gateway flow.
"""
import pytest
from gateway.inspector import AustralianPIIInspector
from gateway.router import LLMRouter
from gateway.logging_utils import ComplianceLogger
from gateway.models import GatewayRequest
import tempfile
import os


@pytest.fixture
def inspector():
    """Create inspector instance."""
    return AustralianPIIInspector()


@pytest.fixture
def router():
    """Create router instance."""
    return LLMRouter()


@pytest.fixture
def temp_logger():
    """Create logger with temp file."""
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.log') as f:
        temp_path = f.name
    
    logger = ComplianceLogger(log_file=temp_path)
    yield logger
    
    # Cleanup
    if os.path.exists(temp_path):
        os.unlink(temp_path)


def test_complete_flow_clean_prompt(inspector, router, temp_logger):
    """Test complete flow with clean prompt."""
    prompt = "What is the capital of Australia?"
    
    # Step 1: Detect PII
    pii_detections, pii_score = inspector.detect_pii(prompt)
    assert pii_score < 0.3  # Should be low
    
    # Step 2: Route (will try cloud first, fallback to local)
    response, route, processing_time = router.route_and_infer(
        prompt=prompt,
        pii_detections=pii_detections,
        pii_score=pii_score
    )
    
    assert isinstance(response, str)
    assert route in ["cloud", "sovereign"]
    assert processing_time >= 0
    
    # Step 3: Log
    temp_logger.log_request(
        route=route,
        pii_score=pii_score,
        pii_types=[d.type for d in pii_detections],
        model_used=router.get_model_name(route),
        prompt_length=len(prompt),
        response_length=len(response),
        processing_time_ms=processing_time
    )


def test_complete_flow_sensitive_prompt(inspector, router, temp_logger):
    """Test complete flow with sensitive prompt."""
    prompt = "My Medicare number is 1234 567 890 and my TFN is 123456789"
    
    # Step 1: Detect PII
    pii_detections, pii_score = inspector.detect_pii(prompt)
    assert pii_score >= 0.3  # Should be high
    assert len(pii_detections) > 0
    
    # Step 2: Route (should go to local)
    response, route, processing_time = router.route_and_infer(
        prompt=prompt,
        pii_detections=pii_detections,
        pii_score=pii_score
    )
    
    assert isinstance(response, str)
    assert route == "sovereign"  # Should route to local
    assert processing_time >= 0
    
    # Step 3: Log
    temp_logger.log_request(
        route=route,
        pii_score=pii_score,
        pii_types=[d.type for d in pii_detections],
        model_used=router.get_model_name(route),
        prompt_length=len(prompt),
        response_length=len(response),
        processing_time_ms=processing_time
    )


def test_gateway_request_model():
    """Test GatewayRequest model."""
    request = GatewayRequest(
        prompt="Test prompt",
        user_id="user123",
        session_id="session456"
    )
    
    assert request.prompt == "Test prompt"
    assert request.user_id == "user123"
    assert request.session_id == "session456"


def test_pii_detection_redaction(inspector):
    """Test that PII values are properly redacted."""
    prompt = "My Medicare is 1234567890"
    detections, _ = inspector.detect_pii(prompt)
    
    assert len(detections) > 0
    for detection in detections:
        if detection.type == "medicare":
            # Value should be redacted (contains asterisks)
            assert "*" in detection.value
            # Redacted value should not be the original
            assert detection.value != "1234567890"

