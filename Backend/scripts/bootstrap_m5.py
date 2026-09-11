import sys
import os
import argparse
from typing import List

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.app.core.postgres import SessionLocal
from backend.app.ingestion.models import CanonicalNodeRecord
from backend.app.resolution.models import ResolvedEntity
from scripts.run_demo_projection import build_case_subgraph, DEFAULT_CASES, load_nodes

CANONICAL_LABELS = {
    "Person", "Phone", "Account", "Location", "Organisation",
    "Vehicle", "Device", "Document", "Event", "Case"
}

def get_canonical_name(label: str, payload: dict) -> str:
    """Extract authoritative identifying value from payload based on label."""
    if label == "Person":
        return payload.get("name", "UNKNOWN_PERSON")
    elif label == "Phone":
        return payload.get("phone_number", "UNKNOWN_PHONE")
    elif label == "Account":
        return payload.get("account_id", "UNKNOWN_ACCOUNT")
    elif label == "Location":
        return payload.get("location_id", "UNKNOWN_LOCATION")
    elif label == "Organisation":
        return payload.get("name", "UNKNOWN_ORGANISATION")
    elif label == "Vehicle":
        return payload.get("vehicle_id", "UNKNOWN_VEHICLE")
    elif label == "Device":
        return payload.get("device_id", "UNKNOWN_DEVICE")
    elif label == "Document":
        return payload.get("title", payload.get("document_id", "UNKNOWN_DOCUMENT"))
    elif label == "Event":
        # Event might just be identified by its ID or timestamp
        ev_type = payload.get("event_type", "Event")
        return f"{ev_type}_{payload.get('id', payload.get('timestamp', 'UNKNOWN'))}"
    elif label == "Case":
        return payload.get("case_name", payload.get("case_id", "UNKNOWN_CASE"))
    
    return payload.get("id", "UNKNOWN")

def run_bootstrap(case_ids: List[str], dry_run: bool = False, db_session=None):
    print("=" * 70)
    print("TraceX Bounded M5 Bootstrap")
    print("=" * 70)
    print(f"Cases selected: {len(case_ids)}")
    print(f"Dry Run: {dry_run}")
    
    db_ctx = db_session if db_session else SessionLocal()
    try:
        db = db_ctx
        # Get existing resolved entities to ensure idempotency
        existing_refs = set(
            row[0] for row in db.query(ResolvedEntity.audit_reference)
            .filter(ResolvedEntity.audit_reference.isnot(None))
            .all()
        )
        
        # We also want to track by name+label if audit_reference is missing
        existing_names = set(
            (row[0], row[1]) for row in db.query(ResolvedEntity.canonical_name, ResolvedEntity.canonical_label).all()
        )
        
        # Find bounded nodes
        node_ids, _ = build_case_subgraph(db, case_ids)
        canonical_nodes = load_nodes(db, node_ids)
        
        print(f"\nCanonical nodes selected: {len(canonical_nodes)}")
        
        counts_by_label = {}
        records_to_insert = []
        skipped_records = []
        skip_reasons = {}
        provenance_fields_found = {"synthetic_flag": 0, "source_dataset": 0, "provenance_mode": 0, "source_record_reference": 0, "generation_batch_id": 0, "audit_reference": 0}
        identifiers_found = 0
        examples_by_label = {}
        
        for node in canonical_nodes:
            label = node.canonical_label
            counts_by_label[label] = counts_by_label.get(label, 0) + 1
            
            if label not in CANONICAL_LABELS:
                reason = f"Non-canonical label: {label}"
                skipped_records.append((node.id, reason))
                skip_reasons[reason] = skip_reasons.get(reason, 0) + 1
                continue
                
            payload = node.payload
            
            # Extract identifiers
            canonical_name = get_canonical_name(label, payload)
            if not canonical_name.startswith("UNKNOWN"):
                identifiers_found += 1
            
            if label not in examples_by_label:
                examples_by_label[label] = canonical_name
                
            audit_ref = node.audit_reference or payload.get("Audit_Reference")
            
            # Idempotency check
            if audit_ref and audit_ref in existing_refs:
                reason = "Idempotency conflict (audit_reference exists)"
                skipped_records.append((node.id, reason))
                skip_reasons[reason] = skip_reasons.get(reason, 0) + 1
                continue
                
            if (canonical_name, label) in existing_names:
                reason = "Idempotency conflict (name+label exists)"
                skipped_records.append((node.id, reason))
                skip_reasons[reason] = skip_reasons.get(reason, 0) + 1
                continue
            
            # Extract Provenance exactly from payload where possible
            synthetic_flag = payload.get("Synthetic_Flag")
            if synthetic_flag is not None: provenance_fields_found["synthetic_flag"] += 1
                
            source_dataset = payload.get("Source_Dataset")
            if source_dataset is not None: provenance_fields_found["source_dataset"] += 1
                
            provenance_mode = payload.get("Provenance_Mode")
            if provenance_mode is not None: provenance_fields_found["provenance_mode"] += 1
                
            source_record_reference = payload.get("source_record_reference")
            if source_record_reference is not None: provenance_fields_found["source_record_reference"] += 1
                
            generation_batch_id = payload.get("Generation_Batch_ID")
            if generation_batch_id is not None: provenance_fields_found["generation_batch_id"] += 1
                
            if audit_ref is not None: provenance_fields_found["audit_reference"] += 1

            # Prepare to insert
            resolved = ResolvedEntity(
                canonical_name=str(canonical_name)[:255],
                canonical_label=str(label)[:255],
                synthetic_flag=bool(synthetic_flag) if synthetic_flag is not None else None,
                source_dataset=str(source_dataset)[:255] if source_dataset else None,
                provenance_mode=str(provenance_mode)[:255] if provenance_mode else None,
                source_record_reference=str(source_record_reference) if source_record_reference else None,
                generation_batch_id=str(generation_batch_id)[:255] if generation_batch_id else None,
                audit_reference=str(audit_ref)[:255] if audit_ref else None
            )
            records_to_insert.append(resolved)
            
            # Keep tracking memory sets to prevent intra-batch dupes
            if audit_ref:
                existing_refs.add(audit_ref)
            existing_names.add((canonical_name, label))

        print("\n--- Dry Run Statistics ---")
        print(f"Total canonical nodes matched to cases: {len(canonical_nodes)}")
        print("Counts by canonical_label:")
        for lbl, count in sorted(counts_by_label.items()):
            print(f"  {lbl}: {count}")
            
        print(f"\nRecords skipped: {len(skipped_records)}")
        for reason, count in skip_reasons.items():
            print(f"  {reason}: {count}")
            
        print(f"\nRecords proposed for insertion: {len(records_to_insert)}")
        
        if records_to_insert:
            print("\nIdentifier completeness:")
            pct_id = (identifiers_found / len(canonical_nodes)) * 100
            print(f"  Populated identifiers: {identifiers_found}/{len(canonical_nodes)} ({pct_id:.1f}%)")
            
            print("\nIdentifier examples by label:")
            for lbl, ex in sorted(examples_by_label.items()):
                print(f"  {lbl}: {ex}")
                
            print("\nProvenance completeness (of proposed records):")
            for field, count in provenance_fields_found.items():
                pct = (count / len(records_to_insert)) * 100
                print(f"  {field}: {count} ({pct:.1f}%)")
        
        if not dry_run and records_to_insert:
            print("\nExecuting insertion...")
            # Chunking to avoid memory issues
            CHUNK_SIZE = 5000
            inserted_count = 0
            for i in range(0, len(records_to_insert), CHUNK_SIZE):
                chunk = records_to_insert[i:i + CHUNK_SIZE]
                db.add_all(chunk)
                db.commit()
                inserted_count += len(chunk)
                print(f"Inserted {inserted_count} records...")
            print("Insertion complete.")
        elif dry_run:
            print("DRY RUN: Zero writes performed.")
    finally:
        if not db_session:
            db.close()
            
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Bootstrap M5 ResolvedEntity from M3 Canonical Nodes")
    parser.add_argument("--cases", nargs="+", default=DEFAULT_CASES, help="Case IDs to project")
    parser.add_argument("--dry-run", action="store_true", help="Perform a dry run without modifying the database")
    
    args = parser.parse_args()
    run_bootstrap(args.cases, dry_run=args.dry_run)
