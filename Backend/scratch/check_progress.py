import sys
import os
from sqlalchemy import text

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from backend.app.core.postgres import SessionLocal

with SessionLocal() as db:
    statuses = db.execute(text("SELECT status, COUNT(*) FROM candidate_entities WHERE batch_id = '4f25f025-4dd9-40fb-bb0a-8338d3a3c3b8' GROUP BY status")).fetchall()
    print("Candidate statuses:")
    for s in statuses:
        print(f"  {s[0]}: {s[1]}")
    matches = db.execute(text("SELECT COUNT(*) FROM candidate_matches")).scalar()
    print(f"Total candidate matches: {matches}")
    print(f"Total candidate matches: {matches}")
