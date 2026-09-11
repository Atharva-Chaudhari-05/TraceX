import sys
import os
import csv
import json
import uuid

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.app.core.postgres import SessionLocal
from backend.app.extraction.models import ExtractionBatch, ExtractionStatus, CandidateEntity, CandidateRelationship, CandidateStatus
from backend.app.resolution.models import ResolvedEntity, CandidateMatch, ResolvedRelationship
from backend.app.extraction.engine import ExtractionEngine, compute_file_fingerprint
from backend.app.resolution.engine import ResolutionEngine
from backend.app.core.config import settings
from sqlalchemy import func

def run():
    out_dir = os.path.dirname(os.path.abspath(__file__))
    corpus_dir = os.path.join(out_dir, "m4_corpus")
    jsonl_path = os.path.join(corpus_dir, "documents.jsonl")
    csv_path = os.path.join(corpus_dir, "adapted_documents.csv")
    
    docs = []
    with open(jsonl_path, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                docs.append(json.loads(line))
                
    with open(csv_path, "w", newline='', encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["description", "document_id", "generation_batch_id", "synthetic_flag", "source_dataset", "provenance_mode", "source_record_reference", "audit_reference"])
        for d in docs:
            writer.writerow([
                d.get("text", ""),
                d.get("document_id", ""),
                d.get("Generation_Batch_ID", ""),
                d.get("Synthetic_Flag", "true"),
                d.get("Source_Dataset", ""),
                d.get("Provenance_Mode", ""),
                d.get("source_record_reference", ""),
                d.get("Audit_Reference", "")
            ])
            
    print(f"Adapted {len(docs)} documents to {csv_path}")
    settings.extraction_documents_path = csv_path
    
    db = SessionLocal()
    fingerprint = str(uuid.uuid4())[:8] + compute_file_fingerprint(csv_path)[8:]
    
    batch = ExtractionBatch(
        id=uuid.uuid4(),
        file_fingerprint=fingerprint,
        status=ExtractionStatus.RUNNING
    )
    db.add(batch)
    db.commit()
    
    print(f"\nStarting M4 ExtractionEngine for batch {batch.id}...")
    ext_engine = ExtractionEngine(batch_id=batch.id, db=db)
    ext_engine.run()
    
    db.refresh(batch)
    print(f"M4 ExtractionEngine finished. Status: {batch.status.name}")
    print(f"Processed Documents: {batch.processed_documents}")
    print(f"Candidates Extracted: {batch.candidates_extracted}")
    print(f"Extraction Errors: {batch.error_count}")
    
    cand_entities = db.query(CandidateEntity).filter(CandidateEntity.batch_id == batch.id).count()
    cand_rels = db.query(CandidateRelationship).filter(CandidateRelationship.batch_id == batch.id).count()
    
    wordpieces = db.query(CandidateEntity).filter(
        CandidateEntity.batch_id == batch.id,
        CandidateEntity.extracted_text.like("%##%")
    ).count()
    
    # Provenance check
    prov_check = db.query(CandidateEntity).filter(
        CandidateEntity.batch_id == batch.id,
        CandidateEntity.generation_batch_id != "",
        CandidateEntity.provenance_mode != "",
        CandidateEntity.audit_reference != ""
    ).first()
    
    if prov_check:
        print(f"\nProvenance Field Check [PASS]: Found candidate with generation_batch_id={prov_check.generation_batch_id}, provenance_mode={prov_check.provenance_mode}, audit_reference={prov_check.audit_reference}")
    else:
        print("\nProvenance Field Check [FAIL]: Missing authoritative provenance fields on candidates.")

    print("\nStarting M5 ResolutionEngine...")
    res_engine = ResolutionEngine(db=db)
    res_engine.run_resolution_batch(batch_id=batch.id)
    print("M5 ResolutionEngine finished.")
    
    total_matches = db.query(CandidateMatch).join(CandidateEntity).filter(CandidateEntity.batch_id == batch.id).count()
    high = db.query(CandidateMatch).filter(CandidateMatch.confidence_level == "HIGH").join(CandidateEntity).filter(CandidateEntity.batch_id == batch.id).count()
    med = db.query(CandidateMatch).filter(CandidateMatch.confidence_level == "MEDIUM").join(CandidateEntity).filter(CandidateEntity.batch_id == batch.id).count()
    low = db.query(CandidateMatch).filter(CandidateMatch.confidence_level == "LOW").join(CandidateEntity).filter(CandidateEntity.batch_id == batch.id).count()
    
    unresolved = db.query(CandidateEntity).filter(
        CandidateEntity.batch_id == batch.id,
        CandidateEntity.status == CandidateStatus.PENDING_RESOLUTION
    ).count()
    
    resolved_ents = db.query(ResolvedEntity).count()
    resolved_rels = db.query(ResolvedRelationship).count()
    
    print("\n================ M4/M5 VALIDATION REPORT ================")
    print(f"ExtractionBatch Status: {batch.status.name}")
    print(f"Processed Documents: {batch.processed_documents}")
    print(f"Total CandidateEntity (this batch): {cand_entities}")
    print(f"Total CandidateRelationship (this batch): {cand_rels}")
    print(f"Wordpiece Fragments (##): {wordpieces}")
    print(f"Candidate Matches Generated: {total_matches}")
    print(f"  - HIGH Confidence: {high}")
    print(f"  - MEDIUM Confidence: {med}")
    print(f"  - LOW Confidence: {low}")
    print(f"Unresolved Candidates (PENDING_RESOLUTION): {unresolved}")
    print(f"Global ResolvedEntity Count: {resolved_ents}")
    print(f"Global ResolvedRelationship Count: {resolved_rels}")
    print("=========================================================")

if __name__ == "__main__":
    run()
