import argparse
import sys
import uuid
import logging
from sqlalchemy import select

from backend.app.core.postgres import SessionLocal
from backend.app.resolution.engine import ResolutionEngine
from backend.app.resolution.models import CandidateMatch, MatchDecision
from backend.app.extraction.models import CandidateEntity
from backend.app.auth.models import User

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    parser = argparse.ArgumentParser(description="Simulate investigator review for CandidateMatches.")
    parser.add_argument("batch_id", type=str, help="The UUID of the extraction batch.")
    parser.add_argument("--auto-confirm", type=float, help="Automatically confirm matches with final score >= threshold.")
    parser.add_argument("--auto-mint", action="store_true", help="Automatically create net-new entities for PENDING_RESOLUTION candidates.")
    parser.add_argument("--admin-email", type=str, default="admin@example.com", help="Admin email for reviewer_id")
    
    args = parser.parse_args()
    
    try:
        batch_uuid = uuid.UUID(args.batch_id)
    except ValueError:
        logger.error("Invalid batch ID format.")
        sys.exit(1)
        
    db = SessionLocal()
    try:
        # Get admin user for reviewer_id
        admin = db.execute(select(User).where(User.email == args.admin_email)).scalar_one_or_none()
        if not admin:
            logger.error(f"Admin user {args.admin_email} not found.")
            sys.exit(1)
            
        engine = ResolutionEngine(db)
        
        if args.auto_mint:
            from backend.app.extraction.models import CandidateStatus
            pending_res = db.execute(
                select(CandidateEntity)
                .where(CandidateEntity.batch_id == batch_uuid)
                .where(CandidateEntity.status == CandidateStatus.PENDING_RESOLUTION)
            ).scalars().all()
            for cand in pending_res:
                logger.info(f"Auto-minting net-new for {cand.id}")
                engine.create_net_new_resolved_entity(cand.id, admin.id)
        
        # Get pending matches for this batch
        matches = db.execute(
            select(CandidateMatch)
            .join(CandidateEntity, CandidateMatch.candidate_entity_id == CandidateEntity.id)
            .where(CandidateEntity.batch_id == batch_uuid)
            .where(CandidateMatch.decision == MatchDecision.PENDING)
        ).scalars().all()
        
        pending_matches = list(matches)
        
        for match in pending_matches:
            if args.auto_confirm is not None and match.final_weighted_score >= args.auto_confirm:
                logger.info(f"Auto-confirming match {match.id} with score {match.final_weighted_score}")
                engine.confirm_match(match.id, admin.id)
            else:
                logger.info(f"Pending match {match.id} (Score: {match.final_weighted_score}) left for manual review.")
                
    except Exception as e:
        logger.error(f"Review simulation failed: {e}")
        sys.exit(1)
    finally:
        db.close()

if __name__ == "__main__":
    main()
