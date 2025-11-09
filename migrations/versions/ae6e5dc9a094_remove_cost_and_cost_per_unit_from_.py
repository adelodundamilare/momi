"""Remove cost and cost_per_unit from Ingredient

Revision ID: ae6e5dc9a094
Revises: 059669725075
Create Date: 2025-09-13 21:06:04.186065

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ae6e5dc9a094'
down_revision: Union[str, None] = '059669725075'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    existing_tables = inspector.get_table_names()

    if 'formula_ingredients' in existing_tables:
        formula_ingredient_columns = [col['name'] for col in inspector.get_columns('formula_ingredients')]

        if 'supplier_id' not in formula_ingredient_columns:
            op.add_column('formula_ingredients', sa.Column('supplier_id', sa.Integer(), nullable=True))

        try:
            op.create_foreign_key(None, 'formula_ingredients', 'suppliers', ['supplier_id'], ['id'])
        except Exception as e:
            print(f"Foreign key might already exist: {e}")

    if 'ingredients' in existing_tables:
        ingredient_columns = [col['name'] for col in inspector.get_columns('ingredients')]

        if 'cost' in ingredient_columns:
            op.drop_column('ingredients', 'cost')
        if 'cost_per_unit' in ingredient_columns:
            op.drop_column('ingredients', 'cost_per_unit')

    if 'suppliers' in existing_tables:
        supplier_columns = [col['name'] for col in inspector.get_columns('suppliers')]

        if 'price_per_unit' not in supplier_columns:
            op.add_column('suppliers', sa.Column('price_per_unit', sa.Float(), nullable=True))

        if 'price_per_kg' in supplier_columns:
            op.drop_column('suppliers', 'price_per_kg')


def downgrade() -> None:
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    existing_tables = inspector.get_table_names()

    if 'suppliers' in existing_tables:
        supplier_columns = [col['name'] for col in inspector.get_columns('suppliers')]

        if 'price_per_kg' not in supplier_columns:
            op.add_column('suppliers', sa.Column('price_per_kg', sa.DOUBLE_PRECISION(precision=53), autoincrement=False, nullable=True))
        if 'price_per_unit' in supplier_columns:
            op.drop_column('suppliers', 'price_per_unit')

    if 'ingredients' in existing_tables:
        ingredient_columns = [col['name'] for col in inspector.get_columns('ingredients')]

        if 'cost_per_unit' not in ingredient_columns:
            op.add_column('ingredients', sa.Column('cost_per_unit', sa.DOUBLE_PRECISION(precision=53), autoincrement=False, nullable=True))
        if 'cost' not in ingredient_columns:
            op.add_column('ingredients', sa.Column('cost', sa.DOUBLE_PRECISION(precision=53), autoincrement=False, nullable=True))

    if 'formula_ingredients' in existing_tables:
        try:
            op.drop_constraint(None, 'formula_ingredients', type_='foreignkey')
        except Exception:
            pass

        formula_ingredient_columns = [col['name'] for col in inspector.get_columns('formula_ingredients')]
        if 'supplier_id' in formula_ingredient_columns:
            op.drop_column('formula_ingredients', 'supplier_id')