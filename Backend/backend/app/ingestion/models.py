import uuid
from datetime import datetime, timezone
import enum

from sqlalchemy import String, Integer, DateTime, ForeignKey, Enum, Index, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB

from backend.app.core.postgres import Base


class IngestionStatus(str, enum.Enum):
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class IngestionBatch(Base):
    __tablename__ = "ingestion_batches"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    file_fingerprint: Mapped[str] = mapped_column(String(64), nullable=False)
    file_name: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[IngestionStatus] = mapped_column(Enum(IngestionStatus), nullable=False, default=IngestionStatus.RUNNING)
    
    total_rows: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    processed_rows: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    valid_records: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    error_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )
    completed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)

    errors: Mapped[list["IngestionErrorLog"]] = relationship("IngestionErrorLog", back_populates="batch", cascade="all, delete-orphan")

    __table_args__ = (
        # Database-level uniqueness/concurrency guarantee:
        # A specific file fingerprint can only have ONE successful or actively running batch.
        # This explicitly handles race conditions.
        Index(
            "ix_unique_running_completed_fingerprint",
            "file_fingerprint",
            unique=True,
            postgresql_where=(status.in_([IngestionStatus.RUNNING, IngestionStatus.COMPLETED]))
        ),
    )


class IngestionErrorLog(Base):
    __tablename__ = "ingestion_error_logs"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    batch_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("ingestion_batches.id", ondelete="CASCADE"), nullable=False)
    
    row_index: Mapped[int] = mapped_column(Integer, nullable=True)
    error_message: Mapped[str] = mapped_column(Text, nullable=False)
    raw_data: Mapped[str] = mapped_column(Text, nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )

    batch: Mapped["IngestionBatch"] = relationship("IngestionBatch", back_populates="errors")


class CanonicalNodeRecord(Base):
    """
    Authoritative PostgreSQL storage for M3 canonical nodes.
    Decouples ingestion from synchronous Neo4j projections.
    """
    __tablename__ = "canonical_node_records"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    batch_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("ingestion_batches.id", ondelete="CASCADE"), nullable=False)
    
    canonical_id: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    canonical_label: Mapped[str] = mapped_column(String(255), nullable=False)
    event_type: Mapped[str] = mapped_column(String(255), nullable=True)
    
    payload: Mapped[dict] = mapped_column(JSONB, nullable=False)
    audit_reference: Mapped[str] = mapped_column(String(255), nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )

    batch: Mapped["IngestionBatch"] = relationship("IngestionBatch")


class CanonicalRelationshipRecord(Base):
    """
    Authoritative PostgreSQL storage for M3 canonical relationships.
    """
    __tablename__ = "canonical_relationship_records"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    batch_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("ingestion_batches.id", ondelete="CASCADE"), nullable=False)
    
    source_id: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    target_id: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    relationship_type: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    
    payload: Mapped[dict] = mapped_column(JSONB, nullable=False)
    audit_reference: Mapped[str] = mapped_column(String(255), nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )

    batch: Mapped["IngestionBatch"] = relationship("IngestionBatch")
