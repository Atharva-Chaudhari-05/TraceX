import pytest
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import tempfile
import pandas as pd
from unittest.mock import patch, MagicMock
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi.testclient import TestClient

from backend.app.ingestion.models import IngestionBatch, IngestionStatus, IngestionErrorLog
from backend.app.ingestion.engine import PipelineEngine, compute_file_fingerprint
from backend.app.main import app

def test_fingerprint_deterministic():
    with tempfile.NamedTemporaryFile(delete=False) as f1, tempfile.NamedTemporaryFile(delete=False) as f2:
        f1.write(b"header1,header2\nval1,val2")
        f2.write(b"header1,header2\nval1,val2")
        f1.close()
        f2.close()
        
        hash1 = compute_file_fingerprint(f1.name)
        hash2 = compute_file_fingerprint(f2.name)
        
        assert hash1 == hash2
        
        os.unlink(f1.name)
        os.unlink(f2.name)

def test_fingerprint_different_for_different_content():
    with tempfile.NamedTemporaryFile(delete=False) as f1, tempfile.NamedTemporaryFile(delete=False) as f2:
        f1.write(b"header1,header2\nval1,val2")
        f2.write(b"header1,header2\nval1,val3") # Different content
        f1.close()
        f2.close()
        
        hash1 = compute_file_fingerprint(f1.name)
        hash2 = compute_file_fingerprint(f2.name)
        
        assert hash1 != hash2
        
        os.unlink(f1.name)
        os.unlink(f2.name)


def test_concurrency_idempotency_guard(db_session: Session):
    engine = PipelineEngine(db_session)
    fingerprint = "test_fingerprint_123"
    
    # Simulate first process starting
    batch1 = IngestionBatch(
        file_fingerprint=fingerprint,
        file_name="persons.csv",
        status=IngestionStatus.RUNNING
    )
    db_session.add(batch1)
    db_session.commit()
    
    # Simulate second concurrent process attempting the same
    batch2 = IngestionBatch(
        file_fingerprint=fingerprint,
        file_name="persons.csv",
        status=IngestionStatus.RUNNING
    )
    db_session.add(batch2)
    
    with pytest.raises(IntegrityError):
        db_session.commit()
        
    db_session.rollback()

def test_retry_failed_batch(db_session: Session):
    fingerprint = "test_fingerprint_fail"
    
    # Simulate failed batch
    batch1 = IngestionBatch(
        file_fingerprint=fingerprint,
        file_name="persons.csv",
        status=IngestionStatus.FAILED
    )
    db_session.add(batch1)
    db_session.commit()
    
    # Next attempt should succeed because partial unique index ignores FAILED
    batch2 = IngestionBatch(
        file_fingerprint=fingerprint,
        file_name="persons.csv",
        status=IngestionStatus.RUNNING
    )
    db_session.add(batch2)
    db_session.commit()
    
    assert batch2.id is not None

def test_engine_successful_skip(db_session: Session):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as f:
        f.write(b"person_id\n123")
        f.close()
        
        engine = PipelineEngine(db_session)
        fingerprint = compute_file_fingerprint(f.name)
        
        # Mark as completed
        batch1 = IngestionBatch(
            file_fingerprint=fingerprint,
            file_name=os.path.basename(f.name),
            status=IngestionStatus.COMPLETED
        )
        db_session.add(batch1)
        db_session.commit()
        
        # Engine should safely return None / empty generator without crashing
        gen = engine.process_file(f.name)
        items = list(gen) if gen else []
        
        assert len(items) == 0
        
        os.unlink(f.name)

def test_bounded_error_logging(db_session: Session):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as f:
        # Create CSV with missing mandatory fields (Audit_Reference, Synthetic_Flag)
        content = "person_id,name\n" + "\n".join([f"{i},Test{i}" for i in range(150)])
        f.write(content.encode())
        f.close()
        
        engine = PipelineEngine(db_session)
        
        # Mock file name to match model map
        with patch("os.path.basename", return_value="persons.csv"):
            gen = engine.process_file(f.name)
            list(gen) # consume generator
        
        # Verify batch status
        batch = db_session.query(IngestionBatch).order_by(IngestionBatch.started_at.desc()).first()
        assert batch.status == IngestionStatus.COMPLETED # Engine completes the batch despite row drops
        assert batch.total_rows == 150
        assert batch.error_count == 150
        assert batch.valid_records == 0
        
        # Verify bounded logging (max 100)
        logs = db_session.query(IngestionErrorLog).filter_by(batch_id=batch.id).all()
        assert len(logs) == 100
        
        os.unlink(f.name)

def test_valid_provenance_preservation(db_session: Session):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as f:
        # Create valid row matching Person schema
        content = (
            "person_id,name,Synthetic_Flag,Source_Dataset,source_record_reference,"
            "scenario_id,Audit_Reference,Provenance_Mode\n"
            "P1,John,True,ds1,ref1,scn1,audit1,direct\n"
        )
        f.write(content.encode())
        f.close()
        
        engine = PipelineEngine(db_session)
        with patch("os.path.basename", return_value="persons.csv"):
            gen = engine.process_file(f.name)
            records = list(gen)
        
        assert len(records) == 1
        person = records[0]
        assert person.canonical_label == "Person"
        assert person.person_id == "P1"
        assert person.name == "John"
        assert person.Synthetic_Flag is True
        assert person.Source_Dataset == "ds1"
        assert person.source_record_reference == "ref1"
        assert person.Generation_Batch_ID == "scn1" # mapped from scenario_id
        assert person.Audit_Reference == "audit1"
        assert person.Provenance_Mode == "direct"
        
        os.unlink(f.name)

def test_nullable_provenance_and_relationships(db_session: Session):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as f:
        # relationships.csv mapping test
        content = (
            "relationship_id,source_entity_type,source_entity_id,relationship_type,"
            "target_entity_type,target_entity_id,timestamp,relationship_origin,"
            "Source_Dataset,source_record_reference,reason,Synthetic_Flag,"
            "Generation_Batch_ID,Confidence_Level,Provenance_Mode,"
            "relationship_type_tag,Audit_Reference\n"
            "REL-1,Person,PER-1,OWNS,Account,ACC-1,,,,"
            ",,True,,Medium,synthetic-design,design_synthetic,AUDIT-1\n"
        )
        f.write(content.encode())
        f.close()
        
        engine = PipelineEngine(db_session)
        with patch("os.path.basename", return_value="relationships.csv"):
            gen = engine.process_file(f.name)
            records = list(gen)
            
        assert len(records) == 1, f"Validation failed! Logs: {[err.error_message for err in db_session.query(IngestionErrorLog).all()]}"
        rel = records[0]
        assert rel.source_id == "PER-1"
        assert rel.target_id == "ACC-1"
        assert rel.relationship_type == "OWNS"
        assert rel.timestamp is None
        assert rel.Source_Dataset is None
        assert rel.source_record_reference is None
        assert rel.Synthetic_Flag is True
        
        os.unlink(f.name)

def test_physical_access_event_type_mapping(db_session: Session):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as f:
        content = (
            "physical_event_id,timestamp,person_id,event_type,location_id,"
            "Synthetic_Flag,Source_Dataset,Generation_Batch_ID,"
            "Confidence_Level,Provenance_Mode,Audit_Reference\n"
            "PHY-1,2025-10-11T13:32:03,PER-1,prox-out-classified,LOC-1,"
            "True,,SCN-MIXED-0005,Medium,synthetic-design,AUDIT-PHY-1\n"
        )
        f.write(content.encode())
        f.close()
        
        engine = PipelineEngine(db_session)
        with patch("os.path.basename", return_value="physical_access_events.csv"):
            gen = engine.process_file(f.name)
            records = list(gen)
            
        assert len(records) == 1, f"Validation failed! Logs: {[err.error_message for err in db_session.query(IngestionErrorLog).all()]}"
        evt = records[0]
        assert evt.canonical_label == "Event"
        assert evt.event_type == "PhysicalAccessEvent"
        assert evt.physical_event_id == "PHY-1"
        
        os.unlink(f.name)

def test_communication_event_type_and_null_phones(db_session: Session):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as f:
        # includes "data", "message", "call", string "nan", and float/empty provenance
        content = (
            "communication_id,timestamp,source_phone_id,target_phone_id,event_type,"
            "Synthetic_Flag,Source_Dataset,Generation_Batch_ID,"
            "Confidence_Level,Provenance_Mode,Audit_Reference\n"
            "COM-1,2025-10-11T13:32:03,,,data,True,,,Medium,synthetic-design,AUDIT-COM-1\n"
            "COM-2,2025-10-11T13:32:04,nan,nan,message,True,nan,nan,Medium,synthetic-design,AUDIT-COM-2\n"
            "COM-3,2025-10-11T13:32:05,,,call,True,,,Medium,synthetic-design,AUDIT-COM-3\n"
        )
        f.write(content.encode())
        f.close()
        
        engine = PipelineEngine(db_session)
        with patch("os.path.basename", return_value="communication_events.csv"):
            gen = engine.process_file(f.name)
            records = list(gen)
            
        assert len(records) == 3, f"Validation failed! Logs: {[err.error_message for err in db_session.query(IngestionErrorLog).all()]}"
        
        for i in range(3):
            assert records[i].canonical_label == "Event"
            assert records[i].event_type == "CommunicationEvent"
            assert records[i].Source_Dataset is None
        
        os.unlink(f.name)

def test_network_event_schema_and_nan(db_session: Session):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as f:
        # NetworkEvent with multiple event_types and "nan" strings
        content = (
            "network_event_id,timestamp,source_ip,target_ip,event_type,"
            "Synthetic_Flag,Source_Dataset,Generation_Batch_ID,"
            "Confidence_Level,Provenance_Mode,Audit_Reference\n"
            "NET-1,2025-10-11T13:32:03,192.168.1.1,10.0.0.1,response,True,nan,nan,Medium,synthetic-design,AUDIT-NET-1\n"
            "NET-2,2025-10-11T13:32:04,192.168.1.1,10.0.0.1,request,True,nan,nan,Medium,synthetic-design,AUDIT-NET-2\n"
            "NET-3,2025-10-11T13:32:05,192.168.1.1,10.0.0.1,session,True,nan,nan,Medium,synthetic-design,AUDIT-NET-3\n"
            "NET-4,2025-10-11T13:32:06,192.168.1.1,10.0.0.1,connection,True,nan,nan,Medium,synthetic-design,AUDIT-NET-4\n"
        )
        f.write(content.encode())
        f.close()
        
        engine = PipelineEngine(db_session)
        with patch("os.path.basename", return_value="network_events.csv"):
            gen = engine.process_file(f.name)
            records = list(gen)
            
        assert len(records) == 4, f"Validation failed! Logs: {[err.error_message for err in db_session.query(IngestionErrorLog).all()]}"
        
        for i in range(4):
            assert records[i].canonical_label == "Event"
            assert records[i].event_type == "NetworkEvent"
            assert records[i].Source_Dataset is None
        
        os.unlink(f.name)
