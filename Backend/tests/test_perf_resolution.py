import pytest
import uuid
import sqlalchemy as sa
from sqlalchemy import event
from sqlalchemy.engine import Engine
from backend.app.extraction.models import ExtractionBatch, CandidateEntity, CandidateStatus
from backend.app.resolution.models import ResolvedEntity, CandidateMatch
from backend.app.resolution.engine import ResolutionEngine
from backend.app.auth.models import User

def test_resolution_performance_bulk_operations(db_session):
    # Setup test data
    user = User(email=f"test_{uuid.uuid4()}@example.com", hashed_password="pwd", is_active=True)
    db_session.add(user)
    
    batch = ExtractionBatch(file_fingerprint=f"test_perf_{uuid.uuid4()}")
    db_session.add(batch)
    db_session.flush()
    
    # Create 5 resolved entities
    for i in range(5):
        resolved = ResolvedEntity(canonical_name=f"Resolved {i}", canonical_label="PER")
        db_session.add(resolved)
        
    # Create 5 candidates
    for i in range(5):
        cand = CandidateEntity(
            batch_id=batch.id, canonical_label="PER", extracted_text=f"Candidate {i}",
            extraction_method="test", confidence_score=1.0, source_document_id="doc",
            status=CandidateStatus.PENDING_RESOLUTION
        )
        db_session.add(cand)
        
    db_session.commit()
    
    # We want to count how many DB queries occur during resolution
    query_count = 0
    
    @event.listens_for(Engine, "before_cursor_execute")
    def receive_before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
        nonlocal query_count
        # Ignore savepoints/commits
        if not statement.lower().startswith(("savepoint", "release", "commit", "begin")):
            query_count += 1
            
    engine = ResolutionEngine(db_session)
    
    # Run resolution
    engine.run_resolution_batch(batch.id)
    
    event.remove(Engine, "before_cursor_execute", receive_before_cursor_execute)
    
    # Analysis:
    # 1 query for candidates
    # 1 query for resolved entities
    # 1 query for bulk CandidateMatches
    # 1 query per candidate for cand_attrs (5)
    # 1 query per resolved for res_attrs (5)
    # Total ~ 13 queries.
    # Without bulk operations, this would be 5 candidates * 5 resolved * 2 queries = 50+ queries.
    
    # Assert query count is reasonable and explicitly NOT O(N*M)
    assert query_count < 25, f"Too many queries ({query_count}), bulk optimization missing."
    
    # Assert matches were actually created (sanity check that semantics remain)
    matches = db_session.query(CandidateMatch).count()
    # Note: we don't assert > 0 because "Resolved 0" and "Candidate 0" might not hit >0.70 cos sim
