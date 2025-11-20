"""
Tests for PII Inspector module.
"""

import pytest

from gateway.inspector import AustralianPIIInspector


def test_medicare_detection():
    """Test Medicare number detection."""
    inspector = AustralianPIIInspector()
    text = "My Medicare number is 1234 567 890"
    detections, score = inspector.detect_pii(text)

    assert len(detections) > 0
    assert any(d.type == "medicare" for d in detections)
    assert score > 0


def test_tfn_detection():
    """Test TFN detection."""
    inspector = AustralianPIIInspector()
    text = "My TFN is 123456789"
    detections, score = inspector.detect_pii(text)

    assert len(detections) > 0
    assert any(d.type == "tfn" for d in detections)
    assert score > 0


def test_mobile_detection():
    """Test Australian mobile number detection."""
    inspector = AustralianPIIInspector()
    text = "Call me on 0412 345 678"
    detections, score = inspector.detect_pii(text)

    assert len(detections) > 0
    assert any(d.type == "mobile" for d in detections)
    assert score > 0


def test_sensitive_keywords():
    """Test sensitive keyword detection."""
    inspector = AustralianPIIInspector()
    text = "I need medical advice about my diagnosis"
    detections, score = inspector.detect_pii(text)

    assert score > 0


def test_clean_text():
    """Test that clean text has low PII score."""
    inspector = AustralianPIIInspector()
    text = "What is the capital of Australia?"
    detections, score = inspector.detect_pii(text)

    assert score < 0.3


def test_multiple_pii():
    """Test detection of multiple PII types."""
    inspector = AustralianPIIInspector()
    text = "My Medicare is 1234 567 890 and my TFN is 123456789"
    detections, score = inspector.detect_pii(text)

    assert len(detections) >= 2
    assert score > 0.5
