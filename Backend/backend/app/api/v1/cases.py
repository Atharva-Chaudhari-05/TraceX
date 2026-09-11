from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session
from typing import List, Dict, Any

from backend.app.core.postgres import get_db
from backend.app.ingestion.models import CanonicalNodeRecord
from backend.app.auth.dependencies import get_current_user
from backend.app.auth.models import User

router = APIRouter()

@router.get("", response_model=List[Dict[str, Any]])
def get_cases(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Retrieve all case nodes from Postgres."""
    # cases have canonical_label = 'case' or 'Case' (Neo4j usually TitleCase, python schema maybe lowercase)
    stmt = select(CanonicalNodeRecord).where(
        CanonicalNodeRecord.canonical_label.ilike('case')
    ).order_by(CanonicalNodeRecord.created_at.desc())
    
    records = db.scalars(stmt).all()
    
    # Deduplicate cases by ID since multiple ingestions might exist
    seen_cases = set()
    cases = []
    for r in records:
        if r.canonical_id not in seen_cases:
            seen_cases.add(r.canonical_id)
            cases.append({
                "id": r.canonical_id,
                "label": r.canonical_label,
                "payload": r.payload
            })
    return cases

@router.get("/{case_id}", response_model=Dict[str, Any])
def get_case_details(case_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Retrieve details for a specific case."""
    stmt = select(CanonicalNodeRecord).where(
        CanonicalNodeRecord.canonical_id == case_id
    )
    r = db.scalars(stmt).first()
    if not r:
        raise HTTPException(status_code=404, detail="Case not found")
        
    return {
        "id": r.canonical_id,
        "label": r.canonical_label,
        "payload": r.payload
    }
