"""fix_time_format_for_local_storage

Revision ID: a5b478b6b867
Revises: e9c915b4a06d
Create Date: 2024-11-24 05:42:33.703318

"""
from typing import Sequence, Union
from datetime import datetime

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a5b478b6b867'
down_revision: Union[str, None] = 'e9c915b4a06d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Modify columns to use datetime.utcnow
    op.alter_column('local_storage', 'created_at',
                    type_=sa.DateTime,
                    server_default=None,
                    existing_nullable=True)
    
    op.alter_column('local_storage', 'blocked_at',
                    type_=sa.DateTime,
                    server_default=None,
                    existing_nullable=True)


def downgrade() -> None:
    pass
