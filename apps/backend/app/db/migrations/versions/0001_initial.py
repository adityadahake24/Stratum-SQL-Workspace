"""initial

Revision ID: 0001
Revises:
Create Date: 2026-05-21

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "stratum_users",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("email", sa.String(255), nullable=False, unique=True),
        sa.Column("hashed_password", sa.String(255), nullable=False),
        sa.Column("is_active", sa.Boolean, nullable=False, default=True),
        sa.Column("is_verified", sa.Boolean, nullable=False, default=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_stratum_users_email", "stratum_users", ["email"])

    op.create_table(
        "stratum_sessions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("stratum_users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("token_hash", sa.String(255), nullable=False),
        sa.Column("ip_address", sa.String(45), nullable=True),
        sa.Column("user_agent", sa.String(512), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("is_active", sa.Boolean, nullable=False, default=True),
    )
    op.create_index("ix_stratum_sessions_token_hash", "stratum_sessions", ["token_hash"])
    op.create_index("ix_stratum_sessions_user_active", "stratum_sessions", ["user_id", "is_active"])

    op.create_table(
        "stratum_db_connections",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("stratum_users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("host", sa.String(1024), nullable=False),
        sa.Column("port", sa.Integer, nullable=False, default=5432),
        sa.Column("database", sa.String(1024), nullable=False),
        sa.Column("username", sa.String(1024), nullable=False),
        sa.Column("password_encrypted", sa.String(2048), nullable=False),
        sa.Column("ssl_mode", sa.String(20), nullable=False, default="disable"),
        sa.Column("is_active", sa.Boolean, nullable=False, default=True),
        sa.Column("last_used_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_stratum_db_connections_user_id", "stratum_db_connections", ["user_id"])

    op.create_table(
        "stratum_query_history",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("stratum_users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("connection_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("stratum_db_connections.id", ondelete="SET NULL"), nullable=True),
        sa.Column("sql_text", sa.Text, nullable=False),
        sa.Column("query_type", sa.String(20), nullable=False, default="SELECT"),
        sa.Column("execution_status", sa.String(20), nullable=False, default="pending"),
        sa.Column("execution_time_ms", sa.Integer, nullable=True),
        sa.Column("rows_affected", sa.Integer, nullable=True),
        sa.Column("row_count", sa.Integer, nullable=True),
        sa.Column("error_message", sa.Text, nullable=True),
        sa.Column("has_undo", sa.Boolean, nullable=False, default=False),
        sa.Column("undo_snapshot_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("undo_executed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_query_history_user_created", "stratum_query_history", ["user_id", "created_at"])
    op.create_index("ix_query_history_conn_created", "stratum_query_history", ["connection_id", "created_at"])

    op.create_table(
        "stratum_query_executions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("history_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("stratum_query_history.id", ondelete="CASCADE"), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("stratum_users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("status", sa.String(20), nullable=False, default="queued"),
        sa.Column("progress_pct", sa.Integer, nullable=True, default=0),
        sa.Column("worker_node", sa.String(255), nullable=True),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_query_executions_user_status", "stratum_query_executions", ["user_id", "status"])
    op.create_index("ix_query_executions_history", "stratum_query_executions", ["history_id"])

    op.create_table(
        "stratum_undo_snapshots",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("history_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("stratum_query_history.id", ondelete="CASCADE"), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("stratum_users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("operation_type", sa.String(20), nullable=False),
        sa.Column("table_name", sa.String(255), nullable=False),
        sa.Column("schema_name", sa.String(255), nullable=False, default="public"),
        sa.Column("snapshot_data", sa.LargeBinary, nullable=True),
        sa.Column("snapshot_size_bytes", sa.Integer, nullable=True),
        sa.Column("row_count", sa.Integer, nullable=True),
        sa.Column("inverse_sql", sa.Text, nullable=True),
        sa.Column("is_consumed", sa.Boolean, nullable=False, default=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_undo_snapshots_user_expires", "stratum_undo_snapshots", ["user_id", "expires_at"])
    op.create_index("ix_undo_snapshots_history", "stratum_undo_snapshots", ["history_id"])

    op.create_table(
        "stratum_support_requests",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("stratum_users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("email", sa.String(255), nullable=False),
        sa.Column("message", sa.Text, nullable=False),
        sa.Column("status", sa.String(20), nullable=False, default="open"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("stratum_support_requests")
    op.drop_table("stratum_undo_snapshots")
    op.drop_table("stratum_query_executions")
    op.drop_table("stratum_query_history")
    op.drop_table("stratum_db_connections")
    op.drop_table("stratum_sessions")
    op.drop_table("stratum_users")
