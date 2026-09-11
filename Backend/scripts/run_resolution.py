import argparse
import sys
import uuid
import logging

from backend.app.core.postgres import SessionLocal
from backend.app.auth.models import User
from backend.app.resolution.engine import ResolutionEngine

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    parser = argparse.ArgumentParser(description="Run Entity Resolution (M5) for a specific extraction batch.")
    parser.add_argument("batch_id", type=str, help="The UUID of the extraction batch to process.")
    
    args = parser.parse_args()
    
    try:
        batch_uuid = uuid.UUID(args.batch_id)
    except ValueError:
        logger.error("Invalid batch ID format. Must be a valid UUID.")
        sys.exit(1)
        
    db = SessionLocal()
    try:
        engine = ResolutionEngine(db)
        engine.run_resolution_batch(batch_uuid)
    except Exception as e:
        logger.error(f"Resolution failed: {e}")
        db.rollback()
        sys.exit(1)
    finally:
        db.close()

if __name__ == "__main__":
    main()
