"""
LLM Integration Module

Provides unified access to multiple LLM providers through a gateway pattern.
"""

from app.llm.gateway import LLMGateway, get_gateway

__all__ = ["LLMGateway", "get_gateway"]