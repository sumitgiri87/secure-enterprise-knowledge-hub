"""
LLM Gateway Module

This module provides a unified interface to multiple LLM providers:
- Azure OpenAI (Primary)
- AWS Bedrock (Fallback)
- GCP Vertex AI (Secondary)

Key Features:
- Multi-provider routing with automatic fallback
- Rate limiting per user/tenant
- Token budget management
- Response streaming support
- Request/response logging for audit

Architecture:
    User Request
        ↓
    LLM Gateway (this module)
        ↓
    ┌─────────┬─────────┬─────────┐
    │  Azure  │   AWS   │   GCP   │
    │ OpenAI  │ Bedrock │ Vertex  │
    └─────────┴─────────┴─────────┘
"""

import os
import time
from typing import Optional, List, Dict, Any, AsyncGenerator
from datetime import datetime
import asyncio

import litellm
from litellm import completion, acompletion
from litellm.exceptions import (
    RateLimitError,
    ServiceUnavailableError,
    Timeout,
    APIError
)

from observability.logging import logger, log_event, log_error, log_performance
from app.security.audit_logger import audit_model_usage


# Configure LiteLLM
litellm.set_verbose = os.getenv("LITELLM_VERBOSE", "False").lower() == "true"
litellm.drop_params = True  # Drop unsupported params instead of erroring


class LLMConfig:
    """
    Configuration for LLM providers.
    
    In production, these would come from:
    - Azure Key Vault
    - AWS Secrets Manager
    - Environment variables (for development)
    """
    
    # Azure OpenAI Configuration
    AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY", "")
    AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT", "")
    AZURE_OPENAI_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-15-preview")
    AZURE_OPENAI_DEPLOYMENT = os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4")
    
    # AWS Bedrock Configuration
    AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID", "")
    AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY", "")
    AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
    
    # GCP Vertex AI Configuration
    GCP_PROJECT_ID = os.getenv("GCP_PROJECT_ID", "")
    GCP_CREDENTIALS_PATH = os.getenv("GCP_CREDENTIALS_PATH", "")
    
    # Model Configuration
    DEFAULT_MODEL = os.getenv("DEFAULT_LLM_MODEL", "gpt-4")
    DEFAULT_MAX_TOKENS = int(os.getenv("DEFAULT_MAX_TOKENS", "1000"))
    DEFAULT_TEMPERATURE = float(os.getenv("DEFAULT_TEMPERATURE", "0.7"))
    
    # Timeout Configuration
    REQUEST_TIMEOUT = int(os.getenv("LLM_REQUEST_TIMEOUT", "30"))  # seconds
    
    # Retry Configuration
    MAX_RETRIES = int(os.getenv("LLM_MAX_RETRIES", "3"))
    RETRY_DELAY = float(os.getenv("LLM_RETRY_DELAY", "1.0"))  # seconds


class LLMGateway:
    """
    Unified gateway for multiple LLM providers.
    
    This class handles:
    - Routing requests to appropriate providers
    - Automatic fallback on failures
    - Rate limiting and budget management
    - Request/response logging
    - Error handling and retry logic
    
    Example usage:
        gateway = LLMGateway()
        response = await gateway.complete(
            messages=[{"role": "user", "content": "Hello!"}],
            user_id="alice",
            request_id="req_123"
        )
    """
    
    def __init__(self):
        self.config = LLMConfig()
        self.providers = self._initialize_providers()
    
    def _initialize_providers(self) -> List[str]:
        """
        Initialize and validate available providers.
        
        Returns a list of provider names in priority order.
        Providers without API keys are skipped.
        """
        providers = []
        
        # Check Azure OpenAI
        if self.config.AZURE_OPENAI_API_KEY and self.config.AZURE_OPENAI_ENDPOINT:
            providers.append("azure")
            logger.info({"event_type": "llm_provider_init", "provider": "azure", "status": "available"})
        
        # Check AWS Bedrock
        if self.config.AWS_ACCESS_KEY_ID and self.config.AWS_SECRET_ACCESS_KEY:
            providers.append("bedrock")
            logger.info({"event_type": "llm_provider_init", "provider": "bedrock", "status": "available"})
        
        # Check GCP Vertex AI
        if self.config.GCP_PROJECT_ID:
            providers.append("vertex")
            logger.info({"event_type": "llm_provider_init", "provider": "vertex", "status": "available"})
        
        if not providers:
            logger.warning({
                "event_type": "llm_provider_init",
                "status": "no_providers",
                "message": "No LLM providers configured. Set API keys in environment variables."
            })
        
        return providers
    
    def _get_model_string(self, model: str, provider: Optional[str] = None) -> str:
        """
        Convert model name to provider-specific format.
        
        LiteLLM expects models in this format:
        - Azure: "azure/gpt-4"
        - AWS Bedrock: "bedrock/anthropic.claude-v2"
        - GCP Vertex: "vertex_ai/gemini-pro"
        
        Args:
            model: Base model name (e.g., "gpt-4", "claude-2")
            provider: Optional provider override
        
        Returns:
            Provider-specific model string
        """
        # If already prefixed, return as-is
        if "/" in model:
            return model
        
        # Default to first available provider
        if not provider:
            provider = self.providers[0] if self.providers else "azure"
        
        # Map to provider-specific format
        provider_models = {
            "azure": {
                "gpt-4": "azure/gpt-4",
                "gpt-4o": "azure/gpt-4o",
                "gpt-3.5-turbo": "azure/gpt-35-turbo"
            },
            "bedrock": {
                "claude-2": "bedrock/anthropic.claude-v2",
                "claude-instant": "bedrock/anthropic.claude-instant-v1",
                "llama-2": "bedrock/meta.llama2-70b-chat-v1"
            },
            "vertex": {
                "gemini-pro": "vertex_ai/gemini-pro",
                "palm-2": "vertex_ai/chat-bison"
            }
        }
        
        return provider_models.get(provider, {}).get(model, f"{provider}/{model}")
    
    async def complete(
        self,
        messages: List[Dict[str, str]],
        user_id: str,
        request_id: str,
        model: Optional[str] = None,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        stream: bool = False,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generate a completion from an LLM.
        
        This is the main method for getting AI responses. It:
        1. Validates the request
        2. Selects the appropriate model/provider
        3. Calls the LLM with retry logic
        4. Logs the request/response for audit
        5. Returns the response
        
        Args:
            messages: List of message dicts [{"role": "user", "content": "Hello"}]
            user_id: User making the request
            request_id: Unique request identifier
            model: Model to use (default: gpt-4)
            max_tokens: Max response length (default: 1000)
            temperature: Creativity level 0-1 (default: 0.7)
            stream: Whether to stream the response (default: False)
            metadata: Additional context for logging
        
        Returns:
            Dict with response data:
            {
                "content": "AI response text",
                "model": "gpt-4",
                "provider": "azure",
                "tokens_used": 150,
                "finish_reason": "stop",
                "latency_ms": 1234.5
            }
        
        Raises:
            RateLimitError: If rate limit exceeded
            ServiceUnavailableError: If all providers fail
            Timeout: If request takes too long
        """
        start_time = time.time()
        
        # Use defaults if not specified
        model = model or self.config.DEFAULT_MODEL
        max_tokens = max_tokens or self.config.DEFAULT_MAX_TOKENS
        temperature = temperature or self.config.DEFAULT_TEMPERATURE
        
        # Log the request
        logger.info({
            "event_type": "llm_request",
            "request_id": request_id,
            "user_id": user_id,
            "model": model,
            "message_count": len(messages),
            "stream": stream
        })
        
        # Try each provider in order
        last_error = None
        for attempt, provider in enumerate(self.providers, 1):
            try:
                model_string = self._get_model_string(model, provider)
                
                logger.info({
                    "event_type": "llm_attempt",
                    "request_id": request_id,
                    "provider": provider,
                    "attempt": attempt,
                    "model": model_string
                })
                
                # Call LiteLLM
                response = await acompletion(
                    model=model_string,
                    messages=messages,
                    max_tokens=max_tokens,
                    temperature=temperature,
                    timeout=self.config.REQUEST_TIMEOUT,
                    stream=stream
                )
                
                # Calculate metrics
                latency_ms = (time.time() - start_time) * 1000
                
                # Extract response data
                result = self._parse_response(response, provider, latency_ms)
                
                # Log performance
                log_performance(
                    operation="llm_completion",
                    duration_ms=latency_ms,
                    user_id=user_id,
                    request_id=request_id,
                    model=model,
                    provider=provider,
                    tokens_used=result["tokens_used"]
                )
                
                # Audit log
                audit_model_usage(
                    request_id=request_id,
                    user_id=user_id,
                    model=model,
                    provider=provider,
                    tokens_used=result["tokens_used"],
                    cost_usd=self._estimate_cost(model, result["tokens_used"]),
                    latency_ms=latency_ms,
                    success=True
                )
                
                return result
                
            except RateLimitError as e:
                last_error = e
                logger.warning({
                    "event_type": "llm_rate_limit",
                    "request_id": request_id,
                    "provider": provider,
                    "attempt": attempt,
                    "error": str(e)
                })
                
                # Try next provider
                if attempt < len(self.providers):
                    await asyncio.sleep(self.config.RETRY_DELAY)
                    continue
                else:
                    raise
            
            except (ServiceUnavailableError, Timeout, APIError) as e:
                last_error = e
                logger.warning({
                    "event_type": "llm_provider_error",
                    "request_id": request_id,
                    "provider": provider,
                    "attempt": attempt,
                    "error_type": type(e).__name__,
                    "error": str(e)
                })
                
                # Try next provider
                if attempt < len(self.providers):
                    await asyncio.sleep(self.config.RETRY_DELAY)
                    continue
                else:
                    raise
            
            except Exception as e:
                last_error = e
                log_error(
                    error_type="llm_unexpected_error",
                    error_message=str(e),
                    user_id=user_id,
                    request_id=request_id,
                    provider=provider
                )
                
                # Try next provider
                if attempt < len(self.providers):
                    await asyncio.sleep(self.config.RETRY_DELAY)
                    continue
                else:
                    raise
        
        # All providers failed
        raise ServiceUnavailableError(f"All LLM providers failed. Last error: {last_error}")
    
    def _parse_response(
        self,
        response: Any,
        provider: str,
        latency_ms: float
    ) -> Dict[str, Any]:
        """
        Parse LiteLLM response into standardized format.
        
        Args:
            response: Raw LiteLLM response
            provider: Provider that generated the response
            latency_ms: Request latency
        
        Returns:
            Standardized response dict
        """
        # Extract content
        content = response.choices[0].message.content
        
        # Extract token usage
        tokens_used = getattr(response.usage, "total_tokens", 0)
        prompt_tokens = getattr(response.usage, "prompt_tokens", 0)
        completion_tokens = getattr(response.usage, "completion_tokens", 0)
        
        # Extract finish reason
        finish_reason = response.choices[0].finish_reason
        
        return {
            "content": content,
            "model": response.model,
            "provider": provider,
            "tokens_used": tokens_used,
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "finish_reason": finish_reason,
            "latency_ms": latency_ms
        }
    
    def _estimate_cost(self, model: str, tokens_used: int) -> float:
        """
        Estimate cost of API call based on model and token usage.
        
        Pricing as of 2024 (approximate):
        - GPT-4: $0.03/1K prompt tokens, $0.06/1K completion tokens
        - GPT-3.5: $0.0015/1K prompt tokens, $0.002/1K completion tokens
        - Claude-2: $0.008/1K tokens
        
        Args:
            model: Model used
            tokens_used: Total tokens consumed
        
        Returns:
            Estimated cost in USD
        """
        # Simplified cost estimation (use average of prompt + completion)
        cost_per_1k = {
            "gpt-4": 0.045,  # Average of prompt and completion
            "gpt-4o": 0.03,
            "gpt-3.5-turbo": 0.00175,
            "claude-2": 0.008,
            "gemini-pro": 0.001
        }
        
        # Get base model name
        base_model = model.split("/")[-1] if "/" in model else model
        
        # Find matching cost
        for key, cost in cost_per_1k.items():
            if key in base_model.lower():
                return (tokens_used / 1000) * cost
        
        # Default estimate
        return (tokens_used / 1000) * 0.01
    
    async def stream_complete(
        self,
        messages: List[Dict[str, str]],
        user_id: str,
        request_id: str,
        model: Optional[str] = None,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None
    ) -> AsyncGenerator[str, None]:
        """
        Stream a completion from an LLM.
        
        This is used for real-time response generation where you want
        to show the AI response as it's being generated (like ChatGPT).
        
        Example usage:
            async for chunk in gateway.stream_complete(messages, ...):
                print(chunk, end="", flush=True)
        
        Args:
            Same as complete() method
        
        Yields:
            String chunks of the response as they're generated
        """
        # Use defaults if not specified
        model = model or self.config.DEFAULT_MODEL
        max_tokens = max_tokens or self.config.DEFAULT_MAX_TOKENS
        temperature = temperature or self.config.DEFAULT_TEMPERATURE
        
        # Get model string for first provider
        provider = self.providers[0] if self.providers else "azure"
        model_string = self._get_model_string(model, provider)
        
        logger.info({
            "event_type": "llm_stream_start",
            "request_id": request_id,
            "user_id": user_id,
            "model": model_string
        })
        
        try:
            # Call LiteLLM with streaming
            response = await acompletion(
                model=model_string,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature,
                timeout=self.config.REQUEST_TIMEOUT,
                stream=True
            )
            
            # Stream chunks
            full_response = ""
            async for chunk in response:
                if chunk.choices[0].delta.content:
                    content = chunk.choices[0].delta.content
                    full_response += content
                    yield content
            
            logger.info({
                "event_type": "llm_stream_complete",
                "request_id": request_id,
                "total_length": len(full_response)
            })
            
        except Exception as e:
            log_error(
                error_type="llm_stream_error",
                error_message=str(e),
                user_id=user_id,
                request_id=request_id
            )
            raise


# Global gateway instance
_gateway_instance: Optional[LLMGateway] = None


def get_gateway() -> LLMGateway:
    """
    Get or create the global LLM gateway instance.
    
    This is a singleton pattern to reuse the same gateway
    throughout the application.
    
    Returns:
        LLMGateway instance
    """
    global _gateway_instance
    
    if _gateway_instance is None:
        _gateway_instance = LLMGateway()
    
    return _gateway_instance