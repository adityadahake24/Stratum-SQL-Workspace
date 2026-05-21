import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class ConnectionCreate(BaseModel):
    name: str
    host: str
    port: int = 5432
    database: str
    username: str
    password: str
    ssl_mode: str = "disable"


class ConnectionUpdate(BaseModel):
    name: Optional[str] = None
    host: Optional[str] = None
    port: Optional[int] = None
    database: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None
    ssl_mode: Optional[str] = None


class ConnectionResponse(BaseModel):
    id: uuid.UUID
    name: str
    host: str  # will be decrypted and returned
    port: int
    database: str
    ssl_mode: str
    is_active: bool
    last_used_at: Optional[datetime]
    created_at: datetime

    model_config = {"from_attributes": True}


class ConnectionTestResponse(BaseModel):
    success: bool
    message: str
    latency_ms: Optional[int] = None
    pg_version: Optional[str] = None


class ConnectionTokenRequest(BaseModel):
    connection_id: uuid.UUID


class ConnectionTokenResponse(BaseModel):
    token: str
    expires_at: datetime
