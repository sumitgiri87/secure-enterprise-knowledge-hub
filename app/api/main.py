"""
Secure Enterprise Knowledge Hub API
Main FastAPI application entry point

This API implements enterprise-grade security controls:
- API Key authentication (designed for Azure AD / IAM integration)
- Request validation and sanitization
- Structured JSON logging for SIEM integration
- Comprehensive audit logging for compliance
- Rate limiting and request tracking
"""

import time
import uuid
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.chat import router as chat_router
from app.api.health import router as health_router
from observability.logging import log_event, logger


# Lifespan context manager for startup/shutdown events
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Handles application startup and shutdown events.
    Add initialization logic here (DB connections, model loading, etc.)
    """
    # Startup
    logger.info(
        {
            "event_type": "application_startup",
            "message": "Secure Enterprise Knowledge Hub API starting...",
        }
    )

    yield

    # Shutdown
    logger.info(
        {
            "event_type": "application_shutdown",
            "message": "Secure Enterprise Knowledge Hub API shutting down...",
        }
    )


# Initialize FastAPI application
app = FastAPI(
    title="Secure Enterprise Knowledge Hub API",
    description="Enterprise-grade conversational AI with security, compliance, and governance",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)


# CORS Middleware Configuration
# NOTE: In production, restrict origins to specific domains
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # TODO: Restrict to specific origins in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request ID Middleware - adds unique tracking ID to every request
@app.middleware("http")
async def add_request_id_middleware(request: Request, call_next):
    """
    Adds a unique request_id to every incoming request for distributed tracing.
    Logs request timing and status for observability.
    """
    request_id = str(uuid.uuid4())
    request.state.request_id = request_id

    # Log incoming request
    start_time = time.time()

    log_event(
        user_id=request.headers.get("x-user-id", "unknown"),
        role=request.headers.get("x-user-role", "unknown"),
        request_id=request_id,
        action=f"{request.method} {request.url.path}",
        status="started",
    )

    # Process request
    response = await call_next(request)

    # Calculate processing time
    process_time = time.time() - start_time
    response.headers["X-Request-ID"] = request_id
    response.headers["X-Process-Time"] = str(process_time)

    # Log request completion
    log_event(
        user_id=request.headers.get("x-user-id", "unknown"),
        role=request.headers.get("x-user-role", "unknown"),
        request_id=request_id,
        action=f"{request.method} {request.url.path}",
        status=f"completed_{response.status_code}",
    )

    return response


# Global Exception Handlers
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    Handles Pydantic validation errors with detailed logging.
    Returns user-friendly error messages while logging full details for debugging.
    """
    request_id = getattr(request.state, "request_id", "unknown")

    # Convert errors to JSON-serializable format
    error_details = []
    for error in exc.errors():
        error_details.append(
            {
                "loc": list(error.get("loc", [])),
                "msg": str(error.get("msg", "")),
                "type": error.get("type", ""),
            }
        )

    logger.warning(
        {
            "event_type": "validation_error",
            "request_id": request_id,
            "path": request.url.path,
            "errors": error_details,
            "body": str(exc.body) if hasattr(exc, "body") else None,
        }
    )

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": "validation_error",
            "message": "Request validation failed",
            "details": error_details,
            "request_id": request_id,
        },
    )


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    """
    Catches all unhandled exceptions and logs them for debugging.
    Returns generic error to avoid leaking implementation details.
    """
    request_id = getattr(request.state, "request_id", "unknown")

    logger.error(
        {
            "event_type": "unhandled_exception",
            "request_id": request_id,
            "path": request.url.path,
            "error_type": type(exc).__name__,
            "error_message": str(exc),
        }
    )

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "internal_server_error",
            "message": "An unexpected error occurred",
            "request_id": request_id,
        },
    )


# Include routers
app.include_router(health_router, prefix="/health", tags=["Health"])
app.include_router(chat_router, prefix="/api/v1/chat", tags=["Chat"])


# Root endpoint
@app.get("/", tags=["Root"])
async def root():
    """
    API root endpoint - returns basic API information
    """
    return {
        "name": "Secure Enterprise Knowledge Hub API",
        "version": "1.0.0",
        "status": "operational",
        "docs": "/docs",
        "health": "/health",
    }


if __name__ == "__main__":
    import uvicorn

    # Run with: python -m app.api.main
    uvicorn.run(
        "app.api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,  # Disable in production
        log_level="info",
    )
