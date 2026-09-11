import sys
import os
import argparse
import uuid
from datetime import datetime, timezone
from pathlib import Path

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.app.core.postgres import SessionLocal
from backend.app.ingestion.engine import PipelineEngine, compute_file_fingerprint
from backend.app.ingestion.models import IngestionBatch, IngestionStatus, CanonicalNodeRecord, CanonicalRelationshipRecord

def get_canonical_id(record_dict: dict) -> str:
    """Extracts the specific source ID and maps it to canonical graph 'id'."""
    id_fields = [
        "id", "person_id", "phone_id", "account_id", "location_id",
        "organization_id", "vehicle_id", "device_id", "document_id",
        "case_id", "transaction_id", "communication_id",
        "network_event_id", "physical_event_id", "incident_id", "context_id"
    ]
    for f in id_fields:
        if f in record_dict and record_dict[f] is not None:
            return str(record_dict[f])
    return record_dict.get("Audit_Reference", "UNKNOWN_ID")

def run_ingestion(source_dir: str):
    """
    Standalone ingestion executor.
    Runs strictly separate from the FastAPI server to bound memory correctly.
    Now writes canonically directly to PostgreSQL (M3 complete).
    """
    source_path = Path(source_dir)
    if not source_path.exists() or not source_path.is_dir():
        print(f"Error: Directory {source_dir} not found.")
        sys.exit(1)

    print(f"Starting ingestion from {source_dir}...")
    
    csv_files = list(source_path.glob("*.csv"))
    if not csv_files:
        print(f"No CSV files found in {source_dir}.")
        return

    with SessionLocal() as db:
        engine = PipelineEngine(db)
        
        for file_path in csv_files:
            print(f"Processing {file_path.name}...")
            
            # The engine process_file returns a generator yielding Canonical objects.
            record_generator = engine.process_file(str(file_path))
            
            # If the generator is None, it means the concurrency idempotency guard kicked in
            if record_generator is None:
                print(f"[{file_path.name}] Skipped: Already processing or completed (fingerprint match).")
                continue
                
            count = 0
            node_mappings = []
            edge_mappings = []
            batch_id = None
            
            for canonical_record in record_generator:
                if batch_id is None:
                    # Fetch the running batch for foreign keys
                    # We must do this after the generator has started yielding, 
                    # because it creates and commits the batch on its first iteration.
                    fingerprint = compute_file_fingerprint(str(file_path))
                    batch = db.query(IngestionBatch).filter_by(file_fingerprint=fingerprint, status=IngestionStatus.RUNNING).first()
                    if not batch:
                        print(f"[{file_path.name}] Error: Could not find active batch.")
                        break
                    batch_id = batch.id

                record_dict = canonical_record.model_dump(mode="json")
                now = datetime.now(timezone.utc)
                
                if hasattr(canonical_record, "relationship_type"):
                    rel_type = record_dict.pop("relationship_type")
                    source_id = record_dict.pop("source_id")
                    target_id = record_dict.pop("target_id")
                    
                    edge_mappings.append({
                        "id": uuid.uuid4(),
                        "batch_id": batch_id,
                        "source_id": str(source_id),
                        "target_id": str(target_id),
                        "relationship_type": rel_type,
                        "payload": record_dict,
                        "audit_reference": record_dict.get("Audit_Reference", "UNKNOWN_ID"),
                        "created_at": now
                    })
                else:
                    label = record_dict.pop("canonical_label")
                    event_type = record_dict.pop("event_type", None)
                    canonical_id = get_canonical_id(record_dict)
                    
                    # Store ID uniformly within payload too
                    record_dict["id"] = canonical_id
                        
                    node_mappings.append({
                        "id": uuid.uuid4(),
                        "batch_id": batch_id,
                        "canonical_id": canonical_id,
                        "canonical_label": label,
                        "event_type": event_type,
                        "payload": record_dict,
                        "audit_reference": record_dict.get("Audit_Reference", "UNKNOWN_ID"),
                        "created_at": now
                    })
                    
                count += 1
                
                # Bulk insert in chunks of 5000
                if len(node_mappings) >= 5000:
                    db.bulk_insert_mappings(CanonicalNodeRecord, node_mappings)
                    node_mappings = []
                if len(edge_mappings) >= 5000:
                    db.bulk_insert_mappings(CanonicalRelationshipRecord, edge_mappings)
                    edge_mappings = []
                    
            # Insert any remaining records
            if node_mappings:
                db.bulk_insert_mappings(CanonicalNodeRecord, node_mappings)
            if edge_mappings:
                db.bulk_insert_mappings(CanonicalRelationshipRecord, edge_mappings)
                
            print(f"[{file_path.name}] Successfully produced and persisted {count} canonical records to PostgreSQL.")
            
            from backend.app.audit.service import AuditService
            from backend.app.audit.models import ActionCategory
            AuditService.log_action(
                db=db,
                action_category=ActionCategory.INGESTION,
                action_detail=f"Ingested file {file_path.name}",
                action_metadata={"file_name": file_path.name, "record_count": count}
            )
            db.commit()

    print("Ingestion execution complete.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="TraceX Structured Ingestion CLI")
    parser.add_argument("--source", default="../TRACEX_PREPARED", help="Path to TRACEX_PREPARED dataset")
    args = parser.parse_args()
    
    run_ingestion(args.source)
