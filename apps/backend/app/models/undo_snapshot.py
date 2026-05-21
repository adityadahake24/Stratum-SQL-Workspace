import uuid
from datetime import datetime
from sqlalchemy import String, DateTime, Integer, Text, LargeBinary, ForeignKey, Index
from sqlalchemy.orm import mapped_column, Mapped
from sqlalchemy.dialects.postgresql import UUID

from app.db.base import Base


class UndoSnapshot(Base):
    __tablename__ = "stratum_undo_snapshots"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    history_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("stratum_query_history.id", ondelete="CASCADE"), nullable=False)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("stratum_users.id", ondelete="CASCADE"), nullable=False)
    operation_type: Mapped[str] = mapped_column(String(20), nullable=False)
    table_name: Mapped[str] = mapped_column(String(255), nullable=False)
    schema_name: Mapped[str] = mapped_column(String(255), nullable=False, default="public")
    snapshot_data: Mapped[bytes] = mapped_column(LargeBinary, nullable=True)
    snapshot_size_bytes: Mapped[int] = mapped_column(Integer, nullable=True)
    row_count: Mapped[int] = mapped_column(Integer, nullable=True)
    inverse_sql: Mapped[str] = mapped_column(Text, nullable=True)
    is_consumed: Mapped[bool] = mapped_column(default=False, nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    __table_args__ = (
        Index("ix_undo_snapshots_user_expires", "user_id", "expires_at"),
        Index("ix_undo_snapshots_history", "history_id"),
    )
