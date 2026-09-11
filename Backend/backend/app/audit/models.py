import uuid
import enum
from datetime import datetime, timezone

from sqlalchemy import String, DateTime, ForeignKey, Enum, Column
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID, JSONB

from backend.app.core.postgres import Base
import backend.app.auth.models  # Import auth models to register `users` table for FK references


class ActionCategory(str, enum.Enum):
    INGESTION = "INGESTION"
    EXTRACTION = "EXTRACTION"
    RESOLUTION = "RESOLUTION"
    GRAPH_CHANGE = "GRAPH_CHANGE"
    CASE_ACCESS = "CASE_ACCESS"
    ADMIN = "ADMIN"


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False, index=True
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True
    )
    action_category: Mapped[ActionCategory] = mapped_column(Enum(ActionCategory), nullable=False, index=True)
    action_detail: Mapped[str] = mapped_column(String(255), nullable=False)
    entity_type: Mapped[str] = mapped_column(String(100), nullable=True)
    entity_id: Mapped[str] = mapped_column(String(100), nullable=True)
    metadata_: Mapped[dict] = mapped_column("metadata", JSONB, nullable=True)
