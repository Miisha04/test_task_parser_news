"""add url to news table

Revision ID: add_url_to_news
Revises: b14aef8d8906
Create Date: 2026-06-11 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'add_url_to_news'
down_revision: Union[str, Sequence[str], None] = 'b14aef8d8906'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        'news',
        sa.Column(
            'url',
            sa.String(length=2048),
            nullable=True,
        )
    )
    
    # Set default URL for existing rows to avoid NOT NULL constraint violation
    op.execute("UPDATE news SET url = CONCAT('https://ria.ru/news/', id) WHERE url IS NULL")
    
    # Make url not nullable after setting default values
    op.alter_column(
        'news',
        'url',
        existing_type=sa.String(length=2048),
        nullable=False,
    )
    
    # Create unique index for url
    op.create_index(
        'ix_news_url',
        'news',
        ['url'],
        unique=True,
    )


def downgrade() -> None:
    op.drop_index('ix_news_url', table_name='news')
    op.drop_column('news', 'url')
