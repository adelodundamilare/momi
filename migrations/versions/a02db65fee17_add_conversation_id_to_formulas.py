"""add_conversation_id_to_formulas

Revision ID: a02db65fee17
Revises: 2b9a3ff5bd4e
Create Date: 2025-11-29 05:05:13.353460

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a02db65fee17'
down_revision: Union[str, None] = '2b9a3ff5bd4e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('formulas', sa.Column('conversation_id', sa.Integer(), sa.ForeignKey('conversations.id'), nullable=True))


def downgrade() -> None:
    op.drop_column('formulas', 'conversation_id')
