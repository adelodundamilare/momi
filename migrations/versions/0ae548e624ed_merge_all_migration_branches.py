"""merge all migration branches

Revision ID: 0ae548e624ed
Revises: a02db65fee17, a1b2c3d4e5f6
Create Date: 2025-11-30 06:47:45.689116

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0ae548e624ed'
down_revision: Union[str, None] = ('a02db65fee17', 'a1b2c3d4e5f6')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
