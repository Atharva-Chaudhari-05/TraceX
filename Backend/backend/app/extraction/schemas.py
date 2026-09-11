from datetime import datetime
from typing import Optional, List, Dict, Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from backend.app.extraction.models import ExtractionStatus, CandidateStatus


class ExtractionTriggerResponse(BaseModel):
    message: str
    batch_id: UUID


class CandidateEntityResponse(BaseModel):
    id: UUID
    batch_id: UUID
    
    canonical_label: str
    extracted_text: str
    normalized_payload: Dict[str, Any]
    
    extraction_method: str
    confidence_score: float
    status: CandidateStatus
    
    source_document_id: str
    generation_batch_id: Optional[str] = None
    audit_reference: Optional[str] = None
    synthetic_flag: Optional[bool] = None
    source_dataset: Optional[str] = None
    provenance_mode: Optional[str] = None
    source_record_reference: Optional[str] = None
    
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ExtractionBatchResponse(BaseModel):
    id: UUID
    status: ExtractionStatus
    total_documents: int
    processed_documents: int
    candidates_extracted: int
    error_count: int
    started_at: datetime
    completed_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
