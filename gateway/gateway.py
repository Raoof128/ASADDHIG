"""
FastAPI Gateway for Sovereign AI - Australian Data Sovereignty Enforcement.

This module provides the main FastAPI application for the Sovereign AI Gateway,
which enforces Australian data sovereignty by routing sensitive prompts to local
LLMs while allowing non-sensitive prompts to use cloud AI models.
"""
import logging
import time
from typing import Optional

from fastapi import FastAPI, Request, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError

from .models import GatewayRequest, GatewayResponse
from .inspector import AustralianPIIInspector
from .router import LLMRouter
from .logging_utils import ComplianceLogger
from .config import config

# Configure logging
logging.basicConfig(
    level=getattr(logging, config.gateway_log_level),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Initialize FastAPI application
app = FastAPI(
    title="Sovereign AI Gateway",
    description="Australian Data Sovereignty Enforcement Gateway",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# CORS middleware configuration
if config.enable_cors:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=config.cors_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "OPTIONS"],
        allow_headers=["*"],
        max_age=3600,
    )

# Initialize services
inspector = AustralianPIIInspector()
router = LLMRouter()
audit_logger = ComplianceLogger(log_file=config.audit_log_file)

logger.info("Sovereign AI Gateway initialized")
logger.info(f"PII Threshold: {config.pii_threshold}")
logger.info(f"OpenAI Model: {config.openai_model}")
logger.info(f"Ollama Model: {config.ollama_model}")


# Exception handlers
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle request validation errors."""
    logger.warning(f"Validation error: {exc.errors()}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": "Validation error",
            "details": exc.errors(),
            "message": "Invalid request format"
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle general exceptions."""
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Internal server error",
            "message": "An unexpected error occurred"
        }
    )


def get_client_ip(request: Request) -> Optional[str]:
    """
    Extract client IP address from request.
    
    Args:
        request: FastAPI request object
        
    Returns:
        Client IP address or None if not available
    """
    # Check for forwarded IP (behind proxy)
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    
    if request.client:
        return request.client.host
    return None


@app.get("/", tags=["Health"])
async def root():
    """
    Root endpoint - basic health check.
    
    Returns:
        Basic service information
    """
    return {
        "service": "Sovereign AI Gateway",
        "status": "operational",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }


@app.get("/health", tags=["Health"])
async def health():
    """
    Detailed health check endpoint.
    
    Returns:
        Health status of all components
    """
    health_status = {
        "status": "healthy",
        "timestamp": time.time(),
        "components": {
            "inspector": "operational",
            "router": "operational",
            "audit_logger": "operational"
        },
        "configuration": {
            "pii_threshold": config.pii_threshold,
            "openai_configured": bool(config.openai_api_key),
            "ollama_url": config.ollama_base_url
        }
    }
    
    return health_status


@app.post("/gateway", response_model=GatewayResponse, tags=["Gateway"])
async def gateway_endpoint(request: GatewayRequest, http_request: Request):
    """
    Main gateway endpoint for AI inference requests.
    
    This endpoint processes prompts through the following pipeline:
    1. Validates and inspects the prompt for Australian PII
    2. Routes to cloud (OpenAI) or sovereign (local Ollama) based on sensitivity
    3. Logs the decision for compliance auditing
    4. Returns the AI response with routing metadata
    
    Args:
        request: Gateway request containing prompt and optional metadata
        http_request: FastAPI request object for extracting client information
        
    Returns:
        GatewayResponse with AI response and routing metadata
        
    Raises:
        HTTPException: If processing fails or request is invalid
    """
    start_time = time.time()
    client_ip = get_client_ip(http_request)
    
    try:
        # Input validation
        if not request.prompt or not request.prompt.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Prompt cannot be empty"
            )
        
        # Check request size
        prompt_size = len(request.prompt.encode('utf-8'))
        if prompt_size > config.max_request_size:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"Request size ({prompt_size} bytes) exceeds maximum ({config.max_request_size} bytes)"
            )
        
        logger.info(f"Processing request from {client_ip}, prompt length: {len(request.prompt)}")
        
        # Step 1: Inspect for PII
        pii_detections, pii_score = inspector.detect_pii(request.prompt)
        pii_types = [det.type for det in pii_detections]
        
        logger.debug(f"PII detection complete: score={pii_score:.2f}, types={pii_types}")
        
        # Step 2: Route and get inference
        response_text, route, processing_time = router.route_and_infer(
            prompt=request.prompt,
            pii_detections=pii_detections,
            pii_score=pii_score
        )
        
        # Step 3: Get model name
        model_used = router.get_model_name(route)
        
        logger.info(f"Request processed: route={route}, model={model_used}, time={processing_time:.1f}ms")
        
        # Step 4: Log for compliance
        try:
            audit_logger.log_request(
                route=route,
                pii_score=pii_score,
                pii_types=pii_types,
                model_used=model_used,
                prompt_length=len(request.prompt),
                response_length=len(response_text),
                processing_time_ms=processing_time,
                user_id=request.user_id,
                session_id=request.session_id,
                ip_address=client_ip
            )
        except Exception as log_error:
            logger.error(f"Failed to write audit log: {log_error}", exc_info=True)
            # Don't fail the request if logging fails
        
        # Step 5: Return response
        return GatewayResponse(
            response=response_text,
            route=route,
            pii_score=pii_score,
            pii_detected=pii_detections,
            model_used=model_used,
            processing_time_ms=processing_time
        )
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except ValidationError as e:
        logger.error(f"Validation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Validation error: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Gateway processing error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Gateway processing error. Please check logs for details."
        )


@app.get("/audit/recent", tags=["Audit"])
async def get_recent_audit_logs(limit: int = 50):
    """
    Get recent audit log entries for dashboard visualization.
    
    Args:
        limit: Maximum number of log entries to return (default: 50, max: 1000)
        
    Returns:
        Dictionary containing log entries and count
        
    Raises:
        HTTPException: If limit is invalid
    """
    if limit < 1 or limit > 1000:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Limit must be between 1 and 1000"
        )
    
    try:
        logs = audit_logger.get_recent_logs(limit=limit)
        return {
            "logs": logs,
            "count": len(logs),
            "limit": limit
        }
    except Exception as e:
        logger.error(f"Error retrieving audit logs: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve audit logs"
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host=config.gateway_host,
        port=config.gateway_port,
        log_level=config.gateway_log_level.lower()
    )

