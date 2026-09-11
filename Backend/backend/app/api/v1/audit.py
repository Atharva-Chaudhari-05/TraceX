from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select, func
from typing import Optional
import uuid

from backend.app.core.postgres import get_db
from backend.app.auth.dependencies import require_role
from backend.app.auth.models import User
from backend.app.audit.models import AuditLog, ActionCategory
from backend.app.audit.schemas import AuditLogPaginatedResponse, AuditLogResponse

router = APIRouter(prefix="/audit", tags=["Audit"])

@router.get("/logs", response_model=AuditLogPaginatedResponse)
def get_audit_logs(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    action_category: Optional[ActionCategory] = None,
    user_id: Optional[uuid.UUID] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["Admin"]))
):
    """
    Retrieve audit logs. Admin only.
    """
    stmt = select(AuditLog)
    count_stmt = select(func.count()).select_from(AuditLog)
    
    if action_category:
        stmt = stmt.where(AuditLog.action_category == action_category)
        count_stmt = count_stmt.where(AuditLog.action_category == action_category)
    if user_id:
        stmt = stmt.where(AuditLog.user_id == user_id)
        count_stmt = count_stmt.where(AuditLog.user_id == user_id)
        
    total = db.scalar(count_stmt) or 0
    
    stmt = stmt.order_by(AuditLog.timestamp.desc()).offset(skip).limit(limit)
    logs = db.scalars(stmt).all()
    
    return AuditLogPaginatedResponse(
        total=total,
        skip=skip,
        limit=limit,
        data=[AuditLogResponse.model_validate(log) for log in logs]
    )
