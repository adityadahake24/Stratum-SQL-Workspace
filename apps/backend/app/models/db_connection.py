import uuid
from datetime import datetime
from sqlalchemy import String, Boolean, DateTime, Integer, ForeignKey
from sqlalchemy.orm import mapped_column, Mapped
from sqlalchemy.dialects.postgresql import UUID

from app.db.base import Base
from app.models.base import TimestampMixin


class DbConnection(TimestampMixin, Base):
    __tablename__ = "stratum_db_connections"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("stratum_users.id", ondelete="CASCADE"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    host: Mapped[str] = mapped_column(String(1024), nullable=False)  # encrypted
    port: Mapped[int] = mapped_column(Integer, nullable=False, default=5432)
    database: Mapped[str] = mapped_column(String(1024), nullable=False)  # encrypted
    username: Mapped[str] = mapped_column(String(1024), nullable=False)  # encrypted
    password_encrypted: Mapped[str] = mapped_column(String(2048), nullable=False)
    ssl_mode: Mapped[str] = mapped_column(String(20), nullable=False, default="disable")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    last_used_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
