"""
Configuration management for the Sovereign AI Gateway.
"""

import os
from typing import Optional, List

# Try pydantic_settings, fallback to BaseSettings for compatibility
try:
    from pydantic_settings import BaseSettings
    from pydantic import Field, field_validator, ConfigDict

    PYDANTIC_V2 = True
except ImportError:
    from pydantic import BaseSettings, Field, validator

    PYDANTIC_V2 = False


class GatewayConfig(BaseSettings):
    """
    Gateway configuration with validation.

    Uses environment variables for configuration with sensible defaults.
    Environment variables are automatically loaded from .env file if present.
    """

    # OpenAI Configuration
    openai_api_key: Optional[str] = None
    openai_base_url: str = "https://api.openai.com/v1"
    openai_model: str = "gpt-4o"
    openai_timeout: int = 30
    openai_max_tokens: int = 1000

    # Ollama Configuration
    ollama_base_url: str = "http://ollama:11434"
    ollama_model: str = "llama3"
    ollama_timeout: int = 60

    # Routing Configuration
    pii_threshold: float = Field(0.3, ge=0.0, le=1.0)

    # Gateway Configuration
    gateway_host: str = "0.0.0.0"
    gateway_port: int = 8000
    gateway_log_level: str = "INFO"

    # Security Configuration
    max_request_size: int = 1024 * 1024  # 1MB default
    enable_cors: bool = True
    cors_origins: List[str] = ["*"]

    # Logging Configuration
    audit_log_file: str = "sovereign_audit.log"
    audit_log_level: str = "INFO"

    # Rate Limiting (for future implementation)
    rate_limit_enabled: bool = False
    rate_limit_per_minute: int = 60

    if PYDANTIC_V2:

        @field_validator("cors_origins", mode="before")
        @classmethod
        def parse_cors_origins(cls, v):
            """Parse CORS origins from string or list."""
            if isinstance(v, str):
                return [origin.strip() for origin in v.split(",")]
            return v

        @field_validator("gateway_log_level", "audit_log_level")
        @classmethod
        def validate_log_level(cls, v):
            """Validate log level."""
            valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
            if v.upper() not in valid_levels:
                raise ValueError(f"Log level must be one of {valid_levels}")
            return v.upper()

        model_config = ConfigDict(
            env_file=".env", env_file_encoding="utf-8", case_sensitive=False, extra="ignore"
        )
    else:

        @validator("cors_origins", pre=True)
        def parse_cors_origins(cls, v):
            """Parse CORS origins from string or list."""
            if isinstance(v, str):
                return [origin.strip() for origin in v.split(",")]
            return v

        @validator("gateway_log_level", "audit_log_level")
        def validate_log_level(cls, v):
            """Validate log level."""
            valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
            if v.upper() not in valid_levels:
                raise ValueError(f"Log level must be one of {valid_levels}")
            return v.upper()

        class Config:
            env_file = ".env"
            env_file_encoding = "utf-8"
            case_sensitive = False


# Global configuration instance
# Load from environment variables
config = GatewayConfig(_env_file=".env", _env_file_encoding="utf-8")

# Override with environment variables if present
for key in [
    "OPENAI_API_KEY",
    "OPENAI_BASE_URL",
    "OPENAI_MODEL",
    "OPENAI_TIMEOUT",
    "OPENAI_MAX_TOKENS",
    "OLLAMA_BASE_URL",
    "OLLAMA_MODEL",
    "OLLAMA_TIMEOUT",
    "PII_THRESHOLD",
    "GATEWAY_HOST",
    "GATEWAY_PORT",
    "GATEWAY_LOG_LEVEL",
    "MAX_REQUEST_SIZE",
    "ENABLE_CORS",
    "CORS_ORIGINS",
    "AUDIT_LOG_FILE",
    "AUDIT_LOG_LEVEL",
    "RATE_LIMIT_ENABLED",
    "RATE_LIMIT_PER_MINUTE",
]:
    env_value = os.getenv(key)
    if env_value is not None:
        # Convert to appropriate type
        attr_name = key.lower()
        if (
            key.endswith("_TIMEOUT")
            or key.endswith("_PORT")
            or key.endswith("_SIZE")
            or key.endswith("_PER_MINUTE")
        ):
            setattr(config, attr_name, int(env_value))
        elif key.endswith("_THRESHOLD"):
            setattr(config, attr_name, float(env_value))
        elif key in ["ENABLE_CORS", "RATE_LIMIT_ENABLED"]:
            setattr(config, attr_name, env_value.lower() in ["true", "1", "yes"])
        else:
            setattr(config, attr_name, env_value)
