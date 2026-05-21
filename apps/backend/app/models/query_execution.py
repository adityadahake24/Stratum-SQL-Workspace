import uuid
from datetime import datetime
from sqlalchemy import String, DateTime, Integer, ForeignKey, Index
from sqlalchemy.orm import mapped_column, Mapped
from sqlalchemy.dialects.postgresql import UUID

from app.db.base import Base


class QueryExecution(Base):
    __tablename__ = "stratum_query_executions"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    history_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("stratum_query_history.id", ondelete="CASCADE"), nullable=False)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("stratum_users.id", ondelete="CASCADE"), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="queued")
    progress_pct: Mapped[int] = mapped_column(Integer, nullable=True, default=0)
    worker_node: Mapped[str] = mapped_column(String(255), nullable=True)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    __table_args__ = (
        Index("ix_query_executions_user_status", "user_id", "status"),
        Index("ix_query_executions_history", "history_id"),
    )
