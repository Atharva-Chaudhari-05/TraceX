import pytest
import uuid
from backend.app.ingestion.models import CanonicalNodeRecord, CanonicalRelationshipRecord, IngestionBatch
from backend.app.resolution.models import ResolvedEntity
from scripts.bootstrap_m5 import run_bootstrap, get_canonical_name, CANONICAL_LABELS
from scripts.run_demo_projection import DEFAULT_CASES

def setup_bootstrap_data(db_session):
    # Create batch
    batch = IngestionBatch(file_fingerprint="bootstrap_test", file_name="test.csv")
    db_session.add(batch)
    db_session.flush()
    
    # Create a person node
    person_node = CanonicalNodeRecord(
        batch_id=batch.id,
        canonical_id="P1",
        canonical_label="Person",
        payload={
            "id": "P1",
            "name": "Bootstrap Person",
            "Synthetic_Flag": True,
            "Source_Dataset": "TestDataset",
            "Provenance_Mode": "direct",
            "source_record_reference": "SRC-P1",
            "Generation_Batch_ID": "GB-1",
            "Audit_Reference": "AUD-P1"
        },
        audit_reference="AUD-P1"
    )
    db_session.add(person_node)
    
    # Create a case node
    case_node = CanonicalNodeRecord(
        batch_id=batch.id,
        canonical_id=DEFAULT_CASES[0],
        canonical_label="Case",
        payload={
            "id": DEFAULT_CASES[0],
            "case_name": "Test Case",
        },
        audit_reference="AUD-C1"
    )
    db_session.add(case_node)
    db_session.flush()
    
    # Link person to case (INVOLVED_IN)
    rel = CanonicalRelationshipRecord(
        batch_id=batch.id,
        source_id=person_node.canonical_id,
        target_id=case_node.canonical_id,
        relationship_type="INVOLVED_IN",
        payload={"id": str(uuid.uuid4())}
    )
    db_session.add(rel)
    db_session.commit()
    
    return person_node, case_node

def test_get_canonical_name():
    assert get_canonical_name("Person", {"name": "Alice"}) == "Alice"
    assert get_canonical_name("Phone", {"phone_number": "123"}) == "123"
    assert get_canonical_name("Account", {"account_id": "456"}) == "456"
    assert get_canonical_name("Location", {"location_id": "LOC123"}) == "LOC123"
    assert get_canonical_name("Device", {"device_id": "AA:BB"}) == "AA:BB"
    assert get_canonical_name("Document", {"title": "Doc1"}) == "Doc1"
    assert get_canonical_name("Event", {"event_type": "Log", "id": "99"}) == "Log_99"

def test_dry_run_no_writes(db_session):
    setup_bootstrap_data(db_session)
    initial_count = db_session.query(ResolvedEntity).count()
    
    run_bootstrap(case_ids=[DEFAULT_CASES[0]], dry_run=True, db_session=db_session)
    
    # Ensure no writes
    final_count = db_session.query(ResolvedEntity).count()
    assert initial_count == final_count

def test_normal_bootstrap(db_session):
    person, case = setup_bootstrap_data(db_session)
    
    # Run normal
    run_bootstrap(case_ids=[DEFAULT_CASES[0]], dry_run=False, db_session=db_session)
    
    entities = db_session.query(ResolvedEntity).all()
    assert len(entities) == 2  # Person and Case
    
    # Verify Person
    resolved_person = db_session.query(ResolvedEntity).filter_by(canonical_label="Person").first()
    assert resolved_person.canonical_name == "Bootstrap Person"
    assert resolved_person.synthetic_flag is True
    assert resolved_person.source_dataset == "TestDataset"
    assert resolved_person.provenance_mode == "direct"
    assert resolved_person.source_record_reference == "SRC-P1"
    assert resolved_person.generation_batch_id == "GB-1"
    assert resolved_person.audit_reference == "AUD-P1"

def test_idempotency(db_session):
    setup_bootstrap_data(db_session)
    
    # Run once
    run_bootstrap(case_ids=[DEFAULT_CASES[0]], dry_run=False, db_session=db_session)
    count1 = db_session.query(ResolvedEntity).count()
    assert count1 == 2
    
    # Run twice
    run_bootstrap(case_ids=[DEFAULT_CASES[0]], dry_run=False, db_session=db_session)
    count2 = db_session.query(ResolvedEntity).count()
    
    # Count should not increase
    assert count1 == count2
