import subprocess
import sys
from pathlib import Path
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from backend.app.auth.dependencies import get_current_user, require_role
from backend.app.auth.models import User
from backend.app.core.config import settings
from backend.app.core.postgres import get_db
from backend.app.extraction.engine import compute_file_fingerprint
from backend.app.extraction.models import ExtractionBatch, ExtractionStatus
from backend.app.extraction.schemas import ExtractionTriggerResponse, ExtractionBatchResponse

router = APIRouter(prefix="/extraction", tags=["Extraction"])


@router.post("/trigger", response_model=ExtractionTriggerResponse)
def trigger_extraction(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["Admin", "Investigator"]))
):
    """
    Trigger the NLP document extraction pipeline in the background.
    Protected by RBAC (Admin/Investigator).
    """
    # Calculate deterministic fingerprint of the input file
    documents_path = Path(settings.extraction_documents_path)
    if not documents_path.exists():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Source documents file not found."
        )
        
    fingerprint = compute_file_fingerprint(str(documents_path))

    # Create the batch record
    batch = ExtractionBatch(file_fingerprint=fingerprint)
    db.add(batch)
    
    try:
        db.commit()
        db.refresh(batch)
    except IntegrityError:
        db.rollback()
        
        # If it failed, it means a RUNNING or COMPLETED batch already exists for this exact input
        existing = db.query(ExtractionBatch).filter(
            ExtractionBatch.file_fingerprint == fingerprint,
            ExtractionBatch.status.in_([ExtractionStatus.RUNNING, ExtractionStatus.COMPLETED])
        ).first()
        
        if existing:
            status_msg = "is already running" if existing.status == ExtractionStatus.RUNNING else "has already been completed"
            return ExtractionTriggerResponse(
                message=f"Extraction {status_msg} for this document fingerprint.",
                batch_id=existing.id
            )
            
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create extraction batch due to an unknown database constraint."
        )
    
    script_path = Path(__file__).parent.parent.parent.parent.parent / "scripts" / "run_extraction.py"
    
    # Run decoupled subprocess for heavy NLP
    try:
        subprocess.Popen([sys.executable, str(script_path), str(batch.id)])
    except Exception as e:
        # If we can't even start the process
        batch.status = "FAILED"
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to start extraction process: {e}"
        )
        
    return ExtractionTriggerResponse(
        message="Document extraction pipeline started.",
        batch_id=batch.id
    )


@router.get("/status/{batch_id}", response_model=ExtractionBatchResponse)
def get_extraction_status(
    batch_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["Admin", "Investigator"]))
):
    """
    Check the status of a specific extraction batch.
    """
    batch = db.query(ExtractionBatch).filter(ExtractionBatch.id == batch_id).first()
    if not batch:
        raise HTTPException(status_code=404, detail="Extraction batch not found")
        
    return batch
