from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import uuid
from pydantic import BaseModel

from backend.app.core.postgres import get_db
from backend.app.auth.dependencies import get_current_user
from backend.app.auth.models import User
from backend.app.resolution.engine import ResolutionEngine

router = APIRouter(prefix="/resolution", tags=["Resolution"])

class MatchDecisionRequest(BaseModel):
    decision: str  # CONFIRM, REJECT
    
class NetNewRequest(BaseModel):
    candidate_id: uuid.UUID

@router.get("/matches", status_code=status.HTTP_200_OK)
def get_matches(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    from backend.app.resolution.models import CandidateMatch, MatchDecision
    from sqlalchemy import select
    
    stmt = select(CandidateMatch).where(CandidateMatch.decision == MatchDecision.PENDING)
    matches = db.scalars(stmt).all()
    
    results = []
    for m in matches:
        results.append({
            "id": m.id,
            "candidate_entity_id": m.candidate_entity_id,
            "name_similarity_score": m.name_similarity_score,
            "shared_phone_score": m.shared_phone_score,
            "final_weighted_score": m.final_weighted_score,
            "decision": m.decision,
            "shared_phone_evidence": m.shared_phone_evidence,
            "spatiotemporal_evidence": m.spatiotemporal_evidence
        })
    return results

@router.post("/batch/{batch_id}/run", status_code=status.HTTP_202_ACCEPTED)
def run_resolution_batch(
    batch_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    engine = ResolutionEngine(db)
    try:
        engine.run_resolution_batch(batch_id)
        return {"status": "accepted", "message": f"Resolution batch {batch_id} complete."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

from backend.app.audit.service import AuditService
from backend.app.audit.models import ActionCategory

@router.post("/match/{match_id}/decision", status_code=status.HTTP_200_OK)
def make_match_decision(
    match_id: uuid.UUID,
    req: MatchDecisionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    engine = ResolutionEngine(db)
    try:
        if req.decision.upper() == "CONFIRM":
            engine.confirm_match(match_id, current_user.id)
            AuditService.log_action(
                db=db,
                action_category=ActionCategory.RESOLUTION,
                action_detail="Confirmed match",
                user_id=current_user.id,
                action_metadata={"match_id": str(match_id), "decision": "CONFIRM"}
            )
            db.commit()
            return {"status": "confirmed"}
        elif req.decision.upper() == "REJECT":
            engine.reject_match(match_id, current_user.id)
            AuditService.log_action(
                db=db,
                action_category=ActionCategory.RESOLUTION,
                action_detail="Rejected match",
                user_id=current_user.id,
                action_metadata={"match_id": str(match_id), "decision": "REJECT"}
            )
            db.commit()
            return {"status": "rejected"}
        else:
            raise HTTPException(status_code=400, detail="Invalid decision. Use CONFIRM or REJECT.")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/candidate/net-new", status_code=status.HTTP_201_CREATED)
def create_net_new_entity(
    req: NetNewRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    engine = ResolutionEngine(db)
    try:
        engine.create_net_new_resolved_entity(req.candidate_id, current_user.id)
        AuditService.log_action(
            db=db,
            action_category=ActionCategory.RESOLUTION,
            action_detail="Created net-new entity",
            user_id=current_user.id,
            action_metadata={"candidate_id": str(req.candidate_id)}
        )
        db.commit()
        return {"status": "created", "candidate_id": req.candidate_id}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
