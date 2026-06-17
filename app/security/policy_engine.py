"""
Policy Engine - Deterministic tool & argument authorization.

This is the structural half of the guardrail layer (see app/llm/guardrails.py):
it decides whether an agent's tool call is permitted at all, and whether its
arguments are within bounds. It is deliberately deterministic - no model sits in
the decision path - so every allow/deny is auditable and replayable, which is a
hard requirement under OSFI E-23 and EU AI Act Article 13.

Design principles:
- Deny by default. A tool not on the allowlist is blocked.
- Least privilege. Each tool is constrained to the narrowest arguments that
  still let it do its job (path prefixes, host allowlists, denied verbs).
- Escalate, don't only block. Dangerous-but-sometimes-legitimate actions route
  to a human instead of failing the agent outright.

Related research: Shi et al., "Progent: Programmable Privilege Control for LLM
Agents" (2025); Debenedetti et al., "Defeating Prompt Injections by Design"
(CaMeL, 2025).
"""
from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger(__name__)


class Decision(str, Enum):
    ALLOW = "allow"
    BLOCK = "block"
    ESCALATE = "escalate"


@dataclass
class ToolCall:
    tool: str
    args: dict = field(default_factory=dict)
    # Untrusted content the agent ingested this turn (retrieved doc, web page).
    ingested_context: str = ""


@dataclass
class PolicyResult:
    decision: Decision
    reason: str
    layer: str


@dataclass
class ToolPolicy:
    """Per-tool argument constraints. Empty collections mean 'no constraint'."""

    allowed_path_prefixes: tuple = ()
    allowed_hosts: tuple = ()
    denied_arg_patterns: tuple = ()  # tuple of compiled regexes


DEFAULT_DENIED_SHELL = re.compile(r"\b(rm|curl|wget|nc|dd|mkfs|chmod|chown)\b|>\s*/")


class PolicyEngine:
    """Deny-by-default tool authorization with per-tool argument policies."""

    def __init__(self, allowed_tools=None, tool_policies=None):
        # Deny by default: only these tools may ever run.
        self.allowed_tools = set(
            allowed_tools or {"read_file", "http_get", "search_kb"}
        )
        self.tool_policies = tool_policies or {
            "read_file": ToolPolicy(allowed_path_prefixes=("/workspace/", "/data/kb/")),
            "http_get": ToolPolicy(allowed_hosts=("api.internal.example",)),
            "shell": ToolPolicy(denied_arg_patterns=(DEFAULT_DENIED_SHELL,)),
        }

    def evaluate(self, call: ToolCall) -> PolicyResult:
        # Layer 2 - tool allowlist
        if call.tool not in self.allowed_tools:
            return PolicyResult(
                Decision.BLOCK, f"tool '{call.tool}' not on allowlist", "allowlist"
            )

        policy = self.tool_policies.get(call.tool, ToolPolicy())

        # Layer 3 - argument policy
        if policy.allowed_path_prefixes:
            path = str(call.args.get("path", ""))
            if not path.startswith(tuple(policy.allowed_path_prefixes)):
                return PolicyResult(
                    Decision.BLOCK, f"path '{path}' out of bounds", "arg-policy"
                )

        if policy.allowed_hosts:
            host = str(call.args.get("host", ""))
            if host not in policy.allowed_hosts:
                return PolicyResult(
                    Decision.ESCALATE, f"host '{host}' not on allowlist", "arg-policy"
                )

        for pattern in policy.denied_arg_patterns:
            for value in call.args.values():
                if pattern.search(str(value)):
                    return PolicyResult(
                        Decision.BLOCK,
                        f"denied argument pattern in {value!r}",
                        "arg-policy",
                    )

        return PolicyResult(Decision.ALLOW, "ok", "arg-policy")
