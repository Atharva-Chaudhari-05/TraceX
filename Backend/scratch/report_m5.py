import sys
import os
from collections import Counter
from sqlalchemy import text

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from backend.app.core.postgres import SessionLocal
from backend.app.resolution.models import CandidateMatch, ResolvedEntity, ResolvedRelationship
from backend.app.extraction.models import CandidateEntity

def report(batch_id_str):
    print("=" * 70)
    print("M5 Resolution Report")
    print("=" * 70)
    
    with SessionLocal() as db:
        # 1. CandidateEntity count for this batch
        candidates = db.query(CandidateEntity).filter(CandidateEntity.batch_id == batch_id_str).all()
        total_candidates = len(candidates)
        print(f"1. CandidateEntity count for batch: {total_candidates}")
        
        # 2. CandidateEntity status distribution
        statuses = [c.status for c in candidates]
        status_dist = Counter(statuses)
        print(f"2. CandidateEntity status distribution: {dict(status_dist)}")
        
        # 3. CandidateMatch count
        candidate_ids = [c.id for c in candidates]
        matches = []
        if candidate_ids:
            matches = db.query(CandidateMatch).filter(CandidateMatch.candidate_entity_id.in_(candidate_ids)).all()
        total_matches = len(matches)
        print(f"3. CandidateMatch count: {total_matches}")
        
        # 4. CandidateMatch confidence distribution
        confidences = [m.confidence_level for m in matches]
        conf_dist = Counter(confidences)
        print(f"4. CandidateMatch confidence distribution: {dict(conf_dist)}")
        
        # 5. CandidateMatch counts by candidate/resolved entity
        match_by_cand = Counter([m.candidate_entity_id for m in matches])
        match_by_res = Counter([m.resolved_entity_id for m in matches])
        print(f"5. CandidateMatch distribution:")
        print(f"   Max matches per candidate: {max(match_by_cand.values()) if match_by_cand else 0}")
        print(f"   Candidates with >0 matches: {len(match_by_cand)}")
        print(f"   Max matches per resolved entity: {max(match_by_res.values()) if match_by_res else 0}")
        
        # 6. unresolved/pending candidate count
        pending = sum(1 for c in candidates if c.status == 'pending')
        print(f"6. Unresolved/pending candidate count: {pending}")
        
        # 7. any errors
        errors = sum(1 for c in candidates if c.status == 'error')
        print(f"7. Errors: {errors}")
        
        # 8. whether ResolvedEntity count changed
        total_resolved = db.query(ResolvedEntity).count()
        print(f"8. ResolvedEntity count: {total_resolved}")
        
        # 9. whether ResolvedRelationship count changed
        total_rel = db.query(ResolvedRelationship).count()
        print(f"9. ResolvedRelationship count: {total_rel}")
        
        # 10. whether any automatic confirmation/merge occurred
        confirmed = sum(1 for c in candidates if c.status == 'confirmed')
        print(f"10. Automatic confirmation/merge occurred: {confirmed > 0} (Confirmed: {confirmed})")
        
        # 11. Inspect 10 representative CandidateMatch records
        print("\n11. Representative CandidateMatch records (up to 10):")
        for m in matches[:10]:
            cand = db.query(CandidateEntity).filter(CandidateEntity.id == m.candidate_entity_id).first()
            res = db.query(ResolvedEntity).filter(ResolvedEntity.id == m.resolved_entity_id).first()
            print(f"  --- Match {m.id} ---")
            print(f"  Candidate Text: {cand.text if cand else 'N/A'}")
            print(f"  Candidate Label: {cand.label if cand else 'N/A'}")
            print(f"  Resolved Entity: {res.canonical_name if res else 'N/A'} (Label: {res.canonical_label if res else 'N/A'})")
            print(f"  Match Score: {m.match_score}")
            print(f"  Confidence Level: {m.confidence_level}")
            print(f"  Matching Components: {m.matching_components}")
            print(f"  Candidate Provenance - Mode: {cand.provenance_mode}, Synth: {cand.synthetic_flag}, Audit: {cand.audit_reference}, GenBatch: {cand.generation_batch_id}")

if __name__ == "__main__":
    report("4f25f025-4dd9-40fb-bb0a-8338d3a3c3b8")
