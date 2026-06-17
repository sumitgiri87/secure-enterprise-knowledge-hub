"""
LLM Integration Module

Provides unified access to multiple LLM providers through a gateway pattern.

The gateway is imported lazily (PEP 562) so that lightweight submodules such as
``app.llm.guardrails`` can be imported - in tests, CI, or standalone tooling -
without pulling in the full provider stack (litellm and friends).
"""
from __future__ import annotations

__all__ = ["LLMGateway", "get_gateway"]


def __getattr__(name):
    if name in __all__:
        from app.llm import gateway

        return getattr(gateway, name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
