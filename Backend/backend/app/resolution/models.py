import uuid
from datetime import datetime, timezone
import enum

from sqlalchemy import String, Integer, DateTime, ForeignKey, Enum, Text, Float, Boolean, Index, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB

from backend.app.core.postgres import Base


class MatchDecision(str, enum.Enum):
    PENDING = "PENDING"
    CONFIRMED = "CONFIRMED"
    REJECTED = "REJECTED"


class ConfidenceLevel(str, enum.Enum):
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class ResolvedEntity(Base):
    __tablename__ = "resolved_entities"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    canonical_name: Mapped[str] = mapped_column(String(255), nullable=False)
    canonical_label: Mapped[str] = mapped_column(String(255), nullable=False)
    
    # Provenance Fields (must perfectly mirror the source CandidateEntity)
    synthetic_flag: Mapped[bool] = mapped_column(Boolean, nullable=True)
    source_dataset: Mapped[str] = mapped_column(String(255), nullable=True)
    provenance_mode: Mapped[str] = mapped_column(String(255), nullable=True)
    source_record_reference: Mapped[str] = mapped_column(Text, nullable=True)
    generation_batch_id: Mapped[str] = mapped_column(String(255), nullable=True)
    audit_reference: Mapped[str] = mapped_column(String(255), nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False
    )


class ResolvedRelationship(Base):
    __tablename__ = "resolved_relationships"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    source_resolved_entity_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("resolved_entities.id", ondelete="CASCADE"), nullable=False)
    target_resolved_entity_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("resolved_entities.id", ondelete="CASCADE"), nullable=False)
    
    relationship_type: Mapped[str] = mapped_column(String(255), nullable=False)
    
    # Provenance Fields
    synthetic_flag: Mapped[bool] = mapped_column(Boolean, nullable=True)
    source_dataset: Mapped[str] = mapped_column(String(255), nullable=True)
    provenance_mode: Mapped[str] = mapped_column(String(255), nullable=True)
    generation_batch_id: Mapped[str] = mapped_column(String(255), nullable=True)
    audit_reference: Mapped[str] = mapped_column(String(255), nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False
    )


class CandidateMatch(Base):
    __tablename__ = "candidate_matches"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    candidate_entity_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("candidate_entities.id", ondelete="CASCADE"), nullable=False)
    resolved_entity_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("resolved_entities.id", ondelete="CASCADE"), nullable=True)  # Null if proposing net-new
    
    # Core numerical inputs for ER score
    name_similarity_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    shared_phone_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    shared_account_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    spatiotemporal_overlap_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    
    # Evidence data (JSON)
    minilm_similarity_score: Mapped[float] = mapped_column(Float, nullable=True)
    shared_phone_evidence: Mapped[dict] = mapped_column(JSONB, nullable=True, default=dict)
    shared_account_evidence: Mapped[dict] = mapped_column(JSONB, nullable=True, default=dict)
    spatiotemporal_evidence: Mapped[dict] = mapped_column(JSONB, nullable=True, default=dict)
    
    final_weighted_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    confidence_level: Mapped[ConfidenceLevel] = mapped_column(Enum(ConfidenceLevel), nullable=False)
    decision: Mapped[MatchDecision] = mapped_column(Enum(MatchDecision), nullable=False, default=MatchDecision.PENDING)
    
    reviewer_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    audit_reference: Mapped[str] = mapped_column(String(255), nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False
    )

    __table_args__ = (
        UniqueConstraint("candidate_entity_id", "resolved_entity_id", name="uq_candidate_match"),
    )
