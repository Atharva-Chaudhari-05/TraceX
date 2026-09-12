from typing import List, Optional
import subprocess
import os
import sys
import shutil
import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, UploadFile, File
from sqlalchemy.orm import Session
from sqlalchemy import select

from backend.app.core.postgres import get_db
from backend.app.auth.dependencies import get_current_user, require_role
from backend.app.auth.models import User
from backend.app.ingestion.models import IngestionBatch
from pydantic import BaseModel, UUID4

router = APIRouter()

class IngestionBatchResponse(BaseModel):
    id: UUID4
    file_name: str
    status: str
    total_rows: int
    processed_rows: int
    valid_records: int
    error_count: int
    duration_seconds: Optional[int]

    class Config:
        from_attributes = True


@router.get("/status", response_model=List[IngestionBatchResponse])
def get_ingestion_status(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["Admin", "Investigator"]))
):
    """
    Retrieves the status of all ingestion batches.
    """
    batches = db.execute(select(IngestionBatch).order_by(IngestionBatch.started_at.desc())).scalars().all()
    
    response = []
    for batch in batches:
        duration = None
        if batch.completed_at and batch.started_at:
            duration = int((batch.completed_at - batch.started_at).total_seconds())
        elif batch.started_at:
            from datetime import datetime, timezone
            duration = int((datetime.now(timezone.utc) - batch.started_at).total_seconds())

        response.append(IngestionBatchResponse(
            id=batch.id,
            file_name=batch.file_name,
            status=batch.status.value,
            total_rows=batch.total_rows,
            processed_rows=batch.processed_rows,
            valid_records=batch.valid_records,
            error_count=batch.error_count,
            duration_seconds=duration
        ))
    return response


@router.post("/trigger")
def trigger_ingestion(
    current_user: User = Depends(require_role(["Admin"]))
):
    """
    Orchestrates the ingestion CLI script via a decoupled subprocess.
    Ensures the web server thread is not blocked by a 2.3GB dataset payload.
    """
    script_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "scripts", "run_ingestion.py")
    
    if not os.path.exists(script_path):
        raise HTTPException(status_code=500, detail="Ingestion script not found.")
    
    # Fire and forget subprocess
    # In a real enterprise system this would dispatch to a queue, but here we use Popen
    subprocess.Popen([sys.executable, script_path])
    
    return {"message": "Ingestion process triggered in background.", "status": "Subprocess Dispatched"}

def run_pipeline_for_folder(folder_path: str):
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    ingest_script = os.path.join(base_dir, "scripts", "run_ingestion.py")
    project_script = os.path.join(base_dir, "scripts", "run_projection.py")
    
    # Run Ingestion
    subprocess.run([sys.executable, ingest_script, "--source", folder_path], check=True)
    # Run Projection
    subprocess.run([sys.executable, project_script], check=True)

@router.post("/upload")
async def upload_file(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    current_user: User = Depends(require_role(["Admin", "Investigator"]))
):
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
    upload_dir = os.path.join(base_dir, "scratch", "ui_uploads", str(uuid.uuid4()))
    os.makedirs(upload_dir, exist_ok=True)
    
    file_path = os.path.join(upload_dir, file.filename)
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    background_tasks.add_task(run_pipeline_for_folder, upload_dir)
    
    return {"message": "File uploaded successfully. Ingestion pipeline started.", "file_name": file.filename}

