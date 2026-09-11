import uuid
import logging
from typing import List, Tuple, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import select

from rapidfuzz.distance import JaroWinkler

from backend.app.extraction.models import CandidateEntity, CandidateRelationship, CandidateStatus
from backend.app.resolution.models import (
    ResolvedEntity, CandidateMatch, ResolvedRelationship,
    ConfidenceLevel, MatchDecision
)
from backend.app.resolution.providers.embedding import get_embedding_provider
from backend.app.graph.engine import GraphEngine

logger = logging.getLogger(__name__)

class ResolutionEngine:
    def __init__(self, db: Session):
        self.db = db
        self.embedding_provider = get_embedding_provider()
        self.graph_engine = GraphEngine()
        
    def _get_entity_attributes(self, entity_id: uuid.UUID) -> Dict[str, set]:
        """
        Retrieves structured attributes (phones, accounts, locations/times) linked to this entity.
        It checks relationships where this entity is the source or target, linked to 'Phone', 'Account', 'LOC', 'DATE', 'TIME'.
        """
        # Find all candidate relationships involving this entity
        rels = self.db.execute(
            select(CandidateRelationship).where(
                (CandidateRelationship.source_candidate_id == entity_id) | 
                (CandidateRelationship.target_candidate_id == entity_id)
            )
        ).scalars().all()
        
        attributes = {
            "phones": set(),
            "accounts": set(),
            "spatiotemporal": set()
        }
        
        for rel in rels:
            # Determine the other entity
            other_id = rel.target_candidate_id if rel.source_candidate_id == entity_id else rel.source_candidate_id
            other_entity = self.db.get(CandidateEntity, other_id)
            if not other_entity:
                continue
                
            label = other_entity.canonical_label.upper()
            val = other_entity.extracted_text.strip().lower()
            
            if "PHONE" in label:
                attributes["phones"].add(val)
            elif "ACCOUNT" in label:
                attributes["accounts"].add(val)
            elif label in ("LOC", "GPE", "DATE", "TIME"):
                attributes["spatiotemporal"].add(val)
                
        return attributes

    def _get_resolved_attributes(self, resolved_entity_id: uuid.UUID) -> Dict[str, set]:
        """
        For a ResolvedEntity, we look at all CandidateEntities that have been CONFIRMED to it,
        and aggregate their attributes.
        """
        candidates = self.db.execute(
            select(CandidateEntity).where(CandidateEntity.resolved_entity_id == resolved_entity_id)
        ).scalars().all()
        
        attributes = {
            "phones": set(),
            "accounts": set(),
            "spatiotemporal": set()
        }
        for cand in candidates:
            cand_attrs = self._get_entity_attributes(cand.id)
            attributes["phones"].update(cand_attrs["phones"])
            attributes["accounts"].update(cand_attrs["accounts"])
            attributes["spatiotemporal"].update(cand_attrs["spatiotemporal"])
            
        return attributes

    def run_resolution_batch(self, batch_id: uuid.UUID):
        """
        Propose matches for all PENDING_RESOLUTION candidates in a batch against all existing global ResolvedEntities.
        """
        logger.info(f"Starting resolution for batch {batch_id}")
        
        # 1. Fetch pending candidates
        candidates = self.db.execute(
            select(CandidateEntity)
            .where(CandidateEntity.batch_id == batch_id)
            .where(CandidateEntity.status == CandidateStatus.PENDING_RESOLUTION)
        ).scalars().all()
        
        if not candidates:
            logger.info("No PENDING_RESOLUTION candidates found in this batch.")
            return

        # 2. Load all existing ResolvedEntities
        resolved_entities = self.db.execute(select(ResolvedEntity)).scalars().all()
        
        # If no resolved entities exist, we can't propose any matches.
        # We just leave them PENDING_RESOLUTION so the investigator can manually mint net-new.
        if not resolved_entities:
            logger.info("No global ResolvedEntity records exist. Candidates will remain PENDING_RESOLUTION for explicit net-new creation.")
            return
            
        resolved_texts = [r.canonical_name for r in resolved_entities]
        resolved_embeddings = self.embedding_provider.get_embeddings(resolved_texts)
        
        # --- PERF OPTIMIZATION: Bulk fetches ---
        candidate_ids = [c.id for c in candidates]
        
        # 3. Pre-fetch existing CandidateMatches for these candidates
        existing_matches = self.db.execute(
            select(CandidateMatch).where(CandidateMatch.candidate_entity_id.in_(candidate_ids))
        ).scalars().all()
        existing_match_pairs = set((m.candidate_entity_id, m.resolved_entity_id) for m in existing_matches)
        
        # 4. Pre-fetch resolved attributes
        resolved_attributes = {}
        for resolved in resolved_entities:
            resolved_attributes[resolved.id] = self._get_resolved_attributes(resolved.id)
            
        # 5. Batch candidate embeddings
        cand_texts = [c.extracted_text for c in candidates]
        cand_embeddings = self.embedding_provider.get_embeddings(cand_texts)
        
        for cand_idx, candidate in enumerate(candidates):
            cand_attrs = self._get_entity_attributes(candidate.id)
            proposed_matches = []
            
            # Step A: Structured Blocking / Exact Match
            # Check if any resolved entity shares a phone or account exactly.
            for i, resolved in enumerate(resolved_entities):
                # Check for existing rejected match to enforce idempotency
                if (candidate.id, resolved.id) in existing_match_pairs:
                    continue # Skip already processed pairs
                
                res_attrs = resolved_attributes[resolved.id]
                has_exact_overlap = (
                    bool(cand_attrs["phones"].intersection(res_attrs["phones"])) or
                    bool(cand_attrs["accounts"].intersection(res_attrs["accounts"]))
                )
                
                if has_exact_overlap:
                    proposed_matches.append((resolved, res_attrs, None)) # Force yield
                    
            # Step B: MiniLM Candidate Generation
            # If no exact overlap, we fall back to semantic similarity > 0.70
            if not proposed_matches and resolved_embeddings.size(0) > 0:
                cand_emb = cand_embeddings[cand_idx].unsqueeze(0)
                # Compute cosine similarities
                import torch
                cos_sims = torch.nn.functional.cosine_similarity(cand_emb, resolved_embeddings)
                
                for i, score in enumerate(cos_sims):
                    if score.item() > 0.70:
                        resolved = resolved_entities[i]
                        # Idempotency check
                        if (candidate.id, resolved.id) not in existing_match_pairs:
                            res_attrs = resolved_attributes[resolved.id]
                            # Only add if not already added by structured blocking
                            if not any(m[0].id == resolved.id for m in proposed_matches):
                                proposed_matches.append((resolved, res_attrs, score.item()))
                                
            # Step C: Pairwise Explainable Scoring
            for resolved, res_attrs, minilm_score in proposed_matches:
                # 1. Name similarity (Jaro-Winkler)
                name_sim = JaroWinkler.normalized_similarity(
                    candidate.extracted_text.lower(),
                    resolved.canonical_name.lower()
                )
                
                # 2. Shared phone (0.0 or 1.0)
                shared_phones = cand_attrs["phones"].intersection(res_attrs["phones"])
                if not cand_attrs["phones"] or not res_attrs["phones"]:
                    phone_score = 0.0
                else:
                    phone_score = 1.0 if shared_phones else 0.0
                    
                # 3. Shared account (0.0 or 1.0)
                shared_accounts = cand_attrs["accounts"].intersection(res_attrs["accounts"])
                if not cand_attrs["accounts"] or not res_attrs["accounts"]:
                    account_score = 0.0
                else:
                    account_score = 1.0 if shared_accounts else 0.0
                    
                # 4. Spatiotemporal overlap (0.0 to 1.0)
                shared_st = cand_attrs["spatiotemporal"].intersection(res_attrs["spatiotemporal"])
                if not cand_attrs["spatiotemporal"] or not res_attrs["spatiotemporal"]:
                    st_score = 0.0
                else:
                    st_score = len(shared_st) / float(len(cand_attrs["spatiotemporal"]))
                    
                # Calculate final score
                final_score = (0.40 * name_sim) + (0.30 * phone_score) + (0.15 * account_score) + (0.15 * st_score)
                
                if final_score >= 0.85:
                    confidence = ConfidenceLevel.HIGH
                elif final_score >= 0.60:
                    confidence = ConfidenceLevel.MEDIUM
                else:
                    confidence = ConfidenceLevel.LOW
                    
                # Create CandidateMatch
                match_record = CandidateMatch(
                    candidate_entity_id=candidate.id,
                    resolved_entity_id=resolved.id,
                    name_similarity_score=name_sim,
                    shared_phone_score=phone_score,
                    shared_phone_evidence=list(shared_phones) if shared_phones else (["insufficient evidence"] if not cand_attrs["phones"] or not res_attrs["phones"] else []),
                    shared_account_score=account_score,
                    shared_account_evidence=list(shared_accounts) if shared_accounts else (["insufficient evidence"] if not cand_attrs["accounts"] or not res_attrs["accounts"] else []),
                    spatiotemporal_overlap_score=st_score,
                    spatiotemporal_evidence=list(shared_st) if shared_st else (["insufficient evidence"] if not cand_attrs["spatiotemporal"] or not res_attrs["spatiotemporal"] else []),
                    minilm_similarity_score=minilm_score,
                    final_weighted_score=final_score,
                    confidence_level=confidence,
                    decision=MatchDecision.PENDING
                )
                self.db.add(match_record)
                
            if proposed_matches:
                candidate.status = CandidateStatus.PENDING_REVIEW
                
        self.db.commit()
        logger.info(f"Resolution batch {batch_id} complete.")

    def confirm_match(self, match_id: uuid.UUID, reviewer_id: uuid.UUID):
        match_record = self.db.get(CandidateMatch, match_id)
        if not match_record or match_record.decision != MatchDecision.PENDING:
            raise ValueError("Invalid match record or already processed.")
            
        candidate = self.db.get(CandidateEntity, match_record.candidate_entity_id)
        
        match_record.decision = MatchDecision.CONFIRMED
        match_record.reviewer_id = reviewer_id
        
        candidate.resolved_entity_id = match_record.resolved_entity_id
        candidate.status = CandidateStatus.RESOLVED
        
        # Check and resolve relationships
        new_rels = self._resolve_relationships(candidate.id)
        self.db.commit()

        # Neo4j Synchronization (After PG Commit)
        try:
            resolved_entity = self.db.get(ResolvedEntity, candidate.resolved_entity_id)
            if resolved_entity:
                self.graph_engine.sync_resolved_entity(resolved_entity)
        except Exception as e:
            logger.error(f"Neo4j sync failed for ResolvedEntity {candidate.resolved_entity_id}: {e}")

        for r_rel in new_rels:
            try:
                self.graph_engine.sync_resolved_relationship(r_rel)
            except Exception as e:
                logger.error(f"Neo4j sync failed for ResolvedRelationship {r_rel.id}: {e}")

    def reject_match(self, match_id: uuid.UUID, reviewer_id: uuid.UUID):
        match_record = self.db.get(CandidateMatch, match_id)
        if not match_record or match_record.decision != MatchDecision.PENDING:
            raise ValueError("Invalid match record or already processed.")
            
        match_record.decision = MatchDecision.REJECTED
        match_record.reviewer_id = reviewer_id
        self.db.commit()

    def create_net_new_resolved_entity(self, candidate_id: uuid.UUID, reviewer_id: uuid.UUID):
        candidate = self.db.get(CandidateEntity, candidate_id)
        if not candidate or candidate.status == CandidateStatus.RESOLVED:
            raise ValueError("Invalid candidate or already resolved.")
            
        # Create new resolved entity mirroring provenance
        resolved = ResolvedEntity(
            canonical_name=candidate.extracted_text,
            canonical_label=candidate.canonical_label,
            synthetic_flag=candidate.synthetic_flag,
            source_dataset=candidate.source_dataset,
            provenance_mode=candidate.provenance_mode,
            generation_batch_id=candidate.generation_batch_id,
            audit_reference=candidate.audit_reference
        )
        self.db.add(resolved)
        self.db.flush() # get ID
        
        candidate.resolved_entity_id = resolved.id
        candidate.status = CandidateStatus.RESOLVED
        
        # Create a synthetic CONFIRMED match for auditability
        match_record = CandidateMatch(
            candidate_entity_id=candidate.id,
            resolved_entity_id=resolved.id,
            name_similarity_score=1.0,
            final_weighted_score=1.0,
            confidence_level=ConfidenceLevel.HIGH,
            decision=MatchDecision.CONFIRMED,
            reviewer_id=reviewer_id,
            audit_reference="NET_NEW_CREATION"
        )
        self.db.add(match_record)
        
        new_rels = self._resolve_relationships(candidate.id)
        self.db.commit()

        # Neo4j Synchronization (After PG Commit)
        try:
            self.graph_engine.sync_resolved_entity(resolved)
        except Exception as e:
            logger.error(f"Neo4j sync failed for ResolvedEntity {resolved.id}: {e}")

        for r_rel in new_rels:
            try:
                self.graph_engine.sync_resolved_relationship(r_rel)
            except Exception as e:
                logger.error(f"Neo4j sync failed for ResolvedRelationship {r_rel.id}: {e}")

    def _resolve_relationships(self, candidate_id: uuid.UUID):
        """
        Find all CandidateRelationships involving this candidate.
        If both source and target candidates are RESOLVED, create ResolvedRelationship.
        """
        rels = self.db.execute(
            select(CandidateRelationship).where(
                (CandidateRelationship.source_candidate_id == candidate_id) |
                (CandidateRelationship.target_candidate_id == candidate_id)
            )
        ).scalars().all()
        
        new_resolved_rels = []
        for rel in rels:
            if rel.status == CandidateStatus.RESOLVED:
                continue
                
            source_cand = self.db.get(CandidateEntity, rel.source_candidate_id)
            target_cand = self.db.get(CandidateEntity, rel.target_candidate_id)
            
            if source_cand.status == CandidateStatus.RESOLVED and target_cand.status == CandidateStatus.RESOLVED:
                resolved_rel = ResolvedRelationship(
                    source_resolved_entity_id=source_cand.resolved_entity_id,
                    target_resolved_entity_id=target_cand.resolved_entity_id,
                    relationship_type=rel.relationship_type,
                    synthetic_flag=source_cand.synthetic_flag, # Inherit from source or standard rule
                    source_dataset=source_cand.source_dataset,
                    provenance_mode=source_cand.provenance_mode,
                    generation_batch_id=source_cand.generation_batch_id,
                    audit_reference=rel.evidence_span
                )
                self.db.add(resolved_rel)
                self.db.flush()
                
                rel.resolved_relationship_id = resolved_rel.id
                rel.status = CandidateStatus.RESOLVED
                new_resolved_rels.append(resolved_rel)
                
        return new_resolved_rels
