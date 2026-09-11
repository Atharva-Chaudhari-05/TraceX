import pytest
from backend.app.resolution.models import ResolvedEntity

def test_resolved_entity_exposes_source_record_reference(db_session):
    """Prove ResolvedEntity exposes source_record_reference and accepts NULL by default."""
    resolved = ResolvedEntity(
        canonical_name="Test No Source Ref",
        canonical_label="Person",
        synthetic_flag=True,
        source_dataset="TestDS",
        provenance_mode="TestMode",
        generation_batch_id="Batch123",
        audit_reference="Audit123"
    )
    db_session.add(resolved)
    db_session.commit()
    db_session.refresh(resolved)
    
    assert resolved.source_record_reference is None
    assert resolved.canonical_name == "Test No Source Ref"
    assert resolved.canonical_label == "Person"
    assert resolved.synthetic_flag is True
    assert resolved.source_dataset == "TestDS"
    assert resolved.provenance_mode == "TestMode"
    assert resolved.generation_batch_id == "Batch123"
    assert resolved.audit_reference == "Audit123"

def test_resolved_entity_persists_source_record_reference(db_session):
    """Prove ResolvedEntity can persist a real source_record_reference."""
    resolved = ResolvedEntity(
        canonical_name="Test With Source Ref",
        canonical_label="Person",
        synthetic_flag=True,
        source_dataset="TestDS",
        provenance_mode="TestMode",
        generation_batch_id="Batch123",
        audit_reference="Audit123",
        source_record_reference="SRC-REF-999"
    )
    db_session.add(resolved)
    db_session.commit()
    db_session.refresh(resolved)
    
    assert resolved.source_record_reference == "SRC-REF-999"
    assert resolved.canonical_name == "Test With Source Ref"
    assert resolved.audit_reference == "Audit123"
