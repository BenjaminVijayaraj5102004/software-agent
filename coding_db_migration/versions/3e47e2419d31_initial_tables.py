"""initial tables

Revision ID: 3e47e2419d31
Revises: 
Create Date: 2026-06-22 11:45:12.856751

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3e47e2419d31'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

"""initial tables

Revision ID: 3e47e2419d31
Revises: 
Create Date: 2026-06-22 11:45:12.856751

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '3e47e2419d31'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None




def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("password_hash", sa.String(), nullable=False),
        sa.Column("tier", sa.String(length=20), nullable=False, server_default="free"),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.text("now()")),
        sa.UniqueConstraint("email"),
    )

    op.create_index("ix_users_email", "users", ["email"], unique=False)

    op.create_table(
        "conversations",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("title", sa.String(length=500)),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.text("now()")),
    )

    op.create_index(
        "idx_conversations_user_created",
        "conversations",
        ["user_id", "created_at"],
        unique=False,
    )

    op.create_table(
        "messages",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "conversation_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("conversations.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("role", sa.String(length=20), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("token_count", sa.Integer()),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()")),
    )

    op.create_index(
        "idx_messages_conversation_created",
        "messages",
        ["conversation_id", "created_at"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("idx_messages_conversation_created", table_name="messages")
    op.drop_table("messages")

    op.drop_index(
        "idx_conversations_user_created",
        table_name="conversations",
    )
    op.drop_table("conversations")

    op.drop_index("ix_users_email", table_name="users")
    op.drop_table("users")
