"""
Audit Logger - Compliance & Governance

Implements comprehensive audit logging for:
- SOC 2 compliance
- GDPR Article 30 (Records of Processing)
- HIPAA audit requirements
- ISO 27001 logging requirements
- Internal governance & risk management

Audit Events Tracked:
- All AI model interactions (prompts, responses)
- Policy decisions (allow/deny)
- Guardrail triggers (content moderation)
- Authentication events
- Authorization decisions
- Data access patterns
- Configuration changes

Storage Recommendations:
- Immutable storage (S3 Object Lock, Azure Immutable Blob Storage)
- Encryption at rest (AES-256)
- Retention: 7 years (typical compliance requirement)
- Regular backups to cold storage (Glacier, Archive tier)
"""

import json
from datetime import datetime
from typing import Optional, Dict, Any
from observability.logging import logger


def audit_event(
    request_id: str,
    user_id: str,
    role: str,
    action: str,
    model: str,
    policy_decision: str,
    guardrail_triggered: bool,
    response_status: str,
    metadata: Optional[Dict[str, Any]] = None
):
    """
    Log a comprehensive audit event.
    
    This function creates an immutable audit trail for compliance.
    All events should be stored in tamper-proof storage.
    
    Args:
        request_id: Unique request identifier
        user_id: User who initiated the request
        role: User's role (for RBAC auditing)
        action: Action performed (chat_request, policy_check, etc.)
        model: AI model used (gpt-4, claude-3, etc.)
        policy_decision: Policy engine decision (allow, deny, require_approval)
        guardrail_triggered: Whether any content guardrails were triggered
        response_status: Response status (pending, completed, failed, blocked)
        metadata: Additional context (conversation_id, department, etc.)
    
    Audit Record Structure:
    {
        "audit_version": "1.0",
        "timestamp": "2024-02-12T10:30:00.123456Z",
        "request_id": "uuid",
        "user_id": "user_123",
        "role": "admin",
        "action": "chat_request",
        "model": "gpt-4",
        "policy_decision": "allow",
        "guardrail_triggered": false,
        "response_status": "completed",
        "metadata": {...}
    }
    
    Example:
        audit_event(
            request_id="req_abc123",
            user_id="alice@company.com",
            role="analyst",
            action="chat_request",
            model="azure-gpt4",
            policy_decision="allow",
            guardrail_triggered=False,
            response_status="completed",
            metadata={
                "conversation_id": "conv_xyz",
                "department": "finance",
                "classification": "confidential"
            }
        )
    """
    
    # Build audit event
    event = {
        "audit_version": "1.0",
        "event_type": "ai_audit",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "request_id": request_id,
        "user_id": user_id,
        "role": role,
        "action": action,
        "model": model,
        "policy_decision": policy_decision,
        "guardrail_triggered": guardrail_triggered,
        "response_status": response_status,
        "metadata": metadata or {}
    }
    
    # Log to structured logger
    # This will be captured by log aggregation systems
    logger.info(event)
    
    # TODO: Also write to dedicated audit storage
    # Examples:
    # - S3 with Object Lock (WORM - Write Once Read Many)
    # - Azure Blob Storage with Immutability Policy
    # - Dedicated audit database with append-only tables
    # - SIEM integration (Splunk, Datadog, etc.)
    
    return event


def audit_authentication_event(
    user_id: str,
    auth_method: str,
    success: bool,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
    failure_reason: Optional[str] = None
):
    """
    Log authentication attempt.
    
    Critical for security monitoring and compliance.
    
    Args:
        user_id: User attempting authentication
        auth_method: Method used (api_key, oauth, azure_ad, etc.)
        success: Whether authentication succeeded
        ip_address: Source IP address
        user_agent: User agent string
        failure_reason: Reason for failure (if applicable)
    
    Example:
        audit_authentication_event(
            user_id="alice@company.com",
            auth_method="azure_ad",
            success=True,
            ip_address="203.0.113.42",
            user_agent="Mozilla/5.0..."
        )
    """
    event = {
        "audit_version": "1.0",
        "event_type": "authentication",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "user_id": user_id,
        "auth_method": auth_method,
        "success": success,
        "ip_address": ip_address,
        "user_agent": user_agent,
        "failure_reason": failure_reason
    }
    
    logger.info(event)
    return event


def audit_authorization_event(
    user_id: str,
    role: str,
    resource: str,
    action: str,
    decision: str,
    reason: Optional[str] = None
):
    """
    Log authorization decision.
    
    Tracks access control decisions for compliance.
    
    Args:
        user_id: User requesting access
        role: User's role
        resource: Resource being accessed
        action: Action requested (read, write, delete, etc.)
        decision: Authorization decision (allow, deny)
        reason: Reason for decision
    
    Example:
        audit_authorization_event(
            user_id="alice@company.com",
            role="analyst",
            resource="confidential_documents",
            action="read",
            decision="allow",
            reason="user_has_required_clearance"
        )
    """
    event = {
        "audit_version": "1.0",
        "event_type": "authorization",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "user_id": user_id,
        "role": role,
        "resource": resource,
        "action": action,
        "decision": decision,
        "reason": reason
    }
    
    logger.info(event)
    return event


def audit_data_access(
    user_id: str,
    role: str,
    data_type: str,
    data_classification: str,
    access_method: str,
    records_accessed: int,
    purpose: Optional[str] = None
):
    """
    Log data access for GDPR Article 30 compliance.
    
    Required for demonstrating compliance with data processing records.
    
    Args:
        user_id: User accessing data
        role: User's role
        data_type: Type of data (customer_data, financial_records, etc.)
        data_classification: Classification level (public, internal, confidential, restricted)
        access_method: How data was accessed (rag_retrieval, direct_query, etc.)
        records_accessed: Number of records accessed
        purpose: Business purpose for access
    
    Example:
        audit_data_access(
            user_id="alice@company.com",
            role="analyst",
            data_type="customer_records",
            data_classification="confidential",
            access_method="rag_retrieval",
            records_accessed=5,
            purpose="customer_support_query"
        )
    """
    event = {
        "audit_version": "1.0",
        "event_type": "data_access",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "user_id": user_id,
        "role": role,
        "data_type": data_type,
        "data_classification": data_classification,
        "access_method": access_method,
        "records_accessed": records_accessed,
        "purpose": purpose
    }
    
    logger.info(event)
    return event


def audit_guardrail_trigger(
    request_id: str,
    user_id: str,
    guardrail_type: str,
    severity: str,
    trigger_reason: str,
    action_taken: str,
    content_sample: Optional[str] = None
):
    """
    Log guardrail trigger event.
    
    Critical for monitoring AI safety and content moderation.
    
    Args:
        request_id: Request that triggered the guardrail
        user_id: User whose request triggered it
        guardrail_type: Type of guardrail (toxicity, bias, pii_leakage, hallucination, etc.)
        severity: Severity level (low, medium, high, critical)
        trigger_reason: Detailed reason for trigger
        action_taken: Action taken (blocked, flagged, redacted, etc.)
        content_sample: Sample of problematic content (redacted if needed)
    
    Example:
        audit_guardrail_trigger(
            request_id="req_abc123",
            user_id="alice@company.com",
            guardrail_type="pii_leakage",
            severity="high",
            trigger_reason="SSN detected in response",
            action_taken="redacted",
            content_sample="Response contained: [REDACTED]"
        )
    """
    event = {
        "audit_version": "1.0",
        "event_type": "guardrail_trigger",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "request_id": request_id,
        "user_id": user_id,
        "guardrail_type": guardrail_type,
        "severity": severity,
        "trigger_reason": trigger_reason,
        "action_taken": action_taken,
        "content_sample": content_sample
    }
    
    logger.warning(event)  # Use WARNING level for guardrail triggers
    return event


def audit_model_usage(
    request_id: str,
    user_id: str,
    model: str,
    provider: str,
    tokens_used: int,
    cost_usd: float,
    latency_ms: float,
    success: bool
):
    """
    Log model usage for cost tracking and performance monitoring.
    
    Args:
        request_id: Request identifier
        user_id: User who initiated the request
        model: Model used (gpt-4, claude-3-opus, etc.)
        provider: Provider (azure, aws, anthropic, etc.)
        tokens_used: Total tokens consumed
        cost_usd: Estimated cost in USD
        latency_ms: Response time in milliseconds
        success: Whether the request succeeded
    
    Example:
        audit_model_usage(
            request_id="req_abc123",
            user_id="alice@company.com",
            model="gpt-4",
            provider="azure-openai",
            tokens_used=1500,
            cost_usd=0.045,
            latency_ms=1234.5,
            success=True
        )
    """
    event = {
        "audit_version": "1.0",
        "event_type": "model_usage",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "request_id": request_id,
        "user_id": user_id,
        "model": model,
        "provider": provider,
        "tokens_used": tokens_used,
        "cost_usd": cost_usd,
        "latency_ms": latency_ms,
        "success": success
    }
    
    logger.info(event)
    return event


# Export audit summary statistics
def get_audit_summary(
    start_time: datetime,
    end_time: datetime,
    user_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Generate audit summary for compliance reporting.
    
    This would typically query your audit storage backend.
    For now, this is a placeholder.
    
    Args:
        start_time: Start of reporting period
        end_time: End of reporting period
        user_id: Optional user filter
    
    Returns:
        Summary statistics
    """
    # TODO: Implement actual query against audit storage
    # Example: Query S3, Splunk, or audit database
    
    return {
        "period_start": start_time.isoformat(),
        "period_end": end_time.isoformat(),
        "user_id": user_id,
        "total_requests": 0,  # TODO: Implement
        "blocked_requests": 0,  # TODO: Implement
        "guardrails_triggered": 0,  # TODO: Implement
        "unique_users": 0,  # TODO: Implement
        "total_tokens": 0,  # TODO: Implement
        "total_cost_usd": 0.0  # TODO: Implement
    }


if __name__ == "__main__":
    # Test audit logging functions
    import uuid
    
    # Test AI audit event
    audit_event(
        request_id=str(uuid.uuid4()),
        user_id="test_user",
        role="admin",
        action="chat_request",
        model="gpt-4",
        policy_decision="allow",
        guardrail_triggered=False,
        response_status="completed",
        metadata={"test": True}
    )
    
    # Test authentication event
    audit_authentication_event(
        user_id="test_user",
        auth_method="api_key",
        success=True,
        ip_address="127.0.0.1"
    )
    
    # Test guardrail trigger
    audit_guardrail_trigger(
        request_id=str(uuid.uuid4()),
        user_id="test_user",
        guardrail_type="toxicity",
        severity="medium",
        trigger_reason="Mild profanity detected",
        action_taken="flagged"
    )
