import sys
import os
import json

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.app.core.postgres import SessionLocal
from backend.app.ingestion.models import CanonicalNodeRecord, CanonicalRelationshipRecord

CASES = [
    "CASE-01591", "CASE-00394", "CASE-01744", "CASE-00184", "CASE-00529",
    "CASE-00959", "CASE-01084", "CASE-01664", "CASE-00564", "CASE-01209",
    "CASE-01334", "CASE-01594", "CASE-00349", "CASE-01269", "CASE-01994",
    "CASE-00139", "CASE-01519", "CASE-01124", "CASE-01059", "CASE-01584",
]

def analyze():
    with SessionLocal() as db:
        nodes = db.query(CanonicalNodeRecord).filter(
            CanonicalNodeRecord.canonical_label == 'Document'
        ).limit(10).all()
        print("Existing Canonical Document Payloads:")
        for n in nodes:
            print(json.dumps(n.payload, indent=2))
            
        print("\nChecking relationships around Cases...")
        rels = db.query(CanonicalRelationshipRecord).filter(
            CanonicalRelationshipRecord.target_id.in_(CASES),
            CanonicalRelationshipRecord.canonical_label == 'HAS_DOCUMENT'
        ).limit(5).all()
        for r in rels:
            print(f"{r.source_id} -[{r.relationship_type}]-> {r.target_id}")

if __name__ == "__main__":
    analyze()
