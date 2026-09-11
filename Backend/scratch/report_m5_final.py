import sys
import os
from sqlalchemy import text, select
from collections import Counter

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from backend.app.core.postgres import SessionLocal
from backend.app.extraction.models import CandidateEntity, CandidateStatus
from backend.app.resolution.models import ResolvedEntity, CandidateMatch, ResolvedRelationship

BATCH_ID = "4f25f025-4dd9-40fb-bb0a-8338d3a3c3b8"

with SessionLocal() as db:
    # A. CandidateEntity
    cand_after = db.execute(select(CandidateEntity).where(CandidateEntity.batch_id == BATCH_ID)).scalars().all()
    status_dist = Counter([c.status for c in cand_after])
    print("A. CandidateEntity")
    print(f"Total: {len(cand_after)}")
    print(f"Status distribution: {dict(status_dist)}")
    
    # B. CandidateMatch
    match_after = db.execute(
        select(CandidateMatch).join(CandidateEntity).where(CandidateEntity.batch_id == BATCH_ID)
    ).scalars().all()
    conf_dist = Counter([m.confidence_level for m in match_after])
    print("\nB. CandidateMatch")
    print(f"Total: {len(match_after)}")
    print(f"Confidence distribution: {dict(conf_dist)}")
    
    # C. ResolvedEntity
    res_ent_after = db.execute(select(ResolvedEntity)).scalars().all()
    print("\nC. ResolvedEntity")
    print(f"Total: {len(res_ent_after)}")
    
    # D. ResolvedRelationship
    res_rel_after = db.execute(select(ResolvedRelationship)).scalars().all()
    print("\nD. ResolvedRelationship")
    print(f"Total: {len(res_rel_after)}")
    
    # G. Quality
    print("\nG. Quality (10 Representative Matches)")
    for m in match_after[:10]:
        c = db.get(CandidateEntity, m.candidate_entity_id)
        r = db.get(ResolvedEntity, m.resolved_entity_id)
        print(f"- Candidate: '{c.extracted_text}' (Label: {c.canonical_label}) -> Resolved: '{r.canonical_name}' (Label: {r.canonical_label})")
        print(f"  Score: {m.final_weighted_score:.3f} (Confidence: {m.confidence_level})")
        print(f"  Features -> MiniLM: {m.minilm_similarity_score:.3f}, Jaro: {m.name_similarity_score:.3f}, Phone: {m.shared_phone_score}, Account: {m.shared_account_score}")
