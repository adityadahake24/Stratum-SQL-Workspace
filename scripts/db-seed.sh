#!/usr/bin/env bash
set -e

echo "Seeding development data..."
docker-compose exec backend python -c "
import asyncio
from app.db.session import async_session_factory
from app.models.user import User
from app.core.security import hash_password

async def seed():
    async with async_session_factory() as session:
        user = User(email='dev@stratum.io', hashed_password=hash_password('devpassword'), is_active=True, is_verified=True)
        session.add(user)
        await session.commit()
        print(f'Created dev user: dev@stratum.io / devpassword')

asyncio.run(seed())
"
echo "Seed complete."
