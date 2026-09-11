import sys
import os
import time
from sqlalchemy import text, select
from collections import Counter

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from backend.app.core.postgres import SessionLocal
from backend.app.auth.models import User # Import to populate SQLAlchemy metadata
from backend.app.resolution.engine import ResolutionEngine
from backend.app.extraction.models import CandidateEntity, CandidateStatus
from backend.app.resolution.models import ResolvedEntity, CandidateMatch, ResolvedRelationship, ConfidenceLevel

BATCH_ID = "4f25f025-4dd9-40fb-bb0a-8338d3a3c3b8"

with SessionLocal() as db:
    # 1. Pre-execution verification
    print("--- PRE-EXECUTION VERIFICATION ---")
    resolved_count = db.execute(select(ResolvedEntity)).scalars().all()
    print(f"ResolvedEntity = {len(resolved_count)}")
    
    cand_count = db.execute(select(CandidateEntity).where(CandidateEntity.batch_id == BATCH_ID)).scalars().all()
    print(f"CandidateEntity for batch = {len(cand_count)}")
    
    match_count = db.execute(select(CandidateMatch)).scalars().all()
    print(f"CandidateMatch = {len(match_count)}")
    
    cand_statuses = db.execute(
        text(f"SELECT status, COUNT(*) FROM candidate_entities WHERE batch_id = '{BATCH_ID}' GROUP BY status")
    ).fetchall()
    print(f"CandidateEntity status = {[dict(cand_statuses)]}")
    
    # 2. Execution
    print("\n--- EXECUTING M5 OPTIMIZED RESOLUTION ---")
    engine = ResolutionEngine(db)
    
    start_time = time.time()
    try:
        engine.run_resolution_batch(BATCH_ID)
        error = None
    except Exception as e:
        error = str(e)
        db.rollback()
    end_time = time.time()
    
    print(f"\nExecution time: {end_time - start_time:.2f} seconds")
    
    # 3. Post-execution reporting
    if error:
        print(f"Errors: {error}")
    
    cand_after = db.execute(select(CandidateEntity).where(CandidateEntity.batch_id == BATCH_ID)).scalars().all()
    print(f"CandidateEntity count: {len(cand_after)}")
    
    match_after = db.execute(
        select(CandidateMatch).join(CandidateEntity).where(CandidateEntity.batch_id == BATCH_ID)
    ).scalars().all()
    print(f"CandidateMatch count: {len(match_after)}")
    
    conf_dist = Counter([m.confidence_level for m in match_after])
    print(f"CandidateMatch confidence distribution: {dict(conf_dist)}")
    
    status_dist = Counter([c.status for c in cand_after])
    print(f"CandidateEntity status distribution: {dict(status_dist)}")
    
    print(f"unresolved count (PENDING_RESOLUTION): {status_dist.get(CandidateStatus.PENDING_RESOLUTION, 0)}")
    
    res_ent_after = db.execute(select(ResolvedEntity)).scalars().all()
    print(f"ResolvedEntity count: {len(res_ent_after)}")
    
    res_rel_after = db.execute(select(ResolvedRelationship)).scalars().all()
    print(f"ResolvedRelationship count: {len(res_rel_after)}")
    
    print("\n--- 10 REPRESENTATIVE MATCHES ---")
    for m in match_after[:10]:
        c = db.get(CandidateEntity, m.candidate_entity_id)
        r = db.get(ResolvedEntity, m.resolved_entity_id)
        print(f"Match: Candidate '{c.extracted_text}' -> Resolved '{r.canonical_name}'")
        print(f"  Confidence: {m.confidence_level}, Score: {m.final_weighted_score:.2f}")
        print(f"  MiniLM: {m.minilm_similarity_score}, Jaro: {m.name_similarity_score:.2f}, Phone: {m.shared_phone_score}")
