from sqlalchemy import func
from backend.app.core.postgres import SessionLocal
from backend.app.extraction.models import CandidateEntity
from backend.app.resolution.models import CandidateMatch, ResolvedEntity, ResolvedRelationship

CASES = [
    "CASE-01591", "CASE-00394", "CASE-01744", "CASE-00184",
    "CASE-00529", "CASE-00959", "CASE-01084", "CASE-01664",
    "CASE-00564", "CASE-01209", "CASE-01334", "CASE-01594",
    "CASE-00349", "CASE-01269", "CASE-01994", "CASE-00139",
    "CASE-01519", "CASE-01124", "CASE-01059", "CASE-01584",
]

db = SessionLocal()

print("========================================")
print("M5 - 20 CASE MANUAL VERIFICATION")
print("========================================")

# --------------------------------------------------
# 1. Global M5 state
# --------------------------------------------------

candidate_count = db.query(CandidateEntity).count()
match_count = db.query(CandidateMatch).count()
resolved_count = db.query(ResolvedEntity).count()
resolved_rel_count = db.query(ResolvedRelationship).count()

print("\nGlobal counts:")
print(f"  CandidateEntity       : {candidate_count}")
print(f"  CandidateMatch        : {match_count}")
print(f"  ResolvedEntity        : {resolved_count}")
print(f"  ResolvedRelationship  : {resolved_rel_count}")

# --------------------------------------------------
# 2. Candidate status
# --------------------------------------------------

print("\nCandidate status distribution:")

status_rows = (
    db.query(CandidateEntity.status, func.count(CandidateEntity.id))
    .group_by(CandidateEntity.status)
    .all()
)

for status, count in status_rows:
    print(f"  {status.value}: {count}")

# --------------------------------------------------
# 3. M4 batch preservation
# --------------------------------------------------

print("\nM4 generation batches:")

batch_rows = (
    db.query(CandidateEntity.batch_id, func.count(CandidateEntity.id))
    .group_by(CandidateEntity.batch_id)
    .all()
)

for batch_id, count in batch_rows:
    print(f"  {batch_id}: {count}")

# --------------------------------------------------
# 4. Verify all 20 cases exist in M5 ResolvedEntity
# --------------------------------------------------

print("\n20-case ResolvedEntity coverage:")

resolved_cases = (
    db.query(ResolvedEntity.canonical_name)
    .filter(
        ResolvedEntity.canonical_label == "Case",
        ResolvedEntity.canonical_name.in_(CASES),
    )
    .all()
)

resolved_case_names = {row[0] for row in resolved_cases}

case_pass = 0

for case_id in CASES:
    if case_id in resolved_case_names:
        print(f"  {case_id}: PASS")
        case_pass += 1
    else:
        print(f"  {case_id}: FAIL")

# --------------------------------------------------
# 5. CandidateMatch confidence distribution
# --------------------------------------------------

print("\nCandidateMatch confidence distribution:")

confidence_rows = (
    db.query(
        CandidateMatch.confidence_level,
        func.count(CandidateMatch.id),
    )
    .group_by(CandidateMatch.confidence_level)
    .all()
)

for confidence, count in confidence_rows:
    print(f"  {confidence}: {count}")

# --------------------------------------------------
# 6. CandidateMatch decision distribution
# --------------------------------------------------

print("\nCandidateMatch decision distribution:")

decision_rows = (
    db.query(
        CandidateMatch.decision,
        func.count(CandidateMatch.id),
    )
    .group_by(CandidateMatch.decision)
    .all()
)

for decision, count in decision_rows:
    print(f"  {decision}: {count}")

# --------------------------------------------------
# 7. M5 safety checks
# --------------------------------------------------

print("\nM5 safety checks:")

print(
    f"  ResolvedEntity baseline preserved: "
    f"{'PASS' if resolved_count == 2262 else 'CHECK'}"
)

print(
    f"  No ResolvedRelationship auto-created: "
    f"{'PASS' if resolved_rel_count == 0 else 'CHECK'}"
)

print(
    f"  All 20 Case entities resolved: "
    f"{'PASS' if case_pass == 20 else 'CHECK'}"
)

print("\n========================================")
print(f"20-CASE COVERAGE: {case_pass}/20")
print("========================================")

db.close()

if (
    case_pass == 20
    and resolved_count == 2262
    and resolved_rel_count == 0
):
    print("M5 20-CASE VERIFICATION: PASS")
else:
    print("M5 20-CASE VERIFICATION: CHECK REQUIRED")
