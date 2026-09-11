import uuid
from datetime import datetime, timezone
import enum

from sqlalchemy import String, Integer, DateTime, ForeignKey, Enum, Text, Float, Boolean, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB

from backend.app.core.postgres import Base
import backend.app.resolution.models  # Ensure target tables are in metadata for FKs


class ExtractionStatus(str, enum.Enum):
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class CandidateStatus(str, enum.Enum):
    PENDING_RESOLUTION = "PENDING_RESOLUTION"
    PENDING_REVIEW = "PENDING_REVIEW"
    RESOLVED = "RESOLVED"
    REJECTED = "REJECTED"


class ExtractionBatch(Base):
    __tablename__ = "extraction_batches"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    file_fingerprint: Mapped[str] = mapped_column(String(64), nullable=False)
    status: Mapped[ExtractionStatus] = mapped_column(Enum(ExtractionStatus), nullable=False, default=ExtractionStatus.RUNNING)
    
    total_documents: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    processed_documents: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    candidates_extracted: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    error_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )
    completed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    
    candidates: Mapped[list["CandidateEntity"]] = relationship("CandidateEntity", back_populates="batch", cascade="all, delete-orphan")
    candidate_relationships: Mapped[list["CandidateRelationship"]] = relationship("CandidateRelationship", back_populates="batch", cascade="all, delete-orphan")

    __table_args__ = (
        Index(
            "ix_extraction_unique_running_completed_fingerprint",
            "file_fingerprint",
            unique=True,
            postgresql_where=(status.in_([ExtractionStatus.RUNNING, ExtractionStatus.COMPLETED]))
        ),
    )


class CandidateEntity(Base):
    __tablename__ = "candidate_entities"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    batch_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("extraction_batches.id", ondelete="CASCADE"), nullable=False)
    
    canonical_label: Mapped[str] = mapped_column(String(255), nullable=False)
    extracted_text: Mapped[str] = mapped_column(Text, nullable=False)
    
    resolved_entity_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("resolved_entities.id", ondelete="SET NULL"), nullable=True)
    normalized_payload: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    
    extraction_method: Mapped[str] = mapped_column(String(255), nullable=False)
    confidence_score: Mapped[float] = mapped_column(Float, nullable=False)
    status: Mapped[CandidateStatus] = mapped_column(Enum(CandidateStatus), nullable=False, default=CandidateStatus.PENDING_RESOLUTION)
    
    # Provenance Fields
    source_document_id: Mapped[str] = mapped_column(String(255), nullable=False)
    generation_batch_id: Mapped[str] = mapped_column(String(255), nullable=True)
    audit_reference: Mapped[str] = mapped_column(String(255), nullable=True)
    synthetic_flag: Mapped[bool] = mapped_column(Boolean, nullable=True)
    source_dataset: Mapped[str] = mapped_column(String(255), nullable=True)
    provenance_mode: Mapped[str] = mapped_column(String(255), nullable=True)
    source_record_reference: Mapped[str] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )

    batch: Mapped["ExtractionBatch"] = relationship("ExtractionBatch", back_populates="candidates")

class CandidateRelationship(Base):
    __tablename__ = "candidate_relationships"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    batch_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("extraction_batches.id", ondelete="CASCADE"), nullable=False)
    
    source_candidate_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("candidate_entities.id", ondelete="CASCADE"), nullable=False)
    target_candidate_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("candidate_entities.id", ondelete="CASCADE"), nullable=False)
    
    relationship_type: Mapped[str] = mapped_column(String(255), nullable=False)
    
    resolved_relationship_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("resolved_relationships.id", ondelete="SET NULL"), nullable=True)
    confidence_score: Mapped[float] = mapped_column(Float, nullable=False)
    evidence_span: Mapped[str] = mapped_column(Text, nullable=False)
    extraction_method: Mapped[str] = mapped_column(String(255), nullable=False)
    
    status: Mapped[CandidateStatus] = mapped_column(Enum(CandidateStatus), nullable=False, default=CandidateStatus.PENDING_RESOLUTION)
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )

    batch: Mapped["ExtractionBatch"] = relationship("ExtractionBatch", back_populates="candidate_relationships")
