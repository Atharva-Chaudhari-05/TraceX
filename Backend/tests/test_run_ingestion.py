import pytest
import os
import sys
import tempfile
from unittest.mock import patch

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from backend.app.ingestion.models import IngestionBatch, CanonicalNodeRecord, CanonicalRelationshipRecord, IngestionStatus, IngestionErrorLog
from scripts.run_ingestion import run_ingestion
from scripts.run_projection import run_projection

def test_run_ingestion_decoupled_from_neo4j(db_session: Session):
    """
    Test that M3 ingestion successfully parses CSVs and persists CanonicalNodeRecord 
    and CanonicalRelationshipRecord to PostgreSQL without requiring Neo4j.
    """
    db_session.query(CanonicalNodeRecord).delete()
    db_session.query(CanonicalRelationshipRecord).delete()
    db_session.query(IngestionBatch).delete()
    db_session.commit()
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create a mock person file
        person_file = os.path.join(tmpdir, "persons.csv")
        with open(person_file, "w") as f:
            f.write(
                "person_id,name,Synthetic_Flag,Source_Dataset,source_record_reference,"
                "scenario_id,Audit_Reference,Provenance_Mode\n"
                "PER-100,TestUser,True,ds1,ref1,scn1,AUDIT-100,direct\n"
            )
            
        # Create a mock relationships file
        rel_file = os.path.join(tmpdir, "relationships.csv")
        with open(rel_file, "w") as f:
            f.write(
                "relationship_id,source_entity_type,source_entity_id,relationship_type,"
                "target_entity_type,target_entity_id,timestamp,relationship_origin,"
                "Source_Dataset,source_record_reference,reason,Synthetic_Flag,"
                "Generation_Batch_ID,Confidence_Level,Provenance_Mode,"
                "relationship_type_tag,Audit_Reference\n"
                "REL-100,Person,PER-100,OWNS,Account,ACC-100,,,,"
                ",,True,,Medium,synthetic-design,design_synthetic,AUDIT-REL-100\n"
            )
            
        # Run ingestion - GraphEngine is NOT mocked because it's not imported/used
        run_ingestion(tmpdir)
        
        # Verify M3 persistence in PostgreSQL for the newly created batches
        from backend.app.ingestion.engine import compute_file_fingerprint
        person_fingerprint = compute_file_fingerprint(person_file)
        rel_fingerprint = compute_file_fingerprint(rel_file)
        
        batches = db_session.query(IngestionBatch).filter(IngestionBatch.file_fingerprint.in_([person_fingerprint, rel_fingerprint])).all()
        assert len(batches) == 2
        batch_ids = [b.id for b in batches]
        for batch in batches:
            assert batch.status == IngestionStatus.COMPLETED
            
        nodes = db_session.query(CanonicalNodeRecord).filter(CanonicalNodeRecord.batch_id.in_(batch_ids)).all()
        assert len(nodes) == 1
        assert nodes[0].canonical_id == "PER-100"
        assert nodes[0].canonical_label == "Person"
        assert nodes[0].audit_reference == "AUDIT-100"
        assert nodes[0].payload["name"] == "TestUser"
        
        edges = db_session.query(CanonicalRelationshipRecord).filter(CanonicalRelationshipRecord.batch_id.in_(batch_ids)).all()
        assert len(edges) == 1
        assert edges[0].source_id == "PER-100"
        assert edges[0].target_id == "ACC-100"
        assert edges[0].relationship_type == "OWNS"
        assert edges[0].audit_reference == "AUDIT-REL-100"


def test_run_projection_success(db_session: Session):
    """
    Test that M6 projection consumes records from PostgreSQL independently.
    """
    db_session.query(CanonicalNodeRecord).delete()
    db_session.query(CanonicalRelationshipRecord).delete()
    db_session.query(IngestionBatch).delete()
    db_session.commit()
    # Seed PostgreSQL Canonical tables manually
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create a mock person file
        person_file = os.path.join(tmpdir, "persons.csv")
        with open(person_file, "w") as f:
            f.write(
                "person_id,name,Synthetic_Flag,Source_Dataset,source_record_reference,"
                "scenario_id,Audit_Reference,Provenance_Mode\n"
                "PER-200,TestUser2,True,ds2,ref2,scn2,AUDIT-200,direct\n"
            )
        run_ingestion(tmpdir)
        
        batch = db_session.query(IngestionBatch).order_by(IngestionBatch.started_at.desc()).first()
        batch_id = batch.id
        
        nodes = db_session.query(CanonicalNodeRecord).filter_by(batch_id=batch_id).all()
        assert len(nodes) == 1
        
        # Run projection and verify it calls Neo4j GraphEngine sync methods
        with patch("scripts.run_projection.GraphEngine") as MockGraphEngine:
            mock_graph_engine_instance = MockGraphEngine.return_value
            
            # Explicitly run projection for this batch only
            run_projection(batch_id=batch_id)
            
            # Verify Neo4j received the payload
            assert mock_graph_engine_instance.bulk_sync_canonical_nodes.call_count == 1
            call_args = mock_graph_engine_instance.bulk_sync_canonical_nodes.call_args[0][0]
            assert len(call_args) == 1
            assert call_args[0]["id"] == "PER-200"


def test_projection_failure_does_not_invalidate_m3_data(db_session: Session):
    """
    Test that if GraphEngine throws an error during M6 projection,
    the PostgreSQL M3 CanonicalRecords remain safely stored and queryable.
    """
    db_session.query(CanonicalNodeRecord).delete()
    db_session.query(CanonicalRelationshipRecord).delete()
    db_session.query(IngestionBatch).delete()
    db_session.commit()
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create a mock person file
        person_file = os.path.join(tmpdir, "persons.csv")
        with open(person_file, "w") as f:
            f.write(
                "person_id,name,Synthetic_Flag,Source_Dataset,source_record_reference,"
                "scenario_id,Audit_Reference,Provenance_Mode\n"
                "PER-300,TestUser3,True,ds3,ref3,scn3,AUDIT-300,direct\n"
            )
        run_ingestion(tmpdir)
        
        batch = db_session.query(IngestionBatch).order_by(IngestionBatch.started_at.desc()).first()
        batch_id = batch.id
        
        # Ensure M3 data is there
        assert db_session.query(CanonicalNodeRecord).filter_by(batch_id=batch_id).count() == 1
        
        # Run projection with a mock that raises an exception
        with patch("scripts.run_projection.GraphEngine") as MockGraphEngine:
            mock_graph_engine_instance = MockGraphEngine.return_value
            mock_graph_engine_instance.bulk_sync_canonical_nodes.side_effect = Exception("Neo4j is down!")
            
            # Should not crash ungracefully, but should report failures
            run_projection(batch_id=batch_id)
            
        # Verify M3 PostgreSQL data is completely unaffected
        nodes = db_session.query(CanonicalNodeRecord).filter_by(batch_id=batch_id).all()
        assert len(nodes) == 1
        assert nodes[0].canonical_id == "PER-300"

def test_bulk_projection_chunking(db_session: Session):
    """
    Test that M6 projection chunks nodes and relationships properly.
    """
    from backend.app.core.postgres import SessionLocal
    with SessionLocal() as db:
        db.query(CanonicalNodeRecord).delete()
        db.query(CanonicalRelationshipRecord).delete()
        db.query(IngestionBatch).delete()
        db.commit()
        
        batch = IngestionBatch(file_fingerprint="chunk_test", file_name="chunk_test.csv")
        db.add(batch)
        db.commit()
        
        # Create 5 nodes
        for i in range(5):
            node = CanonicalNodeRecord(
                batch_id=batch.id,
                canonical_id=f"N-{i}",
                canonical_label="Person",
                payload={"name": f"User{i}"}
            )
            db.add(node)
            
        # Create 5 relationships
        for i in range(5):
            rel = CanonicalRelationshipRecord(
                batch_id=batch.id,
                source_id=f"N-{i}",
                target_id=f"N-{(i+1)%5}",
                relationship_type="KNOWS", 
                payload={} 
            )
            db.add(rel)
            
        db.commit()
        batch_id = batch.id
    
    with patch("scripts.run_projection.GraphEngine") as MockGraphEngine:
        mock_graph_engine_instance = MockGraphEngine.return_value
        
        # Run projection with chunk_size=2
        run_projection(batch_id=batch_id, chunk_size=2)
        
        # 5 items / chunk_size 2 => 3 calls (2, 2, 1)
        assert mock_graph_engine_instance.bulk_sync_canonical_nodes.call_count == 3
        
        # check args lengths for nodes
        calls = mock_graph_engine_instance.bulk_sync_canonical_nodes.call_args_list
        assert len(calls[0][0][0]) == 2
        assert len(calls[1][0][0]) == 2
        assert len(calls[2][0][0]) == 1
        
        # check relationship chunks
        assert mock_graph_engine_instance.bulk_sync_canonical_relationships.call_count == 3
        rel_calls = mock_graph_engine_instance.bulk_sync_canonical_relationships.call_args_list
        assert len(rel_calls[0][0][0]) == 2
        assert len(rel_calls[1][0][0]) == 2
        assert len(rel_calls[2][0][0]) == 1

def test_bulk_sync_unsupported_rel(db_session: Session):
    """
    Ensure unsupported relationship types are rejected during bulk sync.
    """
    from backend.app.graph.engine import GraphEngine
    engine = GraphEngine()
    
    with pytest.raises(ValueError, match="Unsupported relationship type: INVALID_REL"):
        engine.bulk_sync_canonical_relationships([{
            "relationship_type": "INVALID_REL",
            "source_id": "A",
            "target_id": "B"
        }])

def test_run_ingestion_datetime_serialization(db_session, tmpdir):
    """
    Ensure payloads containing datetime objects (like Incident) 
    are correctly serialized to JSON-safe representations and inserted.
    """
    db_session.query(CanonicalNodeRecord).delete()
    db_session.query(CanonicalRelationshipRecord).delete()
    db_session.query(IngestionBatch).delete()
    db_session.commit()
    
    with tempfile.TemporaryDirectory() as temp_dir:
        incident_file = os.path.join(temp_dir, "incidents.csv")
        with open(incident_file, "w") as f:
            f.write(
                "incident_id,timestamp,Synthetic_Flag,Source_Dataset,"
                "source_record_reference,scenario_id,Audit_Reference,Provenance_Mode\n"
                "INC-123,2023-10-24T12:00:00Z,True,ds1,ref1,scn1,AUDIT-INC,direct\n"
            )
        
        # This will fail if datetime is not correctly serialized to JSON string in run_ingestion
        run_ingestion(temp_dir)
        
        batch = db_session.query(IngestionBatch).order_by(IngestionBatch.started_at.desc()).first()
        assert batch is not None
        assert batch.status == IngestionStatus.COMPLETED
        
        nodes = db_session.query(CanonicalNodeRecord).filter_by(batch_id=batch.id).all()
        assert len(nodes) == 1
        assert nodes[0].canonical_id == "INC-123"
        assert nodes[0].canonical_label == "Event"
        assert nodes[0].event_type == "Incident"
        
        payload = nodes[0].payload
        assert payload["incident_id"] == "INC-123"
        assert payload["Synthetic_Flag"] is True
        # timestamp should be an ISO 8601 string, not a Python datetime object in the JSON payload
        assert "T" in payload["timestamp"]
        
        # Ensure None values are preserved
        assert payload["Source_Dataset"] == "ds1"


def test_run_ingestion_crime_context(db_session, tmpdir):
    """
    Ensure crime_context.csv maps to CrimeStatistic, uses context_id as canonical_id,
    and preserves provenance exactly.
    """
    db_session.query(CanonicalNodeRecord).delete()
    db_session.query(CanonicalRelationshipRecord).delete()
    db_session.query(IngestionBatch).delete()
    db_session.commit()
    
    with tempfile.TemporaryDirectory() as temp_dir:
        file_path = os.path.join(temp_dir, "crime_context.csv")
        with open(file_path, "w") as f:
            f.write(
                "context_id,year,state_ut,city,crime_category,crime_count,measure_type,"
                "data_origin,source_dataset,source_record_reference,Synthetic_Flag,"
                "Source_Dataset,Generation_Batch_ID,Confidence_Level,Provenance_Mode,"
                "Audit_Reference\n"
                "CTX-001,2024,Maharashtra,Nashik,fraud,12988,aggregate_count,DERIVED,"
                "01_NCRB,ref_001,False,01_NCRB,batch_x,High,synthetic-design,"
                "AUDIT-CTX-001\n"
            )
        
        run_ingestion(temp_dir)
        
        batch = db_session.query(IngestionBatch).order_by(IngestionBatch.started_at.desc()).first()
        assert batch is not None
        assert batch.status == IngestionStatus.COMPLETED
        
        nodes = db_session.query(CanonicalNodeRecord).filter_by(batch_id=batch.id).all()
        assert len(nodes) == 1
        assert nodes[0].canonical_id == "CTX-001"
        assert nodes[0].canonical_label == "CrimeStatistic"
        assert nodes[0].audit_reference == "AUDIT-CTX-001"
        
        payload = nodes[0].payload
        assert payload["context_id"] == "CTX-001"
        assert payload["year"] == 2024  # Pydantic schema casts to int
        assert payload["crime_count"] == 12988
        assert payload["city"] == "Nashik"
        assert payload["Confidence_Level"] == "High"
        assert payload["Synthetic_Flag"] is False
        assert payload["Source_Dataset"] == "01_NCRB"
        assert payload["Provenance_Mode"] == "synthetic-design"
        assert payload["Generation_Batch_ID"] == "batch_x"
        assert payload["source_record_reference"] == "ref_001"
        assert payload["source_dataset"] == "01_NCRB"

def test_run_ingestion_unknown_file(db_session, tmpdir):
    """
    Ensure unknown files are safely failed with the intended mapping error.
    """
    db_session.query(CanonicalNodeRecord).delete()
    db_session.query(CanonicalRelationshipRecord).delete()
    db_session.query(IngestionBatch).delete()
    db_session.commit()
    
    with tempfile.TemporaryDirectory() as temp_dir:
        file_path = os.path.join(temp_dir, "unknown_data.csv")
        with open(file_path, "w") as f:
            f.write("col1,col2\nval1,val2\n")
        
        run_ingestion(temp_dir)
        
        batch = db_session.query(IngestionBatch).order_by(IngestionBatch.started_at.desc()).first()
        assert batch is not None
        assert batch.status == IngestionStatus.FAILED
        
        errors = db_session.query(IngestionErrorLog).filter_by(batch_id=batch.id).all()
        assert len(errors) == 1
        assert "Unknown file format / model mapping" in errors[0].error_message
