import uuid
from sqlalchemy.orm import Session
from backend.app.audit.models import AuditLog, ActionCategory
from backend.app.core.context import get_request_id

SENSITIVE_KEYS = {"password", "token", "secret", "jwt", "authorization", "hashed_password", "key"}

def _sanitize_metadata(data):
    """
    Recursively sanitize metadata by redacting sensitive keys.
    """
    if isinstance(data, dict):
        sanitized = {}
        for k, v in data.items():
            if any(sensitive in k.lower() for sensitive in SENSITIVE_KEYS):
                sanitized[k] = "[REDACTED]"
            else:
                sanitized[k] = _sanitize_metadata(v)
        return sanitized
    elif isinstance(data, list):
        return [_sanitize_metadata(item) for item in data]
    else:
        return data

class AuditService:
    @staticmethod
    def log_action(
        db: Session,
        action_category: ActionCategory,
        action_detail: str,
        user_id: uuid.UUID | None = None,
        entity_type: str | None = None,
        entity_id: str | None = None,
        action_metadata: dict | None = None
    ) -> AuditLog:
        """
        Log an action to the audit trail.
        Adds the AuditLog to the provided SQLAlchemy session but does NOT commit.
        The caller must commit the transaction.
        """
        req_id = get_request_id()
        
        safe_metadata = {}
        if action_metadata:
            safe_metadata = _sanitize_metadata(action_metadata)
        
        if req_id:
            safe_metadata["request_id"] = req_id

        audit_record = AuditLog(
            user_id=user_id,
            action_category=action_category,
            action_detail=action_detail,
            entity_type=entity_type,
            entity_id=entity_id,
            metadata_=safe_metadata if safe_metadata else None
        )
        
        db.add(audit_record)
        return audit_record
