import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict
from backend.app.audit.models import ActionCategory

class AuditLogBase(BaseModel):
    action_category: ActionCategory
    action_detail: str
    entity_type: Optional[str] = None
    entity_id: Optional[str] = None
    metadata_: Optional[dict] = None

class AuditLogResponse(AuditLogBase):
    id: uuid.UUID
    timestamp: datetime
    user_id: Optional[uuid.UUID] = None

    model_config = ConfigDict(from_attributes=True)

class AuditLogPaginatedResponse(BaseModel):
    total: int
    skip: int
    limit: int
    data: list[AuditLogResponse]
