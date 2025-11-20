"""
Tests for configuration management.
"""

import pytest

from gateway.config import GatewayConfig, config


def test_config_defaults():
    """Test that config has sensible defaults."""
    assert config.pii_threshold == 0.3
    assert config.gateway_port == 8000
    assert config.max_request_size == 1024 * 1024
    assert config.enable_cors is True


def test_config_environment_variable(monkeypatch):
    """Test that environment variables override defaults."""
    monkeypatch.setenv("PII_THRESHOLD", "0.5")
    monkeypatch.setenv("GATEWAY_PORT", "9000")

    # Create new config instance to pick up env vars
    test_config = GatewayConfig()
    assert test_config.pii_threshold == 0.5
    assert test_config.gateway_port == 9000


def test_config_pii_threshold_validation():
    """Test that PII threshold is validated."""
    with pytest.raises(ValueError):
        GatewayConfig(pii_threshold=-0.1)

    with pytest.raises(ValueError):
        GatewayConfig(pii_threshold=1.5)


def test_config_log_level_validation():
    """Test that log levels are validated."""
    with pytest.raises(ValueError):
        GatewayConfig(gateway_log_level="INVALID")

    # Valid levels should work
    valid_config = GatewayConfig(gateway_log_level="DEBUG")
    assert valid_config.gateway_log_level == "DEBUG"


def test_config_cors_origins_parsing():
    """Test that CORS origins are parsed correctly."""
    # Test string parsing
    test_config = GatewayConfig(cors_origins="http://localhost:3000,http://localhost:8080")
    assert len(test_config.cors_origins) == 2
    assert "http://localhost:3000" in test_config.cors_origins

    # Test list
    test_config2 = GatewayConfig(cors_origins=["http://localhost:3000"])
    assert test_config2.cors_origins == ["http://localhost:3000"]
