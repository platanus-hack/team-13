#!/bin/bash
set -e

# Run migrations
poetry run alembic upgrade head

# Start the application
exec poetry run uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
