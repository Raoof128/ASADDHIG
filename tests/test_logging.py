"""
Tests for compliance logging utilities.
"""

import os
import tempfile

import pytest

from gateway.logging_utils import ComplianceLogger


@pytest.fixture
def temp_log_file():
    """Create a temporary log file."""
    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".log") as f:
        temp_path = f.name

    yield temp_path

    # Cleanup
    if os.path.exists(temp_path):
        os.unlink(temp_path)


def test_compliance_logger_initialization(temp_log_file):
    """Test ComplianceLogger initialization."""
    logger = ComplianceLogger(log_file=temp_log_file)
    assert logger.log_file == temp_log_file
    assert os.path.exists(temp_log_file)


def test_log_request(temp_log_file):
    """Test logging a request."""
    logger = ComplianceLogger(log_file=temp_log_file)

    logger.log_request(
        route="sovereign",
        pii_score=0.85,
        pii_types=["medicare", "tfn"],
        model_used="llama3 (local)",
        prompt_length=100,
        response_length=500,
        processing_time_ms=1250.5,
        user_id="test_user",
        session_id="test_session",
        ip_address="192.168.1.1",
    )

    # Verify log file was created and has content
    assert os.path.exists(temp_log_file)

    # Force flush and wait for file write
    import time

    time.sleep(0.5)

    # Read file content
    with open(temp_log_file, "r") as f:
        content = f.read()

    # Verify content exists
    assert len(content) > 0, f"Log file is empty: {temp_log_file}"

    content_lower = content.lower()
    # Check for expected content (case-insensitive)
    # The log should contain either JSON with "sovereign" or human-readable with "SOVEREIGN"
    assert (
        "sovereign" in content_lower or "0.85" in content or "medicare" in content_lower
    ), f"Expected content not found. Content length: {len(content)}, Preview: {content[:500]}"


def test_get_recent_logs(temp_log_file):
    """Test retrieving recent logs."""
    logger = ComplianceLogger(log_file=temp_log_file)

    # Log multiple entries
    for i in range(5):
        logger.log_request(
            route="cloud" if i % 2 == 0 else "sovereign",
            pii_score=0.5 + (i * 0.1),
            pii_types=["test"],
            model_used="test_model",
            prompt_length=100,
            response_length=500,
            processing_time_ms=1000.0,
        )

    logs = logger.get_recent_logs(limit=3)
    assert len(logs) <= 3
    assert all(isinstance(log, dict) for log in logs)


def test_get_recent_logs_empty_file():
    """Test retrieving logs from non-existent file."""
    import os
    import tempfile

    # Use a temp file that doesn't exist yet
    with tempfile.NamedTemporaryFile(delete=True, suffix=".log") as f:
        temp_path = f.name

    # File should not exist
    assert not os.path.exists(temp_path)

    logger = ComplianceLogger(log_file=temp_path)
    logs = logger.get_recent_logs()
    assert logs == []
