"""add auth tables v2

Revision ID: c0d1c389a1d5
Revises: 3845926026ea
Create Date: 2025-11-04 12:00:00.000000

"""

from alembic import op
import sqlalchemy as sa


revision = "c0d1c389a1d5"
down_revision = "3845926026ea"
branch_labels = None
depends_on = None


def upgrade() -> None:
    if not _table_exists("user_accounts"):
        _create_user_accounts()
    if not _table_exists("session_tokens"):
        _create_session_tokens()


def downgrade() -> None:
    if _table_exists("session_tokens"):
        op.drop_index("ix_session_tokens_token", table_name="session_tokens")
        op.drop_table("session_tokens")
    if _table_exists("user_accounts"):
        op.drop_index("ix_user_accounts_login", table_name="user_accounts")
        op.drop_table("user_accounts")


def _create_user_accounts() -> None:
    op.create_table(
        "user_accounts",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("login", sa.String(length=255), nullable=False),
        sa.Column("password_hash", sa.LargeBinary(), nullable=False),
        sa.Column("password_salt", sa.LargeBinary(), nullable=False),
        sa.Column("is_admin", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("player_id", sa.BigInteger(), sa.ForeignKey("players.id", ondelete="SET NULL"), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.UniqueConstraint("player_id", name="uq_user_accounts_player_id"),
    )
    op.create_index("ix_user_accounts_login", "user_accounts", ["login"], unique=True)


def _create_session_tokens() -> None:
    op.create_table(
        "session_tokens",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("token", sa.String(length=128), nullable=False),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("user_accounts.id", ondelete="CASCADE"), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_session_tokens_token", "session_tokens", ["token"], unique=True)


def _table_exists(table_name: str) -> bool:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    return table_name in inspector.get_table_names()
