"""Audit logging service for security-relevant events.

Stage 8 — audit logging infrastructure.

This service centralizes the creation of security audit records.  It is
intentionally separate from application logging: audit records answer
"what security-relevant event happened, who caused it, and when?" while
application logging serves developer/operator diagnostics.

The service is request-safe: it never stores global mutable state and never
raises exceptions that could interfere with the security decision being
audited.  If persistence fails, the error is logged through application
logging and the request continues normally.
"""

import json
import logging
from typing import Any

from sqlalchemy.orm import Session

from app.models.audit import AuditLog

logger = logging.getLogger(__name__)

# Canonical security event types.  Keep the taxonomy small and stable.
LOGIN_SUCCESS = "LOGIN_SUCCESS"
LOGIN_FAILURE = "LOGIN_FAILURE"
AUTH_FAILURE = "AUTH_FAILURE"
AUTHORIZATION_DENIED = "AUTHORIZATION_DENIED"


def log_event(
    db: Session,
    action: str,
    actor: str | None = None,
    details: dict[str, Any] | None = None,
) -> None:
    """Persist a security audit record.

    Args:
        db: The active SQLAlchemy session.
        action: The canonical security event type (see module constants).
        actor: Stable identity of the actor (e.g. user ID as string), or
            ``None`` for unauthenticated events.
        details: Optional structured context.  Must never contain passwords,
            password hashes, JWTs, secrets, or Authorization headers.

    The function is best-effort: it never raises.  If persistence fails,
    the error is logged via application logging and the request continues.
    """
    try:
        record = AuditLog(
            action=action,
            actor=actor,
            details=json.dumps(details) if details else None,
        )
        db.add(record)
        db.commit()
    except Exception:
        db.rollback()
        logger.exception("Failed to persist audit record for action=%s", action)