import uuid
import hashlib
from datetime import datetime, timezone, timedelta
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

import structlog

from app.models.user import User
from app.models.session import UserSession
from app.core.security import hash_password, verify_password, create_access_token, create_refresh_token
from app.core.exceptions import UnauthorizedError
from app.config import settings

logger = structlog.get_logger(__name__)


class AuthService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def register(self, email: str, password: str) -> User:
        result = await self.session.execute(select(User).where(User.email == email))
        if result.scalar_one_or_none():
            from app.core.exceptions import StratumException
            raise StratumException("Email already registered", code="email_taken", status_code=409)

        user = User(
            email=email,
            hashed_password=hash_password(password),
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        logger.info("user_registered", user_id=str(user.id))
        return user

    async def login(
        self, email: str, password: str, ip_address: str = None, user_agent: str = None
    ) -> tuple[str, str]:
        result = await self.session.execute(select(User).where(User.email == email))
        user = result.scalar_one_or_none()
        if not user or not verify_password(password, user.hashed_password):
            raise UnauthorizedError("Invalid email or password")
        if not user.is_active:
            raise UnauthorizedError("Account is disabled")

        access_token = create_access_token(str(user.id))
        refresh_token = create_refresh_token(str(user.id))

        token_hash = hashlib.sha256(refresh_token.encode()).hexdigest()
        session = UserSession(
            user_id=user.id,
            token_hash=token_hash,
            ip_address=ip_address,
            user_agent=user_agent,
            created_at=datetime.now(timezone.utc),
            expires_at=datetime.now(timezone.utc) + timedelta(minutes=settings.jwt_expire_minutes),
            is_active=True,
        )
        self.session.add(session)
        await self.session.commit()
        logger.info("user_login", user_id=str(user.id))
        return access_token, refresh_token

    async def refresh(self, refresh_token: str) -> str:
        from app.core.security import verify_token, decode_token
        from jose import JWTError
        try:
            payload = decode_token(refresh_token)
            if payload.get("type") != "refresh":
                raise UnauthorizedError("Invalid token type")
            user_id = payload.get("sub")
        except JWTError:
            raise UnauthorizedError("Invalid refresh token")

        token_hash = hashlib.sha256(refresh_token.encode()).hexdigest()
        result = await self.session.execute(
            select(UserSession).where(
                UserSession.token_hash == token_hash,
                UserSession.is_active == True,
                UserSession.expires_at > datetime.now(timezone.utc),
            )
        )
        db_session = result.scalar_one_or_none()
        if not db_session:
            raise UnauthorizedError("Session expired or revoked")

        new_access_token = create_access_token(user_id)
        return new_access_token

    async def logout(self, refresh_token: str) -> None:
        token_hash = hashlib.sha256(refresh_token.encode()).hexdigest()
        result = await self.session.execute(
            select(UserSession).where(UserSession.token_hash == token_hash)
        )
        db_session = result.scalar_one_or_none()
        if db_session:
            db_session.is_active = False
            await self.session.commit()
