import hashlib
import json
import os
import uuid
import time
from typing import Iterator, Dict, Any, Type
import pandas as pd
from pydantic import ValidationError
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from sqlalchemy import select

from backend.app.core.postgres import engine as db_engine
from backend.app.ingestion.models import IngestionBatch, IngestionErrorLog, IngestionStatus
from backend.app.ingestion.schemas import (
    CanonicalNode,
    CanonicalRelationship,
    Person,
    Phone,
    Account,
    Location,
    Organisation,
    Vehicle,
    Device,
    Document,
    Case,
    Transaction,
    CommunicationEvent,
    NetworkEvent,
    PhysicalAccessEvent,
    Incident,
    CrimeStatistic
)


SCHEMA_MAPPING_PATH = os.path.join(os.path.dirname(__file__), "schema_mapping.json")

def get_schema_mapping_hash() -> str:
    with open(SCHEMA_MAPPING_PATH, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()

def compute_file_fingerprint(file_path: str) -> str:
    """
    Computes a deterministic fingerprint representing the exact intent of ingestion:
    SHA256(file_bytes + schema_mapping_hash)
    """
    schema_hash = get_schema_mapping_hash()
    
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        # Read and update hash string value in blocks of 4K
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
            
    sha256_hash.update(schema_hash.encode('utf-8'))
    return sha256_hash.hexdigest()


class PipelineEngine:
    def __init__(self, db: Session):
        self.db = db
        self.max_error_logs = 100
        
        # In a real dynamic system, this mapping would be more sophisticated based on schema_mapping.json
        # For M3, we statically map the file basenames to their designated Pydantic models.
        self.file_to_model: Dict[str, Type[CanonicalNode]] = {
            "persons.csv": Person,
            "phones.csv": Phone,
            "accounts.csv": Account,
            "locations.csv": Location,
            "organizations.csv": Organisation, # spelling aligned with schema_mapping
            "vehicles.csv": Vehicle,
            "devices.csv": Device,
            "documents.csv": Document,
            "cases.csv": Case,
            "transactions.csv": Transaction,
            "communication_events.csv": CommunicationEvent,
            "network_events.csv": NetworkEvent,
            "physical_access_events.csv": PhysicalAccessEvent,
            "incidents.csv": Incident,
            "crime_context.csv": CrimeStatistic,
        }

    def process_file(self, file_path: str) -> Iterator[CanonicalNode | CanonicalRelationship]:
        """
        Processes a CSV file in bounded chunks, validating rows and yielding canonical records.
        Implements strict database-level concurrency and idempotency.
        """
        fingerprint = compute_file_fingerprint(file_path)
        file_name = os.path.basename(file_path)
        
        # 1. Database-Level Idempotency Guard
        batch = IngestionBatch(
            file_fingerprint=fingerprint,
            file_name=file_name,
            status=IngestionStatus.RUNNING
        )
        self.db.add(batch)
        try:
            self.db.commit()
            self.db.refresh(batch)
        except IntegrityError:
            self.db.rollback()
            # If IntegrityError, another batch with the same fingerprint is either RUNNING or COMPLETED.
            # Safe duplicate/already-processing result.
            return

        # Setup model map
        target_model = self.file_to_model.get(file_name)
        if not target_model and file_name != "relationships.csv":
            self._fail_batch(batch, "Unknown file format / model mapping.")
            return

        is_relationship = file_name == "relationships.csv"
        
        try:
            # 2. Chunk-based memory-bounded processing
            chunk_iterator = pd.read_csv(file_path, chunksize=10000, dtype=str)
            
            for chunk in chunk_iterator:
                # Replace NaNs with None for Pydantic
                chunk = chunk.where(pd.notnull(chunk), None)
                records = chunk.to_dict(orient="records")
                
                batch.total_rows += len(records)
                
                for record in records:
                    batch.processed_rows += 1
                    try:
                        # 3. Provenance and Schema Validation
                        # M1 specifies how to map these safely.
                        mapped_record = self._apply_provenance_mapping(record, file_name)
                        
                        if is_relationship:
                            canonical_record = CanonicalRelationship(**mapped_record)
                            batch.valid_records += 1
                            yield canonical_record
                        else:
                            canonical_record = target_model(**mapped_record)
                            batch.valid_records += 1
                            yield canonical_record
                            
                            source_node_id = None
                            for id_field in ["communication_id", "transaction_id", "incident_id", "network_event_id", "physical_event_id", "person_id"]:
                                if id_field in mapped_record and mapped_record[id_field] is not None:
                                    source_node_id = mapped_record[id_field]
                                    break
                                    
                            if source_node_id:
                                fk_mappings = {
                                    "source_phone_id": "PARTICIPATED_IN",
                                    "target_phone_id": "PARTICIPATED_IN",
                                    "sender_account_id": "PARTICIPATED_IN",
                                    "receiver_account_id": "PARTICIPATED_IN",
                                    "person_id": "INVOLVED_IN",
                                    "location_id": "LOCATED_AT",
                                    "organization_id": "WORKS_FOR",
                                    "source_device_id": "PARTICIPATED_IN",
                                    "destination_device_id": "PARTICIPATED_IN"
                                }
                                for fk, rel_type in fk_mappings.items():
                                    if fk in mapped_record and mapped_record[fk] and fk != id_field:
                                        rel_payload = {
                                            "Synthetic_Flag": mapped_record.get("Synthetic_Flag", True),
                                            "Audit_Reference": mapped_record.get("Audit_Reference", "UNKNOWN"),
                                            "Provenance_Mode": "implicit_derived",
                                            "relationship_type": rel_type,
                                            "timestamp": mapped_record.get("timestamp"),
                                        }
                                        
                                        if rel_type == "WORKS_FOR" or rel_type == "LOCATED_AT":
                                            rel_payload["source_id"] = source_node_id
                                            rel_payload["target_id"] = mapped_record[fk]
                                        elif rel_type == "INVOLVED_IN" or rel_type == "PARTICIPATED_IN":
                                            rel_payload["source_id"] = mapped_record[fk]
                                            rel_payload["target_id"] = source_node_id
                                            
                                        yield CanonicalRelationship(**rel_payload)
                        
                    except ValidationError as e:
                        self._log_row_error(batch, record, str(e))
                    except Exception as e:
                        self._log_row_error(batch, record, f"Unexpected error: {str(e)}")

            # Successfully completed
            self._complete_batch(batch)
            
        except Exception as e:
            self._fail_batch(batch, str(e))

    def _apply_provenance_mapping(self, record: dict, file_name: str = "") -> dict:
        """
        Normalizes provenance and applies strict mappings without inventing data.
        """
        import pandas as pd
        for k, v in list(record.items()):
            # Handle float nan, string "nan", pd.NaT, and empty strings.
            # Empty strings must become None so Optional[datetime] fields
            # (e.g. `timestamp` in relationships.csv) pass Pydantic validation.
            if v is None:
                continue
            if isinstance(v, float) and pd.isna(v):
                record[k] = None
            elif isinstance(v, str) and v.strip().lower() == "nan":
                record[k] = None
            elif isinstance(v, str) and v.strip() == "":
                record[k] = None
            elif hasattr(v, '__class__') and not isinstance(v, (str, float, int, bool)) and pd.isna(v):
                record[k] = None
                
        # M1 Remediation Spec maps scenario_id to Generation_Batch_ID
        if "scenario_id" in record:
            record["Generation_Batch_ID"] = record.pop("scenario_id")

        # Normalize snake_case TRACEX_DATA provenance fields to canonical PascalCase
        # so that both prepared_real_sample (already canonical) and TRACEX_DATA work
        if "synthetic_flag" in record and "Synthetic_Flag" not in record:
            record["Synthetic_Flag"] = record.pop("synthetic_flag")
        if "source_dataset" in record and "Source_Dataset" not in record:
            record["Source_Dataset"] = record.pop("source_dataset")
        if "source_record_reference" in record and "source_record_reference" in record:
            # keep lowercase — schema accepts it
            pass
        if "data_origin" in record and "Provenance_Mode" not in record:
            record["Provenance_Mode"] = record.pop("data_origin") or "direct"
        if "relationship_origin" in record and "Provenance_Mode" not in record:
            record["Provenance_Mode"] = record.pop("relationship_origin") or "direct"

        # Auto-generate Audit_Reference if absent (required canonical field)
        if "Audit_Reference" not in record or not record.get("Audit_Reference"):
            # Build deterministic reference from available ID fields
            for id_fld in ["relationship_id", "case_id", "person_id", "account_id", "phone_id", "device_id",
                            "location_id", "organization_id", "vehicle_id", "document_id",
                            "transaction_id", "communication_id", "network_event_id",
                            "physical_event_id", "incident_id", "context_id"]:
                if record.get(id_fld):
                    stem = file_name.replace(".csv", "")
                    record["Audit_Reference"] = f"AUDIT-{stem}-{record[id_fld]}"
                    break

        # Ensure Provenance_Mode has a value
        if not record.get("Provenance_Mode"):
            record["Provenance_Mode"] = "direct"

        # Ensure Synthetic_Flag is properly typed
        if "Synthetic_Flag" in record and record["Synthetic_Flag"] is not None:
            flag = str(record["Synthetic_Flag"]).lower()
            record["Synthetic_Flag"] = True if flag in ["true", "1", "t", "yes"] else False
            
        if "source_entity_id" in record:
            record["source_id"] = record.pop("source_entity_id")
            
        if "target_entity_id" in record:
            record["target_id"] = record.pop("target_entity_id")
            
        if "event_type" in record:
            if file_name == "physical_access_events.csv":
                record["event_type"] = "PhysicalAccessEvent"
            elif file_name == "communication_events.csv":
                record["event_type"] = "CommunicationEvent"
            elif file_name == "network_events.csv":
                record["event_type"] = "NetworkEvent"
                
        return record

    def _log_row_error(self, batch: IngestionBatch, record: dict, message: str):
        batch.error_count += 1
        
        # Bounded error logging
        if batch.error_count <= self.max_error_logs:
            error_log = IngestionErrorLog(
                batch_id=batch.id,
                row_index=batch.processed_rows,
                error_message=message,
                raw_data=json.dumps(record, default=str)
            )
            self.db.add(error_log)
        
        # Commit periodically or at the end to save overhead.
        # We'll rely on the final commit, but we can flush to ensure it's written.
        
    def _complete_batch(self, batch: IngestionBatch):
        import time
        from datetime import datetime, timezone
        batch.status = IngestionStatus.COMPLETED
        batch.completed_at = datetime.now(timezone.utc)
        self.db.commit()

    def _fail_batch(self, batch: IngestionBatch, error_message: str):
        import time
        from datetime import datetime, timezone
        batch.status = IngestionStatus.FAILED
        batch.completed_at = datetime.now(timezone.utc)
        # Log the critical failure
        if batch.error_count <= self.max_error_logs:
            self.db.add(IngestionErrorLog(
                batch_id=batch.id,
                error_message=f"CRITICAL PIPELINE FAILURE: {error_message}"
            ))
        self.db.commit()
