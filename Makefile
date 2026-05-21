.PHONY: dev-up dev-down db-migrate db-seed generate-secret logs backend-shell frontend-shell test build

dev-up:
	cp -n .env.example .env || true
	docker-compose up -d

dev-down:
	docker-compose down

dev-logs:
	docker-compose logs -f

db-migrate:
	docker-compose exec backend alembic upgrade head

db-makemigration:
	docker-compose exec backend alembic revision --autogenerate -m "$(msg)"

db-seed:
	docker-compose exec backend python scripts/db-seed.py

db-reset:
	docker-compose exec backend alembic downgrade base
	docker-compose exec backend alembic upgrade head

generate-secret:
	python3 -c "import secrets; print(secrets.token_hex(32))"

generate-fernet:
	python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"

backend-shell:
	docker-compose exec backend bash

frontend-shell:
	docker-compose exec frontend sh

test-backend:
	docker-compose exec backend pytest tests/ -v

test-backend-unit:
	docker-compose exec backend pytest tests/unit/ -v

test-backend-integration:
	docker-compose exec backend pytest tests/integration/ -v

build:
	docker-compose build

ps:
	docker-compose ps

flower:
	@echo "Flower UI: http://localhost:5555"
	@open http://localhost:5555 2>/dev/null || xdg-open http://localhost:5555 2>/dev/null || true

api-docs:
	@echo "API Docs: http://localhost:8000/docs"
	@open http://localhost:8000/docs 2>/dev/null || xdg-open http://localhost:8000/docs 2>/dev/null || true
