import pytest
import os
import shutil
from pathlib import Path

from backend.app.core.postgres import SessionLocal, Base, engine
from backend.app.ingestion.engine import PipelineEngine
from backend.app.ingestion.models import IngestionBatch

def test_smoke_dataset_generator_produces_records():
    """
    Proves that the smoke dataset generator produces non-zero canonical records
    for the required entities and that it avoids the idempotency lock by
    generating unique hashes per run.
    """
    # Create the db schema in test DB
    Base.metadata.create_all(bind=engine)
    
    # Load create_dataset using importlib
    import importlib.util
    spec = importlib.util.spec_from_file_location("create_smoke_dataset", "scratch/create_smoke_dataset.py")
    smoke_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(smoke_module)
    create_dataset = smoke_module.create_dataset
    
    dataset_dir = Path("scratch/smoke_dataset")
    if dataset_dir.exists():
        shutil.rmtree(dataset_dir)
        
    db = SessionLocal()
    try:
        # 1. Run generator the first time
        create_dataset()
        
        ingestion_engine = PipelineEngine(db)
        cases_file = str(dataset_dir / "cases.csv")
        
        # Test it produces > 0 records
        records_1 = list(ingestion_engine.process_file(cases_file))
        assert len(records_1) == 2, "Expected 2 canonical records for cases.csv"
        
        # 2. Run generator a second time (simulating a second smoke test run)
        import time
        time.sleep(1) # ensure time.time() changes
        create_dataset()
        
        # Test it again produces > 0 records (bypassing idempotency lock)
        records_2 = list(ingestion_engine.process_file(cases_file))
        assert len(records_2) == 2, "Expected 2 canonical records after re-generating (idempotency bypass)"
        
    finally:
        # Cleanup
        db.query(IngestionBatch).filter(IngestionBatch.file_name == "cases.csv").delete()
        db.commit()
        db.close()
