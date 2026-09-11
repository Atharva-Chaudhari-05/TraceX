import pytest
import uuid
import sqlalchemy as sa
from backend.app.extraction.models import ExtractionBatch, CandidateEntity, CandidateStatus, CandidateRelationship
from backend.app.resolution.models import ResolvedEntity, CandidateMatch, MatchDecision, ConfidenceLevel, ResolvedRelationship
from backend.app.auth.models import User, Role
from backend.app.resolution.engine import ResolutionEngine

def setup_test_data(db):
    # Setup user
    user = User(email=f"test_reviewer_{uuid.uuid4()}@example.com", hashed_password="pwd", is_active=True)
    db.add(user)
    
    # Setup batch
    batch = ExtractionBatch(file_fingerprint=f"test_fingerprint_{uuid.uuid4()}")
    db.add(batch)
    db.flush()
    
    return user, batch

def test_minilm_loading():
    from backend.app.resolution.providers.embedding import get_embedding_provider
    provider = get_embedding_provider()
    embeddings = provider.get_embeddings(["test entity"])
    assert embeddings.shape == (1, 384)

def test_explainable_scoring(db_session):
    # Create test data
    user, batch = setup_test_data(db_session)
    
    # Create a resolved entity with some attributes
    resolved = ResolvedEntity(canonical_name="John Doe", canonical_label="PER")
    db_session.add(resolved)
    db_session.flush()
    
    # We need an underlying CandidateEntity linked to this ResolvedEntity to supply attributes
    res_cand = CandidateEntity(
        batch_id=batch.id, canonical_label="PER", extracted_text="John Doe",
        extraction_method="test", confidence_score=1.0, source_document_id="doc1",
        status=CandidateStatus.RESOLVED, resolved_entity_id=resolved.id
    )
    db_session.add(res_cand)
    db_session.flush()
    
    phone1 = CandidateEntity(
        batch_id=batch.id, canonical_label="Phone", extracted_text="555-1234",
        extraction_method="test", confidence_score=1.0, source_document_id="doc1"
    )
    db_session.add(phone1)
    db_session.flush()
    
    rel1 = CandidateRelationship(
        batch_id=batch.id, source_candidate_id=res_cand.id, target_candidate_id=phone1.id,
        relationship_type="HAS_PHONE", confidence_score=1.0, evidence_span="", extraction_method="test"
    )
    db_session.add(rel1)
    
    # Now create a new candidate to be resolved
    cand = CandidateEntity(
        batch_id=batch.id, canonical_label="PER", extracted_text="John M. Doe",
        extraction_method="test", confidence_score=1.0, source_document_id="doc2",
        status=CandidateStatus.PENDING_RESOLUTION
    )
    db_session.add(cand)
    db_session.flush()
    
    # It shares the phone
    rel2 = CandidateRelationship(
        batch_id=batch.id, source_candidate_id=cand.id, target_candidate_id=phone1.id,
        relationship_type="HAS_PHONE", confidence_score=1.0, evidence_span="", extraction_method="test"
    )
    db_session.add(rel2)
    db_session.commit()
    
    # Run resolution
    engine = ResolutionEngine(db_session)
    engine.run_resolution_batch(batch.id)
    
    # Check Match
    match = db_session.query(CandidateMatch).filter_by(candidate_entity_id=cand.id, resolved_entity_id=resolved.id).first()
    assert match is not None
    assert match.shared_phone_score == 1.0
    assert match.shared_account_score == 0.0
    assert match.spatiotemporal_overlap_score == 0.0
    assert "insufficient evidence" in match.shared_account_evidence
    
    # name sim for "John Doe" and "John M. Doe" is around 0.90
    expected_score = (0.40 * match.name_similarity_score) + 0.30  # + 0 + 0
    assert abs(match.final_weighted_score - expected_score) < 0.001
    
    # Test Confirm Match workflow
    engine.confirm_match(match.id, user.id)
    
    # Verify status
    db_session.refresh(cand)
    db_session.refresh(match)
    assert match.decision == MatchDecision.CONFIRMED
    assert cand.status == CandidateStatus.RESOLVED
    assert cand.resolved_entity_id == resolved.id

def test_net_new_workflow(db_session):
    user, batch = setup_test_data(db_session)
    
    cand = CandidateEntity(
        batch_id=batch.id, canonical_label="ORG", extracted_text="Novel Corp",
        extraction_method="test", confidence_score=1.0, source_document_id="doc3",
        status=CandidateStatus.PENDING_RESOLUTION,
        synthetic_flag=True, audit_reference="audit123"
    )
    db_session.add(cand)
    db_session.commit()
    
    engine = ResolutionEngine(db_session)
    
    # Directly invoke net new
    engine.create_net_new_resolved_entity(cand.id, user.id)
    
    db_session.refresh(cand)
    assert cand.status == CandidateStatus.RESOLVED
    assert cand.resolved_entity_id is not None
    
    resolved = db_session.get(ResolvedEntity, cand.resolved_entity_id)
    assert resolved is not None
    assert resolved.canonical_name == "Novel Corp"
    assert resolved.synthetic_flag is True
    assert resolved.audit_reference == "audit123"
    
    # Verify synthetic match
    match = db_session.query(CandidateMatch).filter_by(candidate_entity_id=cand.id, resolved_entity_id=resolved.id).first()
    assert match is not None
    assert match.decision == MatchDecision.CONFIRMED
    assert match.reviewer_id == user.id

def test_idempotency(db_session):
    user, batch = setup_test_data(db_session)
    
    resolved = ResolvedEntity(canonical_name="Test Entity", canonical_label="PER")
    db_session.add(resolved)
    
    cand = CandidateEntity(
        batch_id=batch.id, canonical_label="PER", extracted_text="Test Entity",
        extraction_method="test", confidence_score=1.0, source_document_id="doc",
        status=CandidateStatus.PENDING_RESOLUTION
    )
    db_session.add(cand)
    db_session.commit()
    
    engine = ResolutionEngine(db_session)
    engine.run_resolution_batch(batch.id)
    
    # 1 match should exist
    matches = db_session.query(CandidateMatch).filter_by(candidate_entity_id=cand.id).all()
    assert len(matches) == 1
    match_id = matches[0].id
    
    # Reject match
    engine.reject_match(match_id, user.id)
    
    # Run again
    engine.run_resolution_batch(batch.id)
    
    # Still 1 match, idempotent
    matches = db_session.query(CandidateMatch).filter_by(candidate_entity_id=cand.id).all()
    assert len(matches) == 1
    assert matches[0].decision == MatchDecision.REJECTED

def test_relationship_resolution_waits_for_endpoints(db_session):
    user, batch = setup_test_data(db_session)
    
    cand1 = CandidateEntity(
        batch_id=batch.id, canonical_label="PER", extracted_text="Alice",
        extraction_method="test", confidence_score=1.0, source_document_id="doc",
        status=CandidateStatus.PENDING_RESOLUTION
    )
    cand2 = CandidateEntity(
        batch_id=batch.id, canonical_label="ORG", extracted_text="Wonderland",
        extraction_method="test", confidence_score=1.0, source_document_id="doc",
        status=CandidateStatus.PENDING_RESOLUTION
    )
    db_session.add_all([cand1, cand2])
    db_session.flush()
    
    rel = CandidateRelationship(
        batch_id=batch.id, source_candidate_id=cand1.id, target_candidate_id=cand2.id,
        relationship_type="WORKS_FOR", confidence_score=1.0, evidence_span="Alice works at Wonderland", extraction_method="test"
    )
    db_session.add(rel)
    db_session.commit()
    
    engine = ResolutionEngine(db_session)
    
    # Resolve first endpoint
    engine.create_net_new_resolved_entity(cand1.id, user.id)
    
    # Check relationship - should not be resolved yet
    db_session.refresh(rel)
    assert rel.status == CandidateStatus.PENDING_RESOLUTION
    
    # Resolve second endpoint
    engine.create_net_new_resolved_entity(cand2.id, user.id)
    
    # Check relationship - should now be resolved
    db_session.refresh(rel)
    assert rel.status == CandidateStatus.RESOLVED
    assert rel.resolved_relationship_id is not None
    
    resolved_rel = db_session.get(ResolvedRelationship, rel.resolved_relationship_id)
    assert resolved_rel is not None
    assert resolved_rel.source_resolved_entity_id == cand1.resolved_entity_id
    assert resolved_rel.target_resolved_entity_id == cand2.resolved_entity_id
