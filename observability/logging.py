"""
Structured Logging Module

Implements JSON-formatted logging for:
- SIEM integration (Splunk, ELK, Datadog)
- Log aggregation (CloudWatch, Stackdriver)
- Compliance & audit trails
- Debugging & troubleshooting

Log Format:
{
    "timestamp": "2024-02-12T10:30:00.123Z",
    "level": "INFO",
    "event_type": "request_log",
    "user_id": "user_123",
    "role": "admin",
    "request_id": "uuid-here",
    "action": "chat_request",
    "status": "completed",
    "additional_fields": "..."
}

Best Practices:
- Always include timestamp in ISO 8601 format
- Include request_id for distributed tracing
- Use structured fields (not free-form text)
- Log at appropriate levels (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- Redact PII in logs
"""

import logging
import sys
from datetime import datetime
from typing import Optional

from pythonjsonlogger import jsonlogger

# Configure root logger
logger = logging.getLogger("secure-enterprise-ai")
logger.setLevel(logging.INFO)
logger.propagate = False  # Prevent duplicate logs


class CustomJsonFormatter(jsonlogger.JsonFormatter):
    """
    Custom JSON formatter that adds standard fields to every log entry.

    Adds:
    - timestamp (ISO 8601 format)
    - level (INFO, WARNING, ERROR, etc.)
    - logger_name
    - Any custom fields from the log record
    """

    def add_fields(self, log_record: dict, record: logging.LogRecord, message_dict: dict):
        """
        Add standard fields to log record.
        """
        # Add timestamp first
        if not log_record.get("timestamp"):
            log_record["timestamp"] = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%fZ")

        # Add log level
        if log_record.get("level"):
            log_record["level"] = log_record["level"].upper()
        else:
            log_record["level"] = record.levelname

        # Include logger name for debugging
        log_record["logger"] = record.name

        # Now call parent to add remaining fields
        super(CustomJsonFormatter, self).add_fields(log_record, record, message_dict)


# Create console handler with JSON formatting
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.INFO)

# Apply custom JSON formatter
formatter = CustomJsonFormatter(
    "%(timestamp)s %(level)s %(name)s %(message)s",
    rename_fields={"levelname": "level", "name": "logger"},
)
console_handler.setFormatter(formatter)

# Clear existing handlers and add our custom handler
logger.handlers.clear()
logger.addHandler(console_handler)


# Convenience logging functions
def log_event(user_id: str, role: str, request_id: str, action: str, status: str, **kwargs):
    """
    Log a structured event (request, action, etc.).

    Args:
        user_id: User identifier
        role: User role (user, admin, analyst, etc.)
        request_id: Unique request/trace ID
        action: Action being performed
        status: Current status (started, completed, failed, etc.)
        **kwargs: Additional fields to include in log

    Example:
        log_event(
            user_id="user_123",
            role="admin",
            request_id="req_abc",
            action="chat_request",
            status="completed",
            tokens_used=150,
            latency_ms=234
        )
    """
    log_data = {
        "event_type": "request_log",
        "user_id": user_id,
        "role": role,
        "request_id": request_id,
        "action": action,
        "status": status,
        **kwargs,
    }

    logger.info(log_data)


def log_security_event(event_type: str, severity: str, user_id: str, description: str, **kwargs):
    """
    Log a security-related event.

    Args:
        event_type: Type of security event (auth_failure, injection_detected, etc.)
        severity: Severity level (low, medium, high, critical)
        user_id: User identifier
        description: Human-readable description
        **kwargs: Additional context

    Example:
        log_security_event(
            event_type="prompt_injection_detected",
            severity="high",
            user_id="user_123",
            description="Suspicious prompt pattern detected",
            pattern="ignore previous instructions"
        )
    """
    log_data = {
        "event_type": "security_event",
        "security_event_type": event_type,
        "severity": severity,
        "user_id": user_id,
        "description": description,
        **kwargs,
    }

    # Log at WARNING or ERROR level based on severity
    if severity in ["high", "critical"]:
        logger.error(log_data)
    else:
        logger.warning(log_data)


def log_error(
    error_type: str,
    error_message: str,
    user_id: Optional[str] = None,
    request_id: Optional[str] = None,
    **kwargs,
):
    """
    Log an error with context.

    Args:
        error_type: Type of error (validation_error, llm_error, etc.)
        error_message: Error message
        user_id: User identifier (if available)
        request_id: Request ID (if available)
        **kwargs: Additional context

    Example:
        log_error(
            error_type="llm_timeout",
            error_message="LLM request timed out after 30s",
            user_id="user_123",
            request_id="req_abc",
            provider="azure-openai"
        )
    """
    log_data = {
        "event_type": "error",
        "error_type": error_type,
        "error_message": error_message,
        **kwargs,
    }

    if user_id:
        log_data["user_id"] = user_id
    if request_id:
        log_data["request_id"] = request_id

    logger.error(log_data)


def log_performance(
    operation: str,
    duration_ms: float,
    user_id: Optional[str] = None,
    request_id: Optional[str] = None,
    **kwargs,
):
    """
    Log performance metrics.

    Args:
        operation: Operation being measured
        duration_ms: Duration in milliseconds
        user_id: User identifier
        request_id: Request ID
        **kwargs: Additional metrics

    Example:
        log_performance(
            operation="llm_completion",
            duration_ms=1234.5,
            user_id="user_123",
            request_id="req_abc",
            tokens_used=150,
            model="gpt-4"
        )
    """
    log_data = {
        "event_type": "performance",
        "operation": operation,
        "duration_ms": duration_ms,
        **kwargs,
    }

    if user_id:
        log_data["user_id"] = user_id
    if request_id:
        log_data["request_id"] = request_id

    logger.info(log_data)


def log_audit(action: str, user_id: str, resource: str, result: str, **kwargs):
    """
    Log an audit event for compliance.

    Args:
        action: Action performed (create, read, update, delete)
        user_id: User who performed the action
        resource: Resource affected
        result: Result (success, failure, denied)
        **kwargs: Additional audit context

    Example:
        log_audit(
            action="delete_conversation",
            user_id="user_123",
            resource="conversation_abc",
            result="success",
            reason="user_request"
        )
    """
    log_data = {
        "event_type": "audit",
        "action": action,
        "user_id": user_id,
        "resource": resource,
        "result": result,
        **kwargs,
    }

    logger.info(log_data)


# Example usage
if __name__ == "__main__":
    # Test logging functions
    log_event(
        user_id="test_user",
        role="admin",
        request_id="test_req_123",
        action="test_action",
        status="completed",
    )

    log_security_event(
        event_type="test_event",
        severity="medium",
        user_id="test_user",
        description="This is a test security event",
    )

    log_error(error_type="test_error", error_message="This is a test error", user_id="test_user")

    log_performance(operation="test_operation", duration_ms=123.45, user_id="test_user")

    log_audit(action="test_action", user_id="test_user", resource="test_resource", result="success")
