"""add_ip_address_to_local_storage

Revision ID: e9c915b4a06d
Revises: 296c754dec69
Create Date: 2024-11-24 05:29:36.022223

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e9c915b4a06d'
down_revision: Union[str, None] = '296c754dec69'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Step 1: Add column as nullable first (otherwise it will fail with existing records)
    op.add_column('local_storage', sa.Column('ip_address', sa.String(length=45), nullable=True))
    
    # Step 2: Update all existing records
    op.execute("UPDATE local_storage SET ip_address = '0.0.0.0'")
    
    # Step 3: Now we can safely set it to non-nullable
    op.alter_column('local_storage', 'ip_address',
                    existing_type=sa.String(length=45),
                    nullable=False)


def downgrade() -> None:
    op.drop_column('local_storage', 'ip_address')
