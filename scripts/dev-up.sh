#!/usr/bin/env bash
set -e

echo "Starting Stratum development environment…"

if [ ! -f .env ]; then
  cp .env.example .env
  echo ".env created from .env.example — PLEASE UPDATE SECRETS before running in production"
fi

docker-compose up -d

echo ""
echo "Services starting:"
echo "  Frontend:  http://localhost:3000"
echo "  Backend:   http://localhost:8000"
echo "  API Docs:  http://localhost:8000/docs"
echo "  Flower:    http://localhost:5555"
echo ""
echo "Run 'make db-migrate' to apply database migrations."
