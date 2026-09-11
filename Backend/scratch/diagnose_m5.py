import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.app.core.postgres import SessionLocal
from backend.app.resolution.models import ResolvedEntity
from backend.app.ingestion.models import CanonicalNodeRecord
from scripts.run_demo_projection import build_case_subgraph, load_nodes, DEFAULT_CASES
from sqlalchemy import text

def run_diagnosis():
    print("=" * 70)
    print("M5 Bootstrap Diagnosis")
    print("=" * 70)
    
    with SessionLocal() as db:
        print("\n--- A. ResolvedEntity Counts & Provenance ---")
        total = db.execute(text("SELECT COUNT(*) FROM resolved_entities")).scalar()
        print(f"Total ResolvedEntity rows: {total}")
        
        if total > 0:
            print("\nCounts by canonical_label:")
            labels = db.execute(text("SELECT canonical_label, COUNT(*) FROM resolved_entities GROUP BY canonical_label")).fetchall()
            for row in labels: print(f"  {row[0]}: {row[1]}")
                
            print("\nCounts by generation_batch_id:")
            batches = db.execute(text("SELECT generation_batch_id, COUNT(*) FROM resolved_entities GROUP BY generation_batch_id")).fetchall()
            for row in batches: print(f"  {row[0]}: {row[1]}")
                
            print("\nCounts by provenance_mode:")
            modes = db.execute(text("SELECT provenance_mode, COUNT(*) FROM resolved_entities GROUP BY provenance_mode")).fetchall()
            for row in modes: print(f"  {row[0]}: {row[1]}")

            print("\nProvenance nullity (existing ResolvedEntity):")
            nulls = db.execute(text("""
                SELECT 
                    SUM(CASE WHEN source_dataset IS NULL THEN 1 ELSE 0 END) as sd_null
                FROM resolved_entities
            """)).fetchone()
            print(f"  source_dataset NULL: {nulls[0]}")
            print(f"  source_record_reference NULL: (COLUMN NOT IN DB)")
            
        print("\n--- B. Payload Provenance Keys Analysis ---")
        node_ids, _ = build_case_subgraph(db, DEFAULT_CASES)
        nodes = load_nodes(db, node_ids)
        
        sampled_labels = set()
        print("\nSample payloads:")
        
        missing_gb_sample = None
        
        for node in nodes:
            lbl = node.canonical_label
            # Find missing generation_batch_id
            payload = node.payload
            
            gb = payload.get("Generation_Batch_ID") or payload.get("generation_batch_id")
            if gb is None and missing_gb_sample is None:
                missing_gb_sample = (lbl, payload)
                
            if lbl not in sampled_labels and lbl in {"Person", "Organisation", "Account", "Event", "Case"}:
                sampled_labels.add(lbl)
                print(f"\n[{lbl}] Payload keys:")
                prov_keys = {k: v for k, v in payload.items() if "source" in k.lower() or "batch" in k.lower() or "prov" in k.lower() or "synth" in k.lower() or "audit" in k.lower()}
                for k, v in prov_keys.items():
                    print(f"  {k}: {str(v)[:50]}")
                    
        print(f"\nMissing Generation_Batch_ID example:")
        if missing_gb_sample:
            print(f"  Label: {missing_gb_sample[0]}")
            for k, v in missing_gb_sample[1].items():
                if "batch" in k.lower() or "gen" in k.lower():
                    print(f"  {k}: {str(v)[:50]}")
        else:
            print("  None found.")

if __name__ == "__main__":
    run_diagnosis()
