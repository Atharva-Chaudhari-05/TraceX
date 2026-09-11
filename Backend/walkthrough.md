# Phase 5 (M5): Entity Resolution Implementation

I have successfully implemented the M5 Entity Resolution components for TraceX according to the final approved plan.

## Completed Work

### 1. Model Schema & Statuses
- Added `PENDING_REVIEW` and `RESOLVED` to `CandidateStatus` enum in `backend/app/extraction/models.py`.
- Added foreign keys connecting `CandidateEntity` and `CandidateRelationship` to resolved schema equivalents.
- Created `ResolvedEntity`, `CandidateMatch`, and `ResolvedRelationship` models in `backend/app/resolution/models.py`.
- Applied all database schema changes via Alembic. 

### 2. Resolution Engine
- Built `ResolutionEngine` (`backend/app/resolution/engine.py`) to handle candidate generation and core explainable identity scoring.
- Implemented **Structured Blocking**: Performs exact phone/account matches before running heavy semantic similarity searches.
- Implemented **MiniLM Semantic Filtering**: Batched MiniLM embedding cosine similarity (>0.70 threshold) acts as a candidate generator when structured blocking is insufficient.
- Implemented **Explainable Scoring**: Calculates exactly using the approved schema:
  - 40% Name Similarity (Jaro-Winkler via RapidFuzz)
  - 30% Shared Phone
  - 15% Shared Account
  - 15% Spatiotemporal Overlap
- Missing metadata evaluates to `0.0` rather than negative penalty scoring.

### 3. Net-new & Review Workflow
- Disabled auto-merging: Proposed identity matches default to a `PENDING` review status for human investigators.
- `create_net_new_resolved_entity` functionality allows users to manually elevate a candidate into a new global identity, providing full audit references. 
- Relationship resolution correctly cascades when both endpoints (Subject and Object) reach `RESOLVED` status.

### 4. Interfaces
- **FastAPI Endpoints:** `api/v1/resolution.py` (e.g. `/resolution/batch/{batch_id}/run`, `/resolution/match/{match_id}/decision`)
- **CLI Commands:**
  - `scripts/run_resolution.py <batch_id>`: Invokes the ResolutionEngine algorithm in batch processing format.
  - `scripts/review_matches.py <batch_id> --auto-confirm <threshold>`: CLI review simulation tool.

### 5. Verification
- All tests specific to M5 Entity Resolution components have passed successfully, confirming logical idempotency and correct explainable scoring output ratios.

> [!TIP]
> You may now run `/code-review` to launch CodeRabbit for a thorough AI-powered review of the M5 implementation code changes!
