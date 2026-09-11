import csv
import hashlib
import logging
from datetime import datetime, timezone
from pathlib import Path
import uuid
from uuid import UUID

from sqlalchemy.orm import Session

from backend.app.core.postgres import SessionLocal
from backend.app.extraction.models import ExtractionBatch, ExtractionStatus, CandidateEntity, CandidateStatus
from backend.app.extraction.pipeline import ExtractionPipeline

from backend.app.core.config import settings

logger = logging.getLogger(__name__)


def str_to_bool(value: str) -> bool:
    if not value:
        return False
    return value.lower() in ("true", "t", "1", "yes", "y")


def compute_file_fingerprint(file_path: str) -> str:
    """
    Computes a deterministic fingerprint representing the content of the file.
    """
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        # Read and update hash string value in blocks of 4K
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
            
    return sha256_hash.hexdigest()


class ExtractionEngine:
    def __init__(self, batch_id: UUID, db: Session = None):
        self.batch_id = batch_id
        if db is not None:
            self.db = db
            self._owns_db = False
        else:
            self.db = SessionLocal()
            self._owns_db = True
        self.pipeline = ExtractionPipeline()

    def run(self):
        batch = self.db.query(ExtractionBatch).filter(ExtractionBatch.id == self.batch_id).first()
        if not batch:
            logger.error(f"Batch {self.batch_id} not found.")
            return

        batch.status = ExtractionStatus.RUNNING
        self.db.commit()

        documents_path = Path(settings.extraction_documents_path)
        if not documents_path.exists():
            batch.status = ExtractionStatus.FAILED
            batch.completed_at = datetime.now(timezone.utc)
            self.db.commit()
            logger.error(f"Documents file not found at {documents_path}")
            return

        total_docs = 0
        processed_docs = 0
        candidates_extracted = 0
        error_count = 0

        # Read line count (excluding header) for total
        try:
            with open(documents_path, "r", encoding="utf-8") as f:
                total_docs = sum(1 for _ in f) - 1
            batch.total_documents = max(total_docs, 0)
            self.db.commit()
        except Exception as e:
            logger.error(f"Could not count documents: {e}")
            total_docs = 0

        try:
            with open(documents_path, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                
                chunk = []
                chunk_size = 100
                
                for row in reader:
                    processed_docs += 1
                    
                    description = row.get("description", "")
                    
                    if not description.strip():
                        continue
                        
                    try:
                        # Process text
                        spans, relationships = self.pipeline.process(description)
                        
                        # We need to create entities and map their local object IDs to their spans
                        # so we can link CandidateRelationships
                        span_to_entity_id = {}
                        
                        for span in spans:
                            entity = CandidateEntity(
                                id=uuid.uuid4(),
                                batch_id=self.batch_id,
                                canonical_label=span.label,
                                extracted_text=span.text,
                                normalized_payload={
                                    "text": span.text,
                                    "start_char": span.start_char,
                                    "end_char": span.end_char,
                                    "metadata": span.metadata
                                },
                                extraction_method=span.method,
                                confidence_score=span.confidence,
                                status=CandidateStatus.PENDING_RESOLUTION,
                                
                                # Provenance mapping
                                source_document_id=row.get("document_id", ""),
                                generation_batch_id=row.get("generation_batch_id", ""),
                                audit_reference=row.get("audit_reference", ""),
                                synthetic_flag=str_to_bool(row.get("synthetic_flag", "false")),
                                source_dataset=row.get("source_dataset", ""),
                                provenance_mode=row.get("provenance_mode", ""),
                                source_record_reference=row.get("source_record_reference", "")
                            )
                            chunk.append(entity)
                            candidates_extracted += 1
                            span_to_entity_id[id(span)] = entity.id
                            
                        from backend.app.extraction.models import CandidateRelationship
                        for rel in relationships:
                            subj_span = rel["source_span"]
                            obj_span = rel["target_span"]
                            
                            source_candidate_id = span_to_entity_id.get(id(subj_span))
                            target_candidate_id = span_to_entity_id.get(id(obj_span))
                            
                            if source_candidate_id and target_candidate_id:
                                # Handle Bidirectional or Obj->Subj inversion
                                direction = rel["direction"]
                                final_source_id = source_candidate_id
                                final_target_id = target_candidate_id
                                
                                if direction == "OBJ_TO_SUBJ":
                                    final_source_id = target_candidate_id
                                    final_target_id = source_candidate_id
                                
                                rel_obj = CandidateRelationship(
                                    batch_id=self.batch_id,
                                    source_candidate_id=final_source_id,
                                    target_candidate_id=final_target_id,
                                    relationship_type=rel["tracex_relationship"],
                                    confidence_score=rel["confidence"],
                                    evidence_span=rel["evidence_span"],
                                    extraction_method=rel["extraction_method"],
                                    status=CandidateStatus.PENDING_RESOLUTION
                                )
                                chunk.append(rel_obj)
                            
                    except Exception as e:
                        logger.error(f"Error processing row {processed_docs}: {e}")
                        error_count += 1
                        # We must log IngestionErrorLog here if we had that implemented,
                        # but keeping error_count updated handles it gracefully.
                        
                    if len(chunk) >= chunk_size:
                        self.db.add_all(chunk)
                        self.db.commit()
                        chunk = []
                        
                        # Update batch progress periodically
                        batch.processed_documents = processed_docs
                        batch.candidates_extracted = candidates_extracted
                        batch.error_count = error_count
                        self.db.commit()

                # Save remaining
                if chunk:
                    self.db.add_all(chunk)
                    
                batch.processed_documents = processed_docs
                batch.candidates_extracted = candidates_extracted
                batch.error_count = error_count
                batch.status = ExtractionStatus.COMPLETED
                batch.completed_at = datetime.now(timezone.utc)
                self.db.commit()
                
        except Exception as e:
            batch.status = ExtractionStatus.FAILED
            batch.completed_at = datetime.now(timezone.utc)
            self.db.commit()
            logger.exception(f"Extraction failed: {e}")
        finally:
            if self._owns_db:
                self.db.close()
