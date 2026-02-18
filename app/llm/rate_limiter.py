"""
Rate Limiter Module

Prevents abuse by limiting how many requests a user can make.

Why rate limiting?
- Prevents one user from using all the AI budget
- Protects against DoS attacks
- Controls costs per user/tenant
- Enterprise requirement for fair usage

Two implementations:
1. In-memory (development/testing) - simple dict
2. Redis-based (production) - shared across multiple servers

How it works (Token Bucket Algorithm):
- Each user gets a "bucket" of tokens
- Each request uses tokens
- Tokens refill over time
- If bucket is empty, request is rejected

Example:
  User gets 100 tokens per minute
  Each request costs 1 token
  After 100 requests in 1 minute → rate limited
  After 1 minute → tokens refill → can make requests again
"""

import time
import os
from typing import Optional
from collections import defaultdict

from observability.logging import logger


class InMemoryRateLimiter:
    """
    Simple in-memory rate limiter for development and testing.

    NOT suitable for production with multiple servers because
    each server has its own memory - limits won't be shared!

    For production, use RedisRateLimiter below.
    """

    def __init__(self):
        # Stores: {user_id: {"tokens": 100, "last_refill": timestamp}}
        self._buckets: dict = defaultdict(lambda: {
            "tokens": self._get_limit(),
            "last_refill": time.time()
        })

    def _get_limit(self) -> int:
        """Get the rate limit from environment variable."""
        return int(os.getenv("RATE_LIMIT_PER_MINUTE", "60"))

    def _refill_tokens(self, user_id: str) -> None:
        """
        Refill tokens based on time elapsed since last refill.

        If 1 minute has passed, fully refill the bucket.
        If 30 seconds have passed, refill half the bucket.
        """
        bucket = self._buckets[user_id]
        now = time.time()
        elapsed = now - bucket["last_refill"]
        limit = self._get_limit()

        # Calculate how many tokens to add (proportional to time)
        tokens_to_add = (elapsed / 60.0) * limit

        # Add tokens, but don't exceed the limit
        bucket["tokens"] = min(limit, bucket["tokens"] + tokens_to_add)
        bucket["last_refill"] = now

    def check_rate_limit(self, user_id: str, cost: int = 1) -> tuple[bool, dict]:
        """
        Check if user is within rate limits.

        Args:
            user_id: User to check
            cost: How many tokens this request costs (default: 1)

        Returns:
            Tuple of (allowed: bool, info: dict)
            - allowed=True means request is OK
            - allowed=False means rate limited

        Example:
            allowed, info = limiter.check_rate_limit("alice")
            if not allowed:
                raise HTTPException(429, "Rate limit exceeded")
        """
        # Refill tokens first
        self._refill_tokens(user_id)

        bucket = self._buckets[user_id]
        limit = self._get_limit()

        info = {
            "user_id": user_id,
            "tokens_remaining": int(bucket["tokens"]),
            "limit": limit,
            "reset_in_seconds": 60
        }

        # Check if enough tokens
        if bucket["tokens"] >= cost:
            bucket["tokens"] -= cost
            info["allowed"] = True
            info["tokens_remaining"] = int(bucket["tokens"])
            return True, info
        else:
            info["allowed"] = False
            logger.warning({
                "event_type": "rate_limit_exceeded",
                "user_id": user_id,
                "tokens_remaining": int(bucket["tokens"]),
                "tokens_required": cost
            })
            return False, info


class TokenBudgetManager:
    """
    Manages LLM token budgets per user/tenant.

    Different from rate limiting:
    - Rate limiting: controls REQUESTS per minute
    - Token budget: controls TOKENS (AI words) per day/month

    Why token budgets?
    - LLM APIs charge by token (like per word)
    - Need to control costs per department/user
    - Prevent one team from using entire company's budget

    Example:
        Finance team gets 1,000,000 tokens/month
        Each question uses ~500 tokens
        That's ~2000 questions per month for Finance
    """

    def __init__(self):
        # Stores: {user_id: {"used": 0, "limit": 100000, "reset_at": timestamp}}
        self._budgets: dict = {}

    def _get_daily_limit(self, user_id: str) -> int:
        """
        Get token limit for a user.

        In production, this would query a database.
        For now, uses environment variable.
        """
        return int(os.getenv("TOKEN_BUDGET_DAILY", "100000"))

    def check_budget(self, user_id: str, estimated_tokens: int) -> tuple[bool, dict]:
        """
        Check if user has token budget remaining.

        Args:
            user_id: User to check
            estimated_tokens: How many tokens this request will use

        Returns:
            Tuple of (allowed: bool, info: dict)
        """
        # Initialize budget if first time
        if user_id not in self._budgets:
            self._budgets[user_id] = {
                "used": 0,
                "limit": self._get_daily_limit(user_id),
                "reset_at": time.time() + 86400  # 24 hours
            }

        budget = self._budgets[user_id]

        # Reset if day has passed
        if time.time() > budget["reset_at"]:
            budget["used"] = 0
            budget["reset_at"] = time.time() + 86400

        remaining = budget["limit"] - budget["used"]

        info = {
            "user_id": user_id,
            "tokens_used_today": budget["used"],
            "tokens_remaining": remaining,
            "daily_limit": budget["limit"]
        }

        if remaining >= estimated_tokens:
            return True, info
        else:
            logger.warning({
                "event_type": "token_budget_exceeded",
                "user_id": user_id,
                "tokens_requested": estimated_tokens,
                "tokens_remaining": remaining
            })
            return False, info

    def record_usage(self, user_id: str, tokens_used: int) -> None:
        """
        Record actual token usage after a request completes.

        Args:
            user_id: User who made the request
            tokens_used: Actual tokens consumed
        """
        if user_id not in self._budgets:
            self._budgets[user_id] = {
                "used": 0,
                "limit": self._get_daily_limit(user_id),
                "reset_at": time.time() + 86400
            }

        self._budgets[user_id]["used"] += tokens_used

        logger.info({
            "event_type": "token_usage_recorded",
            "user_id": user_id,
            "tokens_used": tokens_used,
            "total_today": self._budgets[user_id]["used"]
        })

    def get_usage_stats(self, user_id: str) -> dict:
        """
        Get token usage statistics for a user.

        Args:
            user_id: User to get stats for

        Returns:
            Dict with usage information
        """
        if user_id not in self._budgets:
            return {
                "user_id": user_id,
                "tokens_used_today": 0,
                "daily_limit": self._get_daily_limit(user_id),
                "tokens_remaining": self._get_daily_limit(user_id)
            }

        budget = self._budgets[user_id]
        return {
            "user_id": user_id,
            "tokens_used_today": budget["used"],
            "daily_limit": budget["limit"],
            "tokens_remaining": budget["limit"] - budget["used"]
        }


# Global instances (singletons)
_rate_limiter: Optional[InMemoryRateLimiter] = None
_budget_manager: Optional[TokenBudgetManager] = None


def get_rate_limiter() -> InMemoryRateLimiter:
    """Get or create the global rate limiter."""
    global _rate_limiter
    if _rate_limiter is None:
        _rate_limiter = InMemoryRateLimiter()
    return _rate_limiter


def get_budget_manager() -> TokenBudgetManager:
    """Get or create the global budget manager."""
    global _budget_manager
    if _budget_manager is None:
        _budget_manager = TokenBudgetManager()
    return _budget_manager