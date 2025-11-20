"""
Data models for the Sovereign AI Gateway.
"""

from datetime import datetime
from typing import List, Literal, Optional

from pydantic import BaseModel, Field


class GatewayRequest(BaseModel):
    """Request model for the gateway endpoint."""

    prompt: str = Field(..., description="User prompt to be processed")
    user_id: Optional[str] = Field(None, description="Optional user identifier")
    session_id: Optional[str] = Field(None, description="Optional session identifier")


class PIIDetection(BaseModel):
    """PII detection result."""

    type: str = Field(..., description="Type of PII detected")
    value: str = Field(..., description="Detected value (may be redacted)")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Detection confidence score")
    position: Optional[tuple] = Field(None, description="Position in text (start, end)")


class GatewayResponse(BaseModel):
    """Response model from the gateway endpoint."""

    response: str = Field(..., description="AI model response")
    route: Literal["cloud", "sovereign"] = Field(..., description="Routing decision")
    pii_score: float = Field(..., ge=0.0, le=1.0, description="PII sensitivity score")
    pii_detected: List[PIIDetection] = Field(
        default_factory=list, description="List of detected PII"
    )
    model_used: str = Field(..., description="Model that generated the response")
    timestamp: datetime = Field(default_factory=datetime.now, description="Response timestamp")
    processing_time_ms: Optional[float] = Field(None, description="Processing time in milliseconds")


class AuditLogEntry(BaseModel):
    """Audit log entry for compliance."""

    timestamp: datetime = Field(default_factory=datetime.now)
    route: Literal["cloud", "sovereign"]
    pii_score: float
    pii_types: List[str]
    model_used: str
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    ip_address: Optional[str] = None
    prompt_length: int
    response_length: int
    processing_time_ms: float
