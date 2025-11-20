"""
Tests for routing logic.
"""

import pytest
import os
from unittest.mock import patch, MagicMock
from gateway.router import LLMRouter
from gateway.models import PIIDetection


def test_routing_decision_clean():
    """Test routing decision for clean prompts."""
    router = LLMRouter()
    router.pii_threshold = 0.3

    prompt = "What is the capital of Australia?"
    detections = []
    pii_score = 0.1

    # Mock the API calls
    with patch.object(router, "_call_openai", return_value="Canberra"):
        with patch.object(router, "_call_ollama"):
            response, route, _ = router.route_and_infer(prompt, detections, pii_score)

            assert route == "cloud"
            assert "Canberra" in response


def test_routing_decision_sensitive():
    """Test routing decision for sensitive prompts."""
    router = LLMRouter()
    router.pii_threshold = 0.3

    prompt = "My Medicare number is 1234 567 890"
    detections = [PIIDetection(type="medicare", value="1234***890", confidence=0.95)]
    pii_score = 0.8

    # Mock the API calls
    with patch.object(router, "_call_openai"):
        with patch.object(router, "_call_ollama", return_value="Response from local model"):
            response, route, _ = router.route_and_infer(prompt, detections, pii_score)

            assert route == "sovereign"
            assert "local model" in response


def test_pii_threshold():
    """Test that PII threshold affects routing."""
    router = LLMRouter()

    # Test with threshold at 0.5
    router.pii_threshold = 0.5
    prompt = "Test prompt"
    detections = []
    pii_score = 0.4  # Below threshold

    with patch.object(router, "_call_openai", return_value="Cloud response"):
        with patch.object(router, "_call_ollama"):
            _, route, _ = router.route_and_infer(prompt, detections, pii_score)
            assert route == "cloud"

    # Test with same score but threshold at 0.3
    router.pii_threshold = 0.3
    pii_score = 0.4  # Above threshold

    with patch.object(router, "_call_openai"):
        with patch.object(router, "_call_ollama", return_value="Local response"):
            _, route, _ = router.route_and_infer(prompt, detections, pii_score)
            assert route == "sovereign"
