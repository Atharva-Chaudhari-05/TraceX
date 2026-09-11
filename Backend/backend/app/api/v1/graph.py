from typing import Dict, List, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from backend.app.auth.dependencies import require_role
from backend.app.auth.models import User
from backend.app.graph.engine import GraphEngine
from backend.app.core.postgres import get_db
from backend.app.audit.service import AuditService
from backend.app.audit.models import ActionCategory

router = APIRouter()

def get_graph_engine() -> GraphEngine:
    return GraphEngine()

@router.get("/neighborhood/{node_id}")
def get_neighborhood(
    node_id: str,
    depth: int = Query(1, ge=1, le=2),
    limit: int = Query(100, ge=1, le=500),
    current_user: User = Depends(require_role(["Admin", "Investigator"])),
    engine: GraphEngine = Depends(get_graph_engine),
    db: Session = Depends(get_db)
):
    """
    Bounded traversal of ego-graph neighborhood.
    """
    try:
        result = engine.get_neighborhood(node_id, depth, limit)
        AuditService.log_action(
            db=db,
            action_category=ActionCategory.CASE_ACCESS,
            action_detail="Graph neighborhood access",
            user_id=current_user.id,
            action_metadata={"node_id": node_id, "depth": depth, "limit": limit}
        )
        db.commit()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/path")
def get_shortest_path(
    source: str = Query(...),
    target: str = Query(...),
    max_depth: int = Query(4, ge=1, le=6),
    limit: int = Query(5, ge=1, le=20),
    current_user: User = Depends(require_role(["Admin", "Investigator"])),
    engine: GraphEngine = Depends(get_graph_engine),
    db: Session = Depends(get_db)
):
    """
    Bounded shortest path traversal.
    """
    try:
        result = engine.get_shortest_path(source, target, max_depth, limit)
        AuditService.log_action(
            db=db,
            action_category=ActionCategory.CASE_ACCESS,
            action_detail="Graph path access",
            user_id=current_user.id,
            action_metadata={"source": source, "target": target, "max_depth": max_depth, "limit": limit}
        )
        db.commit()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
