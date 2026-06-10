"""create news tables

Revision ID: b14aef8d8906
Revises: 
Create Date: 2026-06-10 17:30:42.111009

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = 'b14aef8d8906'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

addition_status_enum = postgresql.ENUM(
    "pending",
    "done",
    "failed",
    name="additionstatus",
)


def upgrade() -> None:

    op.create_table(
        "news",
        sa.Column("id", sa.Integer(), primary_key=True),

        sa.Column(
            "title",
            sa.String(length=512),
            nullable=False,
        ),

        sa.Column(
            "source",
            sa.String(length=512),
            nullable=False,
        ),

        sa.Column(
            "publication_date",
            sa.Date(),
            nullable=False,
        ),

        sa.Column(
            "announcement",
            sa.Text(),
            nullable=True,
        ),

        sa.Column(
            "addition_status",
            sa.Enum(
                "pending",
                "done",
                "failed",
                name="additionstatus",
            ),
            nullable=False,
            server_default="pending",
        ),

        sa.Column(
            "created_at",
            sa.DateTime(),
            server_default=sa.text("now()"),
            nullable=False,
        ),

        sa.Column(
            "updated_at",
            sa.DateTime(),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )

    op.create_index(
        "ix_news_addition_status",
        "news",
        ["addition_status"],
    )

    # news_addition
    op.create_table(
        "news_addition",
        sa.Column(
            "id",
            sa.Integer(),
            primary_key=True,
        ),

        sa.Column(
            "news_id",
            sa.Integer(),
            sa.ForeignKey(
                "news.id",
                ondelete="CASCADE",
            ),
            nullable=False,
            unique=True,
        ),

        sa.Column(
            "full_text",
            sa.Text(),
            nullable=True,
        ),

        sa.Column(
            "author",
            sa.String(length=256),
            nullable=True,
        ),

        sa.Column(
            "images",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=True,
        ),

        sa.Column(
            "categories",
            postgresql.ARRAY(sa.String()),
            nullable=True,
        ),

        sa.Column(
            "tags",
            postgresql.ARRAY(sa.String()),
            nullable=True,
        ),

        sa.Column(
            "key_words",
            postgresql.ARRAY(sa.String()),
            nullable=True,
        ),

        sa.Column(
            "summary",
            sa.Text(),
            nullable=True,
        ),

        sa.Column(
            "views_amount",
            sa.Integer(),
            nullable=False,
            server_default="0",
        ),

        sa.Column(
            "extra_metadata",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=True,
        ),
    )


def downgrade() -> None:
    op.drop_table("news_addition")

    op.drop_index(
        "ix_news_addition_status",
        table_name="news",
    )

    op.drop_table("news")