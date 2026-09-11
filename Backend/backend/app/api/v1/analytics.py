from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from backend.app.core.postgres import get_db
from backend.app.auth.dependencies import require_role
from backend.app.auth.models import User
from backend.app.analytics.engine import NetworkAnalyticsEngine
from backend.app.analytics.models import NetworkAnalyticsResponse
from backend.app.audit.service import AuditService
from backend.app.audit.models import ActionCategory

router = APIRouter()

def get_analytics_engine() -> NetworkAnalyticsEngine:
    return NetworkAnalyticsEngine()

@router.get("/network", response_model=NetworkAnalyticsResponse)
def get_network_analytics(
    case_id: str = Query(..., description="The ID of the case to analyze"),
    current_user: User = Depends(require_role(["Admin", "Investigator", "Analyst"])),
    engine: NetworkAnalyticsEngine = Depends(get_analytics_engine),
    db: Session = Depends(get_db)
):
    """
    Get deterministic structural network analytics for a case.
    """
    try:
        result = engine.execute_analytics(case_id)
        AuditService.log_action(
            db=db,
            action_category=ActionCategory.CASE_ACCESS,
            action_detail="Network analytics access",
            user_id=current_user.id,
            action_metadata={"case_id": case_id}
        )
        db.commit()
        return NetworkAnalyticsResponse(**result)
    except ValueError as ve:
        if "Payload Too Large" in str(ve):
            raise HTTPException(status_code=413, detail=str(ve))
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
