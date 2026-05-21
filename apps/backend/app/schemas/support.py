import uuid
from datetime import datetime
from pydantic import BaseModel, EmailStr


class SupportRequest(BaseModel):
    email: EmailStr
    message: str


class SupportResponse(BaseModel):
    id: uuid.UUID
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}
