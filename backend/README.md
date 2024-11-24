# run migrations.

- From inside your Docker container

```
cd /app
poetry run alembic revision --autogenerate -m "Initial migration"
poetry run alembic upgrade head
```

or you can do this:

- Start your Docker containers

```
docker-compose up -d
```

- Get into the backend container

```
docker-compose exec backend bash
```

- Create initial migration

```
poetry run alembic revision --autogenerate -m "Create initial tables"
```

- Apply the migration

```
poetry run alembic upgrade head
```

- create seed data

```
poetry run alembic revision -m "Add seed data"
```

- Edit the migration file

- Add seed data

```
Revision ID: xxxx
Revises: yyyy
Create Date: 2024-xx-xx
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import table, column

def upgrade():
    # Create reference tables
    customers = table('customers',
        column('id', sa.Integer),
        column('ip_address', sa.BigInteger),
        column('domain', sa.String)
    )

    blocked_ips = table('blocked_ips',
        column('id', sa.Integer),
        column('ip_address', sa.BigInteger),
        column('is_blocked', sa.Boolean)
    )

    # Insert seed data
    op.bulk_insert(customers,
        [
            {'ip_address': 3232235777, 'domain': 'example.com'},  # 192.168.1.1
            {'ip_address': 3232235778, 'domain': 'test.com'},     # 192.168.1.2
        ]
    )

    op.bulk_insert(blocked_ips,
        [
            {'ip_address': 3232235779, 'is_blocked': True},  # 192.168.1.3
            {'ip_address': 3232235780, 'is_blocked': False}, # 192.168.1.4
        ]
    )

def downgrade():
    op.execute('DELETE FROM customers')
    op.execute('DELETE FROM blocked_ips')
```

## apply migration.

```
poetry run alembic upgrade head
```
