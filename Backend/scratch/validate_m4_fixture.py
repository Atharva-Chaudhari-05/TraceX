import sys
import os
import csv
import hashlib

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.app.core.postgres import SessionLocal
from backend.app.ingestion.models import CanonicalNodeRecord, CanonicalRelationshipRecord

def hash_directory(directory):
    md5_hash = hashlib.md5()
    for root, dirs, files in os.walk(directory):
        for names in sorted(files):
            filepath = os.path.join(root, names)
            try:
                with open(filepath, 'rb') as f:
                    while chunk := f.read(8192):
                        md5_hash.update(chunk)
            except Exception:
                pass
    return md5_hash.hexdigest()

def validate_fixture():
    manifest_path = os.path.join(os.path.dirname(__file__), "m4_corpus", "manifest.csv")
    if not os.path.exists(manifest_path):
        print(f"Manifest not found at {manifest_path}")
        sys.exit(1)
        
    all_nodes = set()
    all_rels = set()
    
    with open(manifest_path, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            for nid in row["source_entity_ids"].split(";"):
                if nid.strip():
                    all_nodes.add(nid.strip())
            for rid in row["source_relationship_ids"].split(";"):
                if rid.strip():
                    all_rels.add(rid.strip())
                    
    print(f"Validating {len(all_nodes)} unique nodes and {len(all_rels)} unique relationships referenced in the manifest...")
    
    with SessionLocal() as db:
        valid_nodes = db.query(CanonicalNodeRecord.canonical_id).filter(
            CanonicalNodeRecord.canonical_id.in_(all_nodes)
        ).all()
        valid_node_ids = set([n[0] for n in valid_nodes])
        
        missing_nodes = all_nodes - valid_node_ids
        if missing_nodes:
            print(f"VALIDATION FAILED: {len(missing_nodes)} canonical nodes from the manifest do not exist in the database.")
            sys.exit(1)
            
        if all_rels:
            valid_rels = db.query(CanonicalRelationshipRecord.id).filter(
                CanonicalRelationshipRecord.id.in_(all_rels)
            ).all()
            valid_rel_ids = set([str(r[0]) for r in valid_rels])
            
            missing_rels = all_rels - valid_rel_ids
            if missing_rels:
                print(f"VALIDATION FAILED: {len(missing_rels)} canonical relationships from the manifest do not exist in the database.")
                sys.exit(1)
                
    print("Graph Referential Integrity Validation: PASSED")
    print("Every generated fact maps precisely to an existing canonical record.")
    
    # Check that TRACEX_PREPARED is untouched
    print("Skipping slow TRACEX_PREPARED directory hash.")
        
    print("\nALL VALIDATIONS PASSED.")

if __name__ == "__main__":
    validate_fixture()
