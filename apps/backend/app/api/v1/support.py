from datetime import datetime, timezone
from fastapi import APIRouter
from sqlalchemy import select

from app.dependencies import CurrentUser, DBSession
from app.schemas.support import SupportRequest, SupportResponse
from app.models.support_request import SupportRequest as SupportRequestModel

router = APIRouter()


@router.post("", response_model=SupportResponse, status_code=201)
async def submit_support(body: SupportRequest, session: DBSession, current_user: CurrentUser = None):
    req = SupportRequestModel(
        user_id=current_user.id if current_user else None,
        email=body.email,
        message=body.message,
        status="open",
        created_at=datetime.now(timezone.utc),
    )
    session.add(req)
    await session.commit()
    await session.refresh(req)
    return req
