import sys
import logging
from uuid import UUID

# Ensure the root project directory is in the PYTHONPATH so imports work
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.app.core.logging import configure_logging
from backend.app.core.postgres import SessionLocal
from backend.app.extraction.engine import ExtractionEngine

logger = logging.getLogger(__name__)

import argparse

def main():
    parser = argparse.ArgumentParser(description="Run NLP extraction batch.")
    parser.add_argument("batch_id", help="The UUID of the batch to run.")
    args = parser.parse_args()

    try:
        batch_id = UUID(args.batch_id)
    except ValueError:
        print("Invalid batch ID format. Must be a valid UUID.")
        sys.exit(1)

    configure_logging()
    logger.info(f"Starting NLP extraction batch {batch_id}")
    
    db = SessionLocal()
    try:
        engine = ExtractionEngine(batch_id=batch_id, db=db)
        engine.run()
        logger.info(f"Finished NLP extraction batch {batch_id}")
        
        from backend.app.audit.service import AuditService
        from backend.app.audit.models import ActionCategory
        AuditService.log_action(
            db=db,
            action_category=ActionCategory.EXTRACTION,
            action_detail=f"Extraction batch completed",
            action_metadata={"batch_id": str(batch_id)}
        )
        db.commit()
        
    except Exception as e:
        logger.exception(f"Fatal error running NLP extraction batch {batch_id}: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    main()
