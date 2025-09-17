"""add category and tags to trend data

Revision ID: e1a8e2725537
Revises: ae47edd18116
Create Date: 2025-09-17 17:10:20.390251

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e1a8e2725537'
down_revision: Union[str, None] = 'ae47edd18116'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
