from fastapi import APIRouter, Depends, HTTPException, Query, Path
from sqlalchemy.orm import Session
from backend.app.core.postgres import get_db
from backend.app.auth.dependencies import require_role
from backend.app.auth.models import User
from backend.app.analytics.ml_engine import MLEngine
from backend.app.analytics.models import MLTrainRequest, MLTrainResponse, MLInferenceResponse
from backend.app.audit.service import AuditService
from backend.app.audit.models import ActionCategory

router = APIRouter()

def get_ml_engine() -> MLEngine:
    return MLEngine()

@router.post("/train", response_model=MLTrainResponse)
def train_models(
    request: MLTrainRequest,
    current_user: User = Depends(require_role(["Admin"])),
    engine: MLEngine = Depends(get_ml_engine),
    db: Session = Depends(get_db)
):
    """
    Train M8 ML Models on synthetic dataset (Admin only).
    """
    try:
        result = engine.train_models(case_ids=request.case_ids, target_definition=request.target_definition)
        AuditService.log_action(
            db=db,
            action_category=ActionCategory.ADMIN,
            action_detail="Trained ML models",
            user_id=current_user.id,
            action_metadata={"target_definition": request.target_definition, "model_version": result.get("model_version")}
        )
        db.commit()
        return MLTrainResponse(**result)
    except ValueError as ve:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/case/{case_id}/signals", response_model=MLInferenceResponse)
def infer_signals(
    case_id: str = Path(..., description="The ID of the case to analyze"),
    current_user: User = Depends(require_role(["Admin", "Investigator", "Analyst"])),
    engine: MLEngine = Depends(get_ml_engine),
    db: Session = Depends(get_db)
):
    """
    Generate ML analytical signals for a given case.
    """
    try:
        result = engine.infer_case(case_id)
        AuditService.log_action(
            db=db,
            action_category=ActionCategory.CASE_ACCESS,
            action_detail="Generated ML signals",
            user_id=current_user.id,
            action_metadata={"case_id": case_id, "model_version": result.get("model_version"), "feature_schema_version": result.get("feature_schema_version")}
        )
        db.commit()
        return MLInferenceResponse(**result)
    except ValueError as ve:
        if "Payload Too Large" in str(ve):
            raise HTTPException(status_code=413, detail=str(ve))
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
