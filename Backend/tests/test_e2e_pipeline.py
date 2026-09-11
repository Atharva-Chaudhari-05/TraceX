import os
import sys
import tempfile
import csv
import pytest
from uuid import uuid4
from unittest.mock import patch

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.app.ingestion.engine import PipelineEngine, compute_file_fingerprint
from backend.app.ingestion.models import IngestionBatch, IngestionStatus
from backend.app.extraction.engine import ExtractionEngine
from backend.app.extraction.models import ExtractionBatch, ExtractionStatus, CandidateEntity
from backend.app.resolution.engine import ResolutionEngine
from backend.app.resolution.models import ResolvedEntity, CandidateMatch
from backend.app.auth.models import User, Role

@pytest.fixture
def admin_user(db_session):
    user = User(email="e2e_admin@tracex.local", hashed_password="pwd", is_active=True)
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user

def create_synthetic_dataset(filepath: str):
    with open(filepath, 'w', newline='', encoding='utf-8') as temp_csv:
        writer = csv.writer(temp_csv)
        writer.writerow(["document_id", "description", "Synthetic_Flag", "Source_Dataset", "source_record_reference", "scenario_id", "Audit_Reference", "Provenance_Mode"])
        writer.writerow(["DOC-1", "John Doe and Jane Smith were seen at the coffee shop.", "True", "mock", "ref1", "scn-1", "audit1", "direct"])
        writer.writerow(["DOC-2", "E2E testing is important for software quality.", "True", "mock", "ref2", "scn-2", "audit2", "direct"])

def test_e2e_pipeline_idempotency(db_session, admin_user):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as f:
        filepath = f.name
    
    try:
        create_synthetic_dataset(filepath)
        fingerprint = compute_file_fingerprint(filepath)
        
        # --- PASS 1 ---
        # 1. Ingestion
        ingestion_engine = PipelineEngine(db_session)
        with patch("os.path.basename", return_value="persons.csv"):
            list(ingestion_engine.process_file(filepath))
            
        ingest_batch = db_session.query(IngestionBatch).filter_by(file_fingerprint=fingerprint).first()
        assert ingest_batch is not None
        assert ingest_batch.status == IngestionStatus.COMPLETED
        
        # 2. Extraction
        ext_batch = ExtractionBatch(file_fingerprint=fingerprint, status=ExtractionStatus.RUNNING)
        db_session.add(ext_batch)
        db_session.commit()
        db_session.refresh(ext_batch)
        
        ext_engine = ExtractionEngine(batch_id=ext_batch.id, db=db_session)
        with patch("backend.app.extraction.engine.settings.extraction_documents_path", filepath):
            ext_engine.run()
            
        db_session.refresh(ext_batch)
        assert ext_batch.status == ExtractionStatus.COMPLETED
        
        candidates = db_session.query(CandidateEntity).filter_by(batch_id=ext_batch.id).all()
        assert len(candidates) > 0
        
        # 3. Resolution
        res_engine = ResolutionEngine(db_session)
        res_engine.run_resolution_batch(ext_batch.id)
        
        matches_pass_1 = db_session.query(CandidateMatch).all()
        # Approve all matches
        for m in matches_pass_1:
            res_engine.confirm_match(m.id, admin_user.id)
            
        resolved_entities_pass_1 = db_session.query(ResolvedEntity).count()
        
        # --- PASS 2 ---
        # 1. Ingestion again
        with patch("os.path.basename", return_value="persons.csv"):
            list(ingestion_engine.process_file(filepath))
        # Should be skipped or no-op (idempotency check)
        
        # 2. Extraction again
        ext_batch_2 = ExtractionBatch(file_fingerprint=fingerprint[:62] + "_2", status=ExtractionStatus.RUNNING)
        db_session.add(ext_batch_2)
        db_session.commit()
        
        ext_engine_2 = ExtractionEngine(batch_id=ext_batch_2.id, db=db_session)
        with patch("backend.app.extraction.engine.settings.extraction_documents_path", filepath):
            ext_engine_2.run()
            
        # 3. Resolution again
        res_engine.run_resolution_batch(ext_batch_2.id)
        
        resolved_entities_pass_2 = db_session.query(ResolvedEntity).count()
        
        # Count should remain the same (no duplicate resolved entities created)
        assert resolved_entities_pass_1 == resolved_entities_pass_2, "Idempotency failed: duplicate entities created on pass 2"
        
    finally:
        os.unlink(filepath)
