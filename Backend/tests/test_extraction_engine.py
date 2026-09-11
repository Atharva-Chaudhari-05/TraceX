import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
import tempfile
import csv
from pathlib import Path
from unittest.mock import patch
from uuid import uuid4

from backend.app.extraction.models import ExtractionBatch, CandidateEntity, CandidateStatus, ExtractionStatus
from backend.app.extraction.engine import ExtractionEngine, compute_file_fingerprint

def test_extraction_engine(db_session):
    # Setup batch
    batch_id = uuid4()
    batch = ExtractionBatch(id=batch_id, file_fingerprint="dummy_hash_engine_test", status=ExtractionStatus.RUNNING)
    db_session.add(batch)
    db_session.commit()
    
    with tempfile.NamedTemporaryFile(mode='w', newline='', encoding='utf-8', delete=False) as temp_csv:
        writer = csv.writer(temp_csv)
        writer.writerow(["document_id", "description", "synthetic_flag", "source_dataset", "provenance_mode", "source_record_reference", "generation_batch_id", "audit_reference"])
        writer.writerow(["DOC-1", "John Doe called 555-123-4567.", "true", "mock", "synthetic", "ref1", "scn-1", "audit-1"])
        writer.writerow(["DOC-2", "Nothing important here.", "true", "mock", "synthetic", "ref2", "scn-2", "audit-2"])
        temp_csv_path = temp_csv.name
        
    try:
        engine = ExtractionEngine(batch_id=batch_id, db=db_session)
        
        with patch("backend.app.extraction.engine.settings.extraction_documents_path", temp_csv_path):
            engine.run()
            
        db_session.refresh(batch)
        assert batch.status == ExtractionStatus.COMPLETED
        assert batch.processed_documents == 2
        assert batch.total_documents == 2
        
        # We expect a Person (John Doe) and a Phone (555-123-4567) from DOC-1
        candidates = db_session.query(CandidateEntity).filter(CandidateEntity.batch_id == batch_id).all()
        assert len(candidates) > 0
        
        phone_candidate = next((c for c in candidates if c.canonical_label == "Phone"), None)
        assert phone_candidate is not None
        assert phone_candidate.extracted_text == "555-123-4567"
        assert phone_candidate.source_document_id == "DOC-1"
        assert phone_candidate.synthetic_flag is True
        assert phone_candidate.generation_batch_id == "scn-1"
        assert phone_candidate.status == CandidateStatus.PENDING_RESOLUTION
        
    finally:
        os.unlink(temp_csv_path)

def test_compute_file_fingerprint():
    with tempfile.NamedTemporaryFile(mode='w', newline='', encoding='utf-8', delete=False) as f1:
        f1.write("test content")
        f1_name = f1.name
        
    with tempfile.NamedTemporaryFile(mode='w', newline='', encoding='utf-8', delete=False) as f2:
        f2.write("test content")
        f2_name = f2.name
        
    with tempfile.NamedTemporaryFile(mode='w', newline='', encoding='utf-8', delete=False) as f3:
        f3.write("changed content")
        f3_name = f3.name
        
    try:
        hash1 = compute_file_fingerprint(f1_name)
        hash2 = compute_file_fingerprint(f2_name)
        hash3 = compute_file_fingerprint(f3_name)
        
        assert hash1 == hash2 # Deterministic for same content
        assert hash1 != hash3 # Different for different content
        
    finally:
        os.unlink(f1_name)
        os.unlink(f2_name)
        os.unlink(f3_name)
