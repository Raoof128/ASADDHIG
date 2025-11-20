"""
Edge case tests for PII Inspector.
"""

import pytest

from gateway.inspector import AustralianPIIInspector


def test_detect_pii_empty_string():
    """Test PII detection with empty string."""
    inspector = AustralianPIIInspector()
    detections, score = inspector.detect_pii("")
    assert len(detections) == 0
    assert score == 0.0


def test_detect_pii_none():
    """Test PII detection with None (should raise TypeError)."""
    inspector = AustralianPIIInspector()
    with pytest.raises(TypeError):
        inspector.detect_pii(None)


def test_detect_pii_non_string():
    """Test PII detection with non-string input."""
    inspector = AustralianPIIInspector()
    with pytest.raises(TypeError):
        inspector.detect_pii(123)


def test_detect_pii_very_long_text():
    """Test PII detection with very long text."""
    inspector = AustralianPIIInspector()
    long_text = "This is a test. " * 1000 + "My Medicare number is 1234 567 890"
    detections, score = inspector.detect_pii(long_text)
    assert len(detections) > 0
    assert score > 0


def test_detect_pii_special_characters():
    """Test PII detection with special characters."""
    inspector = AustralianPIIInspector()
    text = "Contact me at test@example.com or call 0412 345 678"
    detections, score = inspector.detect_pii(text)
    # Should detect email and mobile
    assert len(detections) >= 1
    assert score > 0


def test_detect_pii_multiple_medicare():
    """Test detection of multiple Medicare numbers."""
    inspector = AustralianPIIInspector()
    text = "Medicare 1234 567 890 and also 9876 543 210"
    detections, score = inspector.detect_pii(text)
    assert len(detections) >= 2
    assert score > 0.5


def test_detect_pii_whitespace_only():
    """Test PII detection with whitespace-only string."""
    inspector = AustralianPIIInspector()
    detections, score = inspector.detect_pii("   \n\t   ")
    assert len(detections) == 0
    assert score == 0.0


def test_redact_value_short():
    """Test redaction of very short values."""
    inspector = AustralianPIIInspector()
    result = inspector._redact_value("123", "medicare")
    assert result == "****"


def test_redact_value_empty():
    """Test redaction of empty value."""
    inspector = AustralianPIIInspector()
    result = inspector._redact_value("", "medicare")
    assert result == "****"


def test_validate_medicare_invalid_format():
    """Test Medicare validation with invalid format."""
    inspector = AustralianPIIInspector()
    assert inspector._validate_medicare("123") is False
    assert inspector._validate_medicare("123456789012") is False


def test_validate_tfn_invalid_format():
    """Test TFN validation with invalid format."""
    inspector = AustralianPIIInspector()
    assert inspector._validate_tfn("123") is False
    assert inspector._validate_tfn("123456789012") is False
