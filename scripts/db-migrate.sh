#!/usr/bin/env bash
set -e

echo "Running Alembic migrations..."
docker-compose exec backend alembic upgrade head
echo "Migrations complete."
