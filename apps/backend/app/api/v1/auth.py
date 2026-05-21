from fastapi import APIRouter, Request, Response

from app.dependencies import CurrentUser, DBSession
from app.schemas.auth import RegisterRequest, LoginRequest, TokenResponse, UserResponse
from app.services.auth_service import AuthService

router = APIRouter()


@router.post("/register", response_model=UserResponse, status_code=201)
async def register(body: RegisterRequest, session: DBSession):
    svc = AuthService(session)
    user = await svc.register(body.email, body.password)
    return user


@router.post("/login", response_model=TokenResponse)
async def login(body: LoginRequest, request: Request, response: Response, session: DBSession):
    svc = AuthService(session)
    ip = request.client.host if request.client else None
    ua = request.headers.get("user-agent")
    access_token, refresh_token = await svc.login(body.email, body.password, ip, ua)
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=False,  # True in production
        samesite="lax",
        max_age=7 * 24 * 60 * 60,
        path="/api/v1/auth",
    )
    return TokenResponse(access_token=access_token)


@router.post("/refresh", response_model=TokenResponse)
async def refresh(request: Request, session: DBSession):
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        from app.core.exceptions import UnauthorizedError
        raise UnauthorizedError("No refresh token")
    svc = AuthService(session)
    access_token = await svc.refresh(refresh_token)
    return TokenResponse(access_token=access_token)


@router.post("/logout")
async def logout(request: Request, response: Response, session: DBSession):
    refresh_token = request.cookies.get("refresh_token")
    if refresh_token:
        svc = AuthService(session)
        await svc.logout(refresh_token)
    response.delete_cookie("refresh_token", path="/api/v1/auth")
    return {"message": "Logged out"}


@router.get("/me", response_model=UserResponse)
async def me(current_user: CurrentUser):
    return current_user
