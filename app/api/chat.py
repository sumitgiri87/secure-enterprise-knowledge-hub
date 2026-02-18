"""
Chat Endpoint - Phase 2: LLM Integration

Now actually calls AI models!

Flow:
1.  Authentication check
2.  Request validation (Pydantic)
3.  Rate limit check
4.  Token budget check
5.  Build prompt messages
6.  Call LLM Gateway
7.  Audit logging
8.  Return response (streaming or regular)
"""

import os
import uuid
from datetime import datetime
from typing import Optional, List
import re
import time

from fastapi import APIRouter, Depends, Request, HTTPException, status
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field, field_validator, ConfigDict

from app.api.auth import verify_api_key
from app.llm.rate_limiter import get_rate_limiter, get_budget_manager
from observability.logging import log_event, log_error
from app.security.audit_logger import audit_event

router = APIRouter()

# Check if LLM is enabled (False by default until API keys are configured)
LLM_ENABLED = os.getenv("LLM_ENABLED", "false").lower() == "true"


# ─────────────────────────────────────────────
# Request / Response Models
# ─────────────────────────────────────────────

class ChatRequest(BaseModel):
    """Chat request model with strict validation."""

    model_config = ConfigDict(str_strip_whitespace=True)

    user_id: str = Field(..., min_length=3, max_length=64,
                         examples=["alice", "alice@company.com"])
    role: str = Field(..., pattern="^(user|admin|analyst|viewer)$")
    message: str = Field(..., min_length=1, max_length=2000)
    conversation_id: str = Field(..., min_length=3, max_length=64)
    stream: bool = Field(default=False, description="Stream response in real-time")
    model: Optional[str] = Field(default=None, description="Override default model")
    metadata: Optional[dict] = Field(default=None)

    @field_validator("message")
    @classmethod
    def validate_message(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Message cannot be empty or whitespace only")

        suspicious_patterns = [
            r"ignore.*instructions",
            r"system\s*prompt",
            r"you\s+are\s+now",
            r"<\s*script",
            r"javascript:",
            r"eval\s*\(",
        ]

        for pattern in suspicious_patterns:
            if re.search(pattern, v, re.IGNORECASE):
                raise ValueError(
                    "Message contains suspicious patterns. "
                    "Please rephrase your query."
                )
        return v

    @field_validator("user_id", "conversation_id")
    @classmethod
    def validate_ids(cls, v: str) -> str:
        if not re.match(r'^[a-zA-Z0-9@._-]+$', v):
            raise ValueError("ID contains invalid characters.")
        return v


class ChatResponse(BaseModel):
    """Chat response model."""

    status: str
    request_id: str
    conversation_id: str
    message: Optional[str] = None
    model: Optional[str] = None
    tokens_used: Optional[int] = None
    processing_time_ms: Optional[float] = None
    guardrails_triggered: Optional[List[str]] = None
    rate_limit_info: Optional[dict] = None


# ─────────────────────────────────────────────
# Endpoints
# ─────────────────────────────────────────────

@router.post(
    "/",
    response_model=ChatResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Submit a chat message",
)
async def chat_endpoint(
    request: Request,
    payload: ChatRequest,
    auth_context: dict = Depends(verify_api_key),
):
    """
    Main chat endpoint.

    If LLM_ENABLED=true in .env, calls the real AI model.
    If LLM_ENABLED=false (default), returns a mock response.
    This lets you develop and test without needing API keys.
    """
    start_time = time.time()

    request_id = getattr(request.state, "request_id", str(uuid.uuid4()))
    user_id = payload.user_id
    user_role = payload.role

    # Step 1: Rate limiting
    rate_limiter = get_rate_limiter()
    allowed, rate_info = rate_limiter.check_rate_limit(user_id)

    if not allowed:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail={
                "error": "rate_limit_exceeded",
                "message": "Too many requests. Please wait before trying again.",
                "retry_after_seconds": 60,
                "limit_info": rate_info
            }
        )

    # Step 2: Token budget check
    budget_manager = get_budget_manager()
    estimated_tokens = len(payload.message.split()) * 2
    budget_ok, budget_info = budget_manager.check_budget(user_id, estimated_tokens)

    if not budget_ok:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail={
                "error": "token_budget_exceeded",
                "message": "Daily token budget exceeded. Resets in 24 hours.",
                "budget_info": budget_info
            }
        )

    # Step 3: Structured logging
    log_event(
        user_id=user_id,
        role=user_role,
        request_id=request_id,
        action="chat_request_received",
        status="accepted"
    )

    # Step 4: Streaming response
    if payload.stream and LLM_ENABLED:
        return StreamingResponse(
            _stream_response(payload, request_id, user_id, user_role),
            media_type="text/event-stream",
            headers={
                "X-Request-ID": request_id,
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
            }
        )

    # Step 5: Regular (non-streaming) response
    ai_message = None
    model_used = "mock"
    tokens_used = 0

    if LLM_ENABLED:
        try:
            from app.llm.gateway import get_gateway
            from app.llm.prompts import build_chat_messages

            gateway = get_gateway()
            messages = build_chat_messages(payload.message)

            llm_response = await gateway.complete(
                messages=messages,
                user_id=user_id,
                request_id=request_id,
                model=payload.model,
            )

            ai_message = llm_response["content"]
            model_used = llm_response["model"]
            tokens_used = llm_response["tokens_used"]

            budget_manager.record_usage(user_id, tokens_used)

        except Exception as e:
            log_error(
                error_type="llm_call_failed",
                error_message=str(e),
                user_id=user_id,
                request_id=request_id,
            )
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail={
                    "error": "llm_unavailable",
                    "message": "AI service temporarily unavailable. Please try again.",
                    "request_id": request_id
                }
            )
    else:
        # Mock response - works WITHOUT any API keys
        ai_message = (
            f"[MOCK] You asked: '{payload.message}'. "
            f"To get real AI responses, set LLM_ENABLED=true and add your API keys to .env"
        )
        model_used = "mock"
        tokens_used = 0

    # Step 6: Calculate processing time
    processing_time_ms = (time.time() - start_time) * 1000

    # Step 7: Audit logging
    audit_event(
        request_id=request_id,
        user_id=user_id,
        role=user_role,
        action="chat_request",
        model=model_used,
        policy_decision="allow",
        guardrail_triggered=False,
        response_status="completed",
        metadata={
            "conversation_id": payload.conversation_id,
            "message_length": len(payload.message),
            "tokens_used": tokens_used,
            "llm_enabled": LLM_ENABLED,
        }
    )

    return ChatResponse(
        status="completed",
        request_id=request_id,
        conversation_id=payload.conversation_id,
        message=ai_message,
        model=model_used,
        tokens_used=tokens_used if tokens_used > 0 else None,
        processing_time_ms=round(processing_time_ms, 2),
        guardrails_triggered=None,
        rate_limit_info={
            "requests_remaining": rate_info.get("tokens_remaining"),
            "limit": rate_info.get("limit")
        }
    )


async def _stream_response(payload, request_id, user_id, user_role):
    """Internal generator for streaming SSE responses."""
    import json
    from app.llm.gateway import get_gateway
    from app.llm.prompts import build_chat_messages

    try:
        gateway = get_gateway()
        messages = build_chat_messages(payload.message)

        async for chunk in gateway.stream_complete(
            messages=messages,
            user_id=user_id,
            request_id=request_id,
            model=payload.model,
        ):
            data = json.dumps({
                "chunk": chunk,
                "request_id": request_id,
                "conversation_id": payload.conversation_id
            })
            yield f"data: {data}\n\n"

        yield "data: [DONE]\n\n"

    except Exception as e:
        error_data = json.dumps({"error": "stream_failed", "message": str(e)})
        yield f"data: {error_data}\n\n"


@router.get("/{request_id}", response_model=ChatResponse, summary="Get request status")
async def get_chat_status(
    request_id: str,
    auth_context: dict = Depends(verify_api_key),
):
    return ChatResponse(status="processing", request_id=request_id, conversation_id="unknown")


@router.delete("/{conversation_id}", status_code=status.HTTP_204_NO_CONTENT,
               summary="Delete conversation (GDPR)")
async def delete_conversation(
    conversation_id: str,
    auth_context: dict = Depends(verify_api_key),
):
    audit_event(
        request_id=str(uuid.uuid4()),
        user_id=auth_context.get("user_id", "unknown"),
        role=auth_context.get("role", "user"),
        action="conversation_delete",
        model="n/a",
        policy_decision="allow",
        guardrail_triggered=False,
        response_status="completed",
        metadata={"conversation_id": conversation_id, "timestamp": datetime.utcnow().isoformat()}
    )
    return None


@router.get("/budget/{user_id}", summary="Get token budget usage")
async def get_token_budget(user_id: str, auth_context: dict = Depends(verify_api_key)):
    """Get token usage and remaining budget for a user."""
    budget_manager = get_budget_manager()
    return budget_manager.get_usage_stats(user_id)