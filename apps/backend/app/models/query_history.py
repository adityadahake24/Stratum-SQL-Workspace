import uuid
from datetime import datetime
from sqlalchemy import String, Boolean, DateTime, Integer, Text, ForeignKey, Index
from sqlalchemy.orm import mapped_column, Mapped
from sqlalchemy.dialects.postgresql import UUID

from app.db.base import Base


class QueryHistory(Base):
    __tablename__ = "stratum_query_history"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("stratum_users.id", ondelete="CASCADE"), nullable=False)
    connection_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("stratum_db_connections.id", ondelete="SET NULL"), nullable=True)
    sql_text: Mapped[str] = mapped_column(Text, nullable=False)
    query_type: Mapped[str] = mapped_column(String(20), nullable=False, default="SELECT")
    execution_status: Mapped[str] = mapped_column(String(20), nullable=False, default="pending")
    execution_time_ms: Mapped[int] = mapped_column(Integer, nullable=True)
    rows_affected: Mapped[int] = mapped_column(Integer, nullable=True)
    row_count: Mapped[int] = mapped_column(Integer, nullable=True)
    error_message: Mapped[str] = mapped_column(Text, nullable=True)
    has_undo: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    undo_snapshot_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=True)
    undo_executed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    __table_args__ = (
        Index("ix_query_history_user_created", "user_id", "created_at"),
        Index("ix_query_history_conn_created", "connection_id", "created_at"),
    )
