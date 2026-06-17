"""
PII & Secret Detection - Egress control.

The egress half of the guardrail: before any tool call sends data outward (an
HTTP body, a webhook, a log line), scan it for secrets and personal data that
must not leave. Deterministic regex detection - cheap, explainable, and the
highest-value layer, because most genuinely costly incidents are data *leaving*.

Detects:
- Secrets: API keys, AWS access keys, private-key blocks, bearer tokens
- PII:     emails, North American phone numbers, SSNs, credit-card-shaped numbers

This is detection, not redaction policy; callers decide block vs. redact vs.
escalate. Maps to EU AI Act Art. 10 (data governance) and GDPR Art. 5.
"""
from __future__ import annotations

import re
from dataclasses import dataclass

SECRET_PATTERNS = {
    "openai_key": re.compile(r"sk-[A-Za-z0-9]{20,}"),
    "aws_access_key": re.compile(r"AKIA[0-9A-Z]{16}"),
    "private_key_block": re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    "bearer_token": re.compile(r"\bBearer\s+[A-Za-z0-9._\-]{20,}\b"),
}

PII_PATTERNS = {
    "email": re.compile(r"\b[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}\b"),
    "ssn": re.compile(r"\b\d{3}-\d{2}-\d{4}\b"),
    "credit_card": re.compile(r"\b(?:\d[ -]?){13,16}\b"),
    "phone_na": re.compile(r"\b(?:\+?1[ .\-]?)?\(?\d{3}\)?[ .\-]?\d{3}[ .\-]?\d{4}\b"),
}


@dataclass
class Finding:
    kind: str   # "secret" | "pii"
    label: str  # e.g. "aws_access_key"
    match: str  # the matched substring (caller decides whether to persist it)


def scan(text: str) -> list[Finding]:
    """Return all secret/PII findings in ``text`` (empty list if clean)."""
    findings: list[Finding] = []
    for label, pattern in SECRET_PATTERNS.items():
        for m in pattern.findall(text or ""):
            findings.append(Finding("secret", label, m if isinstance(m, str) else str(m)))
    for label, pattern in PII_PATTERNS.items():
        for m in pattern.findall(text or ""):
            findings.append(Finding("pii", label, m if isinstance(m, str) else str(m)))
    return findings


def contains_sensitive(text: str) -> bool:
    return bool(scan(text))
