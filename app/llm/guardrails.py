"""
Guardrails - the chokepoint every tool call passes through.

This is the production-shaped version of the guardrail described in
"The Agent Red Team, Part 3" (Sumit Giri, 2026): four ordered checks around
every tool call, any one of which can veto. It composes the structural layers
(PolicyEngine) and the egress layer (pii_detection) with a semantic input
screen, and emits an auditable decision for every call.

    1. INPUT SCREEN   - scan ingested/untrusted content for injection signatures
    2. TOOL ALLOWLIST - is this tool permitted at all?            (PolicyEngine)
    3. ARG POLICY     - are the arguments in bounds?              (PolicyEngine)
    4. EGRESS CHECK   - does the action move secrets/PII outward? (pii_detection)

Design stance: assume the model can be convinced of anything, and constrain what
a convinced model is allowed to *do*. The structural layers (2-4) constrain
capability reliably; the semantic layer (1) detects intent unreliably and is
treated as a tripwire for logging/escalation, not a wall. See CaMeL (2025) and
Progent (2025).
"""
from __future__ import annotations

import logging
import re
from dataclasses import dataclass

from app.security import pii_detection
from app.security.policy_engine import Decision, PolicyEngine, ToolCall

logger = logging.getLogger(__name__)

INJECTION_SIGNATURES = re.compile(
    r"(ignore (all |the )?(previous|prior|above) instructions|disregard the above|"
    r"you are now|new task:|system override|set aside the earlier)",
    re.I,
)


@dataclass
class GuardrailDecision:
    decision: Decision
    reason: str
    layer: str

    @property
    def allowed(self) -> bool:
        return self.decision is Decision.ALLOW

    @property
    def blocked(self) -> bool:
        return self.decision is Decision.BLOCK


class Guardrail:
    """Compose input-screen + policy + egress into one auditable veto point."""

    def __init__(self, policy: PolicyEngine | None = None):
        self.policy = policy or PolicyEngine()

    def check(self, call: ToolCall) -> GuardrailDecision:
        # 1. INPUT SCREEN (semantic - tripwire, escalate rather than trust)
        if call.ingested_context and INJECTION_SIGNATURES.search(call.ingested_context):
            return self._log(
                call,
                GuardrailDecision(
                    Decision.ESCALATE,
                    "possible injection in ingested content",
                    "input-screen",
                ),
            )

        # 2 + 3. TOOL ALLOWLIST + ARG POLICY (structural)
        pol = self.policy.evaluate(call)
        if pol.decision is not Decision.ALLOW:
            return self._log(call, GuardrailDecision(pol.decision, pol.reason, pol.layer))

        # 4. EGRESS CHECK (structural - secrets/PII leaving via outbound args)
        outbound = " ".join(str(v) for v in call.args.values())
        findings = pii_detection.scan(outbound)
        if findings:
            kinds = ", ".join(sorted({f.label for f in findings}))
            return self._log(
                call,
                GuardrailDecision(
                    Decision.BLOCK, f"sensitive data in outbound args: {kinds}", "egress"
                ),
            )

        return self._log(call, GuardrailDecision(Decision.ALLOW, "ok", "egress"))

    def _log(self, call: ToolCall, result: GuardrailDecision) -> GuardrailDecision:
        logger.info(
            "guardrail tool=%s decision=%s layer=%s reason=%s",
            call.tool,
            result.decision.value,
            result.layer,
            result.reason,
        )
        return result
